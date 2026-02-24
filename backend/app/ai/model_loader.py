# import os
# import io
# import base64
# import numpy as np
# import torch
# import torch.nn as nn
# from flask import request, jsonify, render_template
# from PIL import Image
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import zipfile
# import tempfile
# import shutil


# # Configuration
# UPLOAD_FOLDER = 'uploads'
# MODEL_NAME = 'unet_lung_segmentation.pth'
# ALLOWED_EXTENSIONS = {'npy', 'png', 'jpg', 'jpeg', 'zip'}

# # Try to locate the model file by searching upward from this file and the CWD
# MODEL_PATH = None
# search_locations = []
# cwd = os.path.abspath(os.getcwd())
# search_locations.append(cwd)
# base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# for _ in range(5):
#     candidate = os.path.join(base, MODEL_NAME)
#     search_locations.append(base)
#     if os.path.exists(candidate):
#         MODEL_PATH = candidate
#         break
#     base = os.path.dirname(base)

# # Also check the current package directory
# pkg_candidate = os.path.join(os.path.dirname(__file__), MODEL_NAME)
# if MODEL_PATH is None and os.path.exists(pkg_candidate):
#     MODEL_PATH = pkg_candidate


# # Ensure upload folder exists (Flask app will configure MAX_CONTENT_LENGTH)
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Model Definition
# class MiniUNet(nn.Module):
#     def __init__(self):
#         super().__init__()
        
#         self.enc1 = nn.Sequential(
#             nn.Conv2d(1, 16, 3, padding=1),
#             nn.ReLU()
#         )
#         self.pool = nn.MaxPool2d(2)
        
#         self.enc2 = nn.Sequential(
#             nn.Conv2d(16, 32, 3, padding=1),
#             nn.ReLU()
#         )
        
#         self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False)
        
#         self.dec1 = nn.Sequential(
#             nn.Conv2d(32 + 16, 16, 3, padding=1),
#             nn.ReLU()
#         )
        
#         self.out = nn.Conv2d(16, 1, 1)
    
#     def forward(self, x):
#         x1 = self.enc1(x)
#         x2 = self.enc2(self.pool(x1))
#         x3 = self.up(x2)
#         x4 = torch.cat([x3, x1], dim=1)
#         return self.out(self.dec1(x4))

# # Load model
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = MiniUNet().to(device)

# if MODEL_PATH and os.path.exists(MODEL_PATH):
#     try:
#         model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
#         model.eval()
#         print(f"✓ Model loaded successfully from {MODEL_PATH} on {device}")
#     except Exception as e:
#         print(f"⚠ Warning: Could not load model from {MODEL_PATH}: {e}")
# else:
#     print(f"⚠ Warning: Model file '{MODEL_NAME}' not found. Searched locations: {search_locations}. Continuing without pretrained weights.")

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def preprocess_image(img_array):
#     """Normalize image to [0, 1] range"""
#     img_norm = (img_array - img_array.min()) / (img_array.max() - img_array.min() + 1e-8)
#     return img_norm

# def load_image_file(filepath):
#     """Load image from either .npy or standard image formats"""
#     ext = filepath.rsplit('.', 1)[1].lower()
    
#     if ext == 'npy':
#         img = np.load(filepath).astype(np.float32)
#     else:
#         pil_img = Image.open(filepath).convert('L')
#         img = np.array(pil_img).astype(np.float32)
    
#     return img

# def inference_single_slice(model, img_array, device):
#     """Run inference on a single CT slice"""
#     model.eval()
    
#     img_norm = preprocess_image(img_array)
#     img_tensor = torch.tensor(img_norm).unsqueeze(0).unsqueeze(0).to(device)
    
#     with torch.no_grad():
#         logits = model(img_tensor)
#         pred = torch.sigmoid(logits)
#         pred_mask = (pred > 0.5).float().cpu().numpy()[0, 0]
#         confidence = pred.cpu().numpy()[0, 0]
    
#     return pred_mask, confidence

# def calculate_metrics_for_slice(pred_mask, confidence, img_shape):
#     """Calculate comprehensive metrics for a single slice.

#     This now computes an approximate tumor diameter (assuming the tumor
#     area is circular) and assigns a TNM-style stage (0-3) based on the
#     diameter thresholds you provided. Stage IV cannot be determined
#     from a single-slice area estimate and therefore is not assigned
#     automatically.
#     """
#     binary_mask = (pred_mask > 0.5).astype(np.float32)
#     tumor_pixels = int(np.sum(binary_mask))
#     total_pixels = int(binary_mask.size)

#     # Confidence rate
#     if tumor_pixels > 0:
#         try:
#             confidence_rate = float(np.mean(confidence[binary_mask > 0]))
#         except Exception:
#             confidence_rate = float(np.mean(confidence))
#     else:
#         confidence_rate = 0.0

#     # Tumor area in mm² (pixel_spacing default 0.5 mm)
#     pixel_spacing = 0.5
#     tumor_area_mm2 = float(tumor_pixels * (pixel_spacing ** 2))


#     # Stage mapping (based on diameter thresholds provided)
#     # Stage 0: T < 10 mm
#     # Stage I: 10 mm ≤ T < 40 mm
#     # Stage II: 40 mm ≤ T < 70 mm
#     # Stage III: T ≥ 70 mm
#     if tumor_area_mm2 <= 0:
#         stage_num = None
#         stage_label = 'Unknown'
#     elif tumor_area_mm2 < 10.0:
#         stage_num = 0
#         stage_label = 'Stage 0 (T < 10 mm)'
#     elif tumor_area_mm2 < 40.0:
#         stage_num = 1
#         stage_label = 'Stage I (10–39 mm)'
#     elif tumor_area_mm2 < 70.0:
#         stage_num = 2
#         stage_label = 'Stage II (40–69 mm)'
#     else:
#         stage_num = 3
#         stage_label = 'Stage III (T ≥ 70 mm)'

#     return {
#         'tumor_pixels': tumor_pixels,
#         'total_pixels': total_pixels,
#         'has_tumor': bool(tumor_pixels > 0),
#         'confidence_rate': float(confidence_rate),
#         'tumor_size_mm': round(tumor_area_mm2, 2),
#         'tumor_stage': stage_num,
#         'tumor_stage_label': stage_label
#     }

# def process_multiple_slices(slice_files_dict, device, top_k=10):
#     """Process multiple CT slices and return top K results"""
#     all_results = []
    
#     print(f"\n{'='*50}")
#     print(f"Processing {len(slice_files_dict)} slices...")
#     print(f"{'='*50}")
    
#     for idx, (filename, filepath) in enumerate(slice_files_dict.items()):
#         try:
#             img_array = load_image_file(filepath)
#             pred_mask, confidence = inference_single_slice(model, img_array, device)
#             metrics = calculate_metrics_for_slice(pred_mask, confidence, img_array.shape)
            
#             result = {
#                 'slice_index': idx,
#                 'filename': filename,
#                 'image': img_array,
#                 'pred_mask': pred_mask,
#                 'confidence': confidence,
#                 'metrics': metrics
#             }
            
#             all_results.append(result)
            
#             if (idx + 1) % 50 == 0:
#                 print(f"  Processed {idx + 1}/{len(slice_files_dict)} slices...")
                
#         except Exception as e:
#             print(f"  Error processing {filename}: {e}")
#             continue
    
#     # Filter slices with tumors
#     tumor_slices = [r for r in all_results if r['metrics']['has_tumor']]
    
#     # Sort by tumor size
#     tumor_slices.sort(key=lambda x: x['metrics']['tumor_pixels'], reverse=True)
    
#     # Get top K
#     top_slices = tumor_slices[:top_k]
    
#     print(f"✓ Found {len(tumor_slices)} slices with tumors")
#     print(f"✓ Returning top {len(top_slices)} results")
    
#     return top_slices

# def create_batch_visualization(top_slices):
#     """Create a grid visualization of top slices"""
#     n_slices = len(top_slices)
    
#     if n_slices == 0:
#         return None
    
#     n_rows = min(n_slices, 10)
#     fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5 * n_rows))
    
#     if n_rows == 1:
#         axes = axes.reshape(1, -1)
    
#     for idx, slice_data in enumerate(top_slices[:10]):
#         img = slice_data['image']
#         pred_mask = slice_data['pred_mask']
#         confidence = slice_data['confidence']
#         metrics = slice_data['metrics']
        
#         # Original
#         axes[idx, 0].imshow(img, cmap='bone')
#         axes[idx, 0].set_title(f"Slice {slice_data['slice_index']}\n{slice_data['filename']}", fontsize=8)
#         axes[idx, 0].axis('off')
        
#         # Overlay
#         axes[idx, 1].imshow(img, cmap='bone')
#         axes[idx, 1].imshow(np.ma.masked_where(pred_mask == 0, pred_mask), 
#                            alpha=0.5, cmap='autumn')
#         axes[idx, 1].set_title(f"Tumor: {metrics['tumor_pixels']} px\n{metrics['tumor_size_mm']:.1f} mm²", fontsize=8)
#         axes[idx, 1].axis('off')
        
#         # Confidence
#         im = axes[idx, 2].imshow(confidence, cmap='jet')
#         axes[idx, 2].set_title(f"Confidence: {metrics['confidence_rate']:.2%}", fontsize=8)
#         axes[idx, 2].axis('off')
#         plt.colorbar(im, ax=axes[idx, 2], fraction=0.046, pad=0.04)
    
#     plt.tight_layout()
    
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
#     buf.seek(0)
#     img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#     plt.close(fig)
    
#     return img_base64

# def extract_zip(zip_path, extract_to):
#     """Extract zip file and return dict of .npy files"""
#     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#         zip_ref.extractall(extract_to)
    
#     npy_files = {}
#     for root, dirs, files in os.walk(extract_to):
#         for file in files:
#             if file.endswith('.npy'):
#                 filepath = os.path.join(root, file)
#                 npy_files[file] = filepath
    
#     # Sort by filename
#     try:
#         npy_files = dict(sorted(npy_files.items(), key=lambda x: int(x[0].split('.')[0])))
#     except:
#         npy_files = dict(sorted(npy_files.items()))
    
#     return npy_files


import os
import io
import base64
import numpy as np
import torch
from flask import request, jsonify
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import zipfile
import tempfile
import shutil

import segmentation_models_pytorch as smp

# ── Configuration ─────────────────────────────────────────────────────────────
UPLOAD_FOLDER = 'uploads'
MODEL_NAME = 'resnet34_lung_segmentation.pth'          # ← NEW model file name
ALLOWED_EXTENSIONS = {'npy', 'png', 'jpg', 'jpeg', 'zip'}

# ── Locate the model file (searches upward from this file and CWD) ────────────
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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Model & Device ────────────────────────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = smp.Unet(
    encoder_name    = "resnet34",
    encoder_weights = None,   # weights loaded from .pth, not downloaded
    in_channels     = 1,      # grayscale CT slices
    classes         = 1,      # binary tumour mask
    activation      = None,   # raw logits — sigmoid applied at inference
).to(device)

if MODEL_PATH and os.path.exists(MODEL_PATH):
    try:
        state = torch.load(MODEL_PATH, map_location=device)
        # Support both plain state_dict and checkpoint dicts
        if isinstance(state, dict) and "model" in state:
            state = state["model"]
        model.load_state_dict(state)
        model.eval()
        print(f"✓ Model loaded successfully from {MODEL_PATH} on {device}")
    except Exception as e:
        print(f"⚠ Warning: Could not load model weights from {MODEL_PATH}: {e}")
else:
    print(
        f"⚠ Warning: Model file '{MODEL_NAME}' not found. "
        f"Searched: {search_locations}. Running without pretrained weights."
    )

# ── Helper utilities ──────────────────────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(img_array):
    """Normalize image to [0, 1]."""
    return (img_array - img_array.min()) / (img_array.max() - img_array.min() + 1e-8)


def load_image_file(filepath):
    """Load image from .npy or standard image formats → float32 numpy array."""
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'npy':
        img = np.load(filepath).astype(np.float32)
    else:
        pil_img = Image.open(filepath).convert('L')
        img = np.array(pil_img).astype(np.float32)
    return img


def inference_single_slice(mdl, img_array, dev):
    """
    Run inference on a single 2-D CT slice.

    The ResNet34-UNet accepts input of shape (1, 1, H, W).
    Minimum spatial size is 32×32 — images smaller than this are padded
    and then cropped back to the original size after inference.
    """
    mdl.eval()
    img_norm   = preprocess_image(img_array)
    h, w       = img_norm.shape[:2]

    # Pad to at least 32×32 (ResNet encoder requirement)
    pad_h = max(0, 32 - h)
    pad_w = max(0, 32 - w)
    if pad_h or pad_w:
        img_norm = np.pad(img_norm, ((0, pad_h), (0, pad_w)), mode='reflect')

    img_tensor = torch.tensor(img_norm).unsqueeze(0).unsqueeze(0).to(dev)

    with torch.no_grad():
        logits     = mdl(img_tensor)
        pred       = torch.sigmoid(logits)
        pred_mask  = (pred > 0.5).float().cpu().numpy()[0, 0]
        confidence = pred.cpu().numpy()[0, 0]

    # Crop back to original size if we padded
    pred_mask  = pred_mask[:h, :w]
    confidence = confidence[:h, :w]

    return pred_mask, confidence


def calculate_metrics_for_slice(pred_mask, confidence, img_shape):
    """
    Calculate tumour metrics for a single slice and assign a TNM-style stage.

    Stage mapping (diameter thresholds):
        Stage 0  : no tumour detected
        Stage I  : area < 10 mm²   (T < 10 mm)
        Stage II : 10 ≤ area < 40  (10–39 mm)
        Stage III: 40 ≤ area < 70  (40–69 mm)
        Stage IV : area ≥ 70       (≥ 70 mm)
    """
    binary_mask   = (pred_mask > 0.5).astype(np.float32)
    tumor_pixels  = int(np.sum(binary_mask))
    total_pixels  = int(binary_mask.size)

    if tumor_pixels > 0:
        try:
            confidence_rate = float(np.mean(confidence[binary_mask > 0]))
        except Exception:
            confidence_rate = float(np.mean(confidence))
    else:
        confidence_rate = 0.0

    pixel_spacing   = 0.5  # mm
    tumor_area_mm2  = float(tumor_pixels * (pixel_spacing ** 2))

    if tumor_area_mm2 <= 0:
        stage_num, stage_label = None, 'Unknown'
    elif tumor_area_mm2 < 10.0:
        stage_num, stage_label = 0, 'Stage 0 (T < 10 mm)'
    elif tumor_area_mm2 < 40.0:
        stage_num, stage_label = 1, 'Stage I (10–39 mm)'
    elif tumor_area_mm2 < 70.0:
        stage_num, stage_label = 2, 'Stage II (40–69 mm)'
    else:
        stage_num, stage_label = 3, 'Stage III (T ≥ 70 mm)'

    return {
        'tumor_pixels'     : tumor_pixels,
        'total_pixels'     : total_pixels,
        'has_tumor'        : bool(tumor_pixels > 0),
        'confidence_rate'  : float(confidence_rate),
        'tumor_size_mm'    : round(tumor_area_mm2, 2),
        'tumor_stage'      : stage_num,
        'tumor_stage_label': stage_label,
    }


def process_multiple_slices(slice_files_dict, dev, top_k=10):
    """Process multiple CT slices and return the top-K most affected slices."""
    all_results = []

    print(f"\n{'='*50}")
    print(f"Processing {len(slice_files_dict)} slices…")
    print(f"{'='*50}")

    for idx, (filename, filepath) in enumerate(slice_files_dict.items()):
        try:
            img_array        = load_image_file(filepath)
            pred_mask, conf  = inference_single_slice(model, img_array, dev)
            metrics          = calculate_metrics_for_slice(pred_mask, conf, img_array.shape)

            all_results.append({
                'slice_index': idx,
                'filename'   : filename,
                'image'      : img_array,
                'pred_mask'  : pred_mask,
                'confidence' : conf,
                'metrics'    : metrics,
            })

            if (idx + 1) % 50 == 0:
                print(f"  Processed {idx + 1}/{len(slice_files_dict)} slices…")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            continue

    tumor_slices = [r for r in all_results if r['metrics']['has_tumor']]
    tumor_slices.sort(key=lambda x: x['metrics']['tumor_pixels'], reverse=True)
    top_slices = tumor_slices[:top_k]

    print(f"✓ Found {len(tumor_slices)} slices with tumours")
    print(f"✓ Returning top {len(top_slices)} results")
    return top_slices


def create_batch_visualization(top_slices):
    """Create a grid visualisation of top slices (Original | Overlay | Confidence)."""
    n_slices = len(top_slices)
    if n_slices == 0:
        return None

    n_rows = min(n_slices, 10)
    fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    for idx, sd in enumerate(top_slices[:10]):
        img       = sd['image']
        pred_mask = sd['pred_mask']
        conf      = sd['confidence']
        metrics   = sd['metrics']

        axes[idx, 0].imshow(img, cmap='bone')
        axes[idx, 0].set_title(f"Slice {sd['slice_index']}\n{sd['filename']}", fontsize=8)
        axes[idx, 0].axis('off')

        axes[idx, 1].imshow(img, cmap='bone')
        axes[idx, 1].imshow(np.ma.masked_where(pred_mask == 0, pred_mask), alpha=0.5, cmap='autumn')
        axes[idx, 1].set_title(
            f"Tumour: {metrics['tumor_pixels']} px\n{metrics['tumor_size_mm']:.1f} mm²", fontsize=8)
        axes[idx, 1].axis('off')

        im = axes[idx, 2].imshow(conf, cmap='jet')
        axes[idx, 2].set_title(f"Confidence: {metrics['confidence_rate']:.2%}", fontsize=8)
        axes[idx, 2].axis('off')
        plt.colorbar(im, ax=axes[idx, 2], fraction=0.046, pad=0.04)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_b64


def extract_zip(zip_path, extract_to):
    """Extract a zip file and return a sorted dict of {filename: filepath} for .npy files."""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)

    npy_files = {}
    for root, _, files in os.walk(extract_to):
        for f in files:
            if f.endswith('.npy'):
                npy_files[f] = os.path.join(root, f)

    try:
        npy_files = dict(sorted(npy_files.items(), key=lambda x: int(x[0].split('.')[0])))
    except Exception:
        npy_files = dict(sorted(npy_files.items()))

    return npy_files