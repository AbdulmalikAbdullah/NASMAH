import os
import io
import base64
import numpy as np
import torch
import torch.nn as nn
from flask import request, jsonify, render_template
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import zipfile
import tempfile
import shutil


# Configuration
UPLOAD_FOLDER = 'uploads'
MODEL_NAME = 'unet_lung_segmentation.pth'
ALLOWED_EXTENSIONS = {'npy', 'png', 'jpg', 'jpeg', 'zip'}

# Try to locate the model file by searching upward from this file and the CWD
MODEL_PATH = None
search_locations = []
cwd = os.path.abspath(os.getcwd())
search_locations.append(cwd)
base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for _ in range(5):
    candidate = os.path.join(base, MODEL_NAME)
    search_locations.append(base)
    if os.path.exists(candidate):
        MODEL_PATH = candidate
        break
    base = os.path.dirname(base)

# Also check the current package directory
pkg_candidate = os.path.join(os.path.dirname(__file__), MODEL_NAME)
if MODEL_PATH is None and os.path.exists(pkg_candidate):
    MODEL_PATH = pkg_candidate


# Ensure upload folder exists (Flask app will configure MAX_CONTENT_LENGTH)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model Definition
class MiniUNet(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.enc1 = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU()
        )
        self.pool = nn.MaxPool2d(2)
        
        self.enc2 = nn.Sequential(
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU()
        )
        
        self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False)
        
        self.dec1 = nn.Sequential(
            nn.Conv2d(32 + 16, 16, 3, padding=1),
            nn.ReLU()
        )
        
        self.out = nn.Conv2d(16, 1, 1)
    
    def forward(self, x):
        x1 = self.enc1(x)
        x2 = self.enc2(self.pool(x1))
        x3 = self.up(x2)
        x4 = torch.cat([x3, x1], dim=1)
        return self.out(self.dec1(x4))

# Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MiniUNet().to(device)

if MODEL_PATH and os.path.exists(MODEL_PATH):
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.eval()
        print(f"✓ Model loaded successfully from {MODEL_PATH} on {device}")
    except Exception as e:
        print(f"⚠ Warning: Could not load model from {MODEL_PATH}: {e}")
else:
    print(f"⚠ Warning: Model file '{MODEL_NAME}' not found. Searched locations: {search_locations}. Continuing without pretrained weights.")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(img_array):
    """Normalize image to [0, 1] range"""
    img_norm = (img_array - img_array.min()) / (img_array.max() - img_array.min() + 1e-8)
    return img_norm

def load_image_file(filepath):
    """Load image from either .npy or standard image formats"""
    ext = filepath.rsplit('.', 1)[1].lower()
    
    if ext == 'npy':
        img = np.load(filepath).astype(np.float32)
    else:
        pil_img = Image.open(filepath).convert('L')
        img = np.array(pil_img).astype(np.float32)
    
    return img

def inference_single_slice(model, img_array, device):
    """Run inference on a single CT slice"""
    model.eval()
    
    img_norm = preprocess_image(img_array)
    img_tensor = torch.tensor(img_norm).unsqueeze(0).unsqueeze(0).to(device)
    
    with torch.no_grad():
        logits = model(img_tensor)
        pred = torch.sigmoid(logits)
        pred_mask = (pred > 0.5).float().cpu().numpy()[0, 0]
        confidence = pred.cpu().numpy()[0, 0]
    
    return pred_mask, confidence

def calculate_metrics_for_slice(pred_mask, confidence, img_shape):
    """Calculate comprehensive metrics for a single slice"""
    binary_mask = (pred_mask > 0.5).astype(np.float32)
    tumor_pixels = np.sum(binary_mask)
    total_pixels = binary_mask.size
    tumor_percentage = (tumor_pixels / total_pixels) * 100
    
    # Confidence rate
    if tumor_pixels > 0:
        confidence_rate = float(np.mean(confidence[binary_mask > 0]))
    else:
        confidence_rate = 0.0
    
    # Tumor size in mm²
    pixel_spacing = 0.5
    tumor_size_mm = float(tumor_pixels * (pixel_spacing ** 2))
    
    return {
        'tumor_pixels': int(tumor_pixels),
        'total_pixels': int(total_pixels),
        'tumor_percentage': float(tumor_percentage),
        'has_tumor': bool(tumor_pixels > 0),
        'confidence_rate': float(confidence_rate),
        'tumor_size_mm': round(tumor_size_mm, 2)
    }

def process_multiple_slices(slice_files_dict, device, top_k=10):
    """Process multiple CT slices and return top K results"""
    all_results = []
    
    print(f"\n{'='*50}")
    print(f"Processing {len(slice_files_dict)} slices...")
    print(f"{'='*50}")
    
    for idx, (filename, filepath) in enumerate(slice_files_dict.items()):
        try:
            img_array = load_image_file(filepath)
            pred_mask, confidence = inference_single_slice(model, img_array, device)
            metrics = calculate_metrics_for_slice(pred_mask, confidence, img_array.shape)
            
            result = {
                'slice_index': idx,
                'filename': filename,
                'image': img_array,
                'pred_mask': pred_mask,
                'confidence': confidence,
                'metrics': metrics
            }
            
            all_results.append(result)
            
            if (idx + 1) % 50 == 0:
                print(f"  Processed {idx + 1}/{len(slice_files_dict)} slices...")
                
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            continue
    
    # Filter slices with tumors
    tumor_slices = [r for r in all_results if r['metrics']['has_tumor']]
    
    # Sort by tumor size
    tumor_slices.sort(key=lambda x: x['metrics']['tumor_pixels'], reverse=True)
    
    # Get top K
    top_slices = tumor_slices[:top_k]
    
    print(f"✓ Found {len(tumor_slices)} slices with tumors")
    print(f"✓ Returning top {len(top_slices)} results")
    
    return top_slices

def create_batch_visualization(top_slices):
    """Create a grid visualization of top slices"""
    n_slices = len(top_slices)
    
    if n_slices == 0:
        return None
    
    n_rows = min(n_slices, 10)
    fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5 * n_rows))
    
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    for idx, slice_data in enumerate(top_slices[:10]):
        img = slice_data['image']
        pred_mask = slice_data['pred_mask']
        confidence = slice_data['confidence']
        metrics = slice_data['metrics']
        
        # Original
        axes[idx, 0].imshow(img, cmap='bone')
        axes[idx, 0].set_title(f"Slice {slice_data['slice_index']}\n{slice_data['filename']}", fontsize=8)
        axes[idx, 0].axis('off')
        
        # Overlay
        axes[idx, 1].imshow(img, cmap='bone')
        axes[idx, 1].imshow(np.ma.masked_where(pred_mask == 0, pred_mask), 
                           alpha=0.5, cmap='autumn')
        axes[idx, 1].set_title(f"Tumor: {metrics['tumor_pixels']} px\n{metrics['tumor_size_mm']:.1f} mm²", fontsize=8)
        axes[idx, 1].axis('off')
        
        # Confidence
        im = axes[idx, 2].imshow(confidence, cmap='jet')
        axes[idx, 2].set_title(f"Confidence: {metrics['confidence_rate']:.2%}", fontsize=8)
        axes[idx, 2].axis('off')
        plt.colorbar(im, ax=axes[idx, 2], fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    
    return img_base64

def extract_zip(zip_path, extract_to):
    """Extract zip file and return dict of .npy files"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    npy_files = {}
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.endswith('.npy'):
                filepath = os.path.join(root, file)
                npy_files[file] = filepath
    
    # Sort by filename
    try:
        npy_files = dict(sorted(npy_files.items(), key=lambda x: int(x[0].split('.')[0])))
    except:
        npy_files = dict(sorted(npy_files.items()))
    
    return npy_files