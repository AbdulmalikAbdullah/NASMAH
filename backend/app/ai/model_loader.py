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
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from scipy.spatial import ConvexHull

# ── Configuration ─────────────────────────────────────────────────────────────
UPLOAD_FOLDER = 'uploads'
MODEL_NAME = 'resnet34_lung_segmentation.pth'          # ← NEW model file name
ALLOWED_EXTENSIONS = {'npy', 'png', 'jpg', 'jpeg', 'zip', 'dcm', 'dicom'}

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
    Calculate tumour metrics for a single slice using RECIST-style longest
    diameter measured across the convex-hull of the predicted mask.
    """
    binary_mask = (pred_mask > 0.5).astype(np.uint8)
    tumor_pixels = int(np.sum(binary_mask))
    total_pixels = int(binary_mask.size)

    # ===== Confidence =====
    if tumor_pixels > 0:
        try:
            confidence_rate = float(np.mean(confidence[binary_mask > 0]))
        except Exception:
            confidence_rate = float(np.mean(confidence))
    else:
        confidence_rate = 0.0

    pixel_spacing = 0.5  # mm

    # ===== RECIST Longest Diameter (convex-hull based) =====
    def _recist_longest(mask_2d, spacing_mm=0.5):
        coords = np.argwhere(mask_2d > 0)
        if len(coords) < 2:
            return 0.0, None, None, 0

        try:
            pts = coords[ConvexHull(coords).vertices]
        except Exception:
            pts = coords

        best_d = 0.0
        pa, pb = pts[0], pts[1]
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = float(np.linalg.norm(pts[i] - pts[j]))
                if d > best_d:
                    best_d, pa, pb = d, pts[i], pts[j]

        return best_d * spacing_mm, tuple(int(x) for x in pa), tuple(int(x) for x in pb), int(mask_2d.sum())

    diameter_mm, point_a, point_b, tumor_area_px = _recist_longest(binary_mask, pixel_spacing)

    # ===== Stage Classification Based on DIAMETER =====
    if diameter_mm <= 0:
        stage_num, stage_label = None, 'Unknown'
    elif diameter_mm < 10:
        stage_num, stage_label = 0, 'Stage 0 (T < 10 mm)'
    elif diameter_mm < 40:
        stage_num, stage_label = 1, 'Stage I (10–39 mm)'
    elif diameter_mm < 70:
        stage_num, stage_label = 2, 'Stage II (40–69 mm)'
    else:
        stage_num, stage_label = 3, 'Stage III (T ≥ 70 mm)'

    return {
        'tumor_pixels': tumor_pixels,
        'total_pixels': total_pixels,
        'has_tumor': bool(tumor_pixels > 0),
        'confidence_rate': confidence_rate,
        'tumor_size_mm': round(diameter_mm, 2),
        'tumor_diameter_cm': round(diameter_mm / 10, 2),
        'tumor_stage': stage_num,
        'tumor_stage_label': stage_label,
        'tumor_area_px': tumor_area_px,
        'recist_point_a': point_a,
        'recist_point_b': point_b,
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
        axes[idx, 0].set_title(f"Slice {sd['slice_index']}\n{sd['filename']}", fontsize=12)
        axes[idx, 0].axis('off')

        axes[idx, 1].imshow(img, cmap='bone')
        axes[idx, 1].imshow(np.ma.masked_where(pred_mask == 0, pred_mask), alpha=0.5, cmap='autumn')
        # Overlay RECIST measurement if available
        recist_pa = metrics.get('recist_point_a')
        recist_pb = metrics.get('recist_point_b')
        meas_text = f"Tumour: {metrics['tumor_pixels']} px\n{metrics['tumor_size_mm']:.1f} mm"
        axes[idx, 1].set_title(meas_text, fontsize=12)
        if recist_pa and recist_pb:
            # plot line and endpoints (note: points are (y,x))
            axes[idx, 1].plot([recist_pa[1], recist_pb[1]], [recist_pa[0], recist_pb[0]],
                              color='cyan', linewidth=2.5)
            for pt, lbl in [(recist_pa, 'A'), (recist_pb, 'B')]:
                axes[idx, 1].scatter(pt[1], pt[0], s=60, color='#ffeb3b', edgecolors='white', linewidths=0.8)
                axes[idx, 1].text(pt[1] + 3, pt[0] - 3, lbl, color='#ffeb3b', fontsize=12, fontweight='bold')
            # Zoom into the tumour region so A/B are clear
            try:
                rows, cols = np.where(pred_mask > 0)
                m = 20
                x0 = max(cols.min() - m, 0)
                x1 = min(cols.max() + m, pred_mask.shape[1])
                y0 = min(rows.max() + m, pred_mask.shape[0])
                y1 = max(rows.min() - m, 0)
                axes[idx, 1].set_xlim(x0, x1)
                axes[idx, 1].set_ylim(y0, y1)
            except Exception:
                pass
        axes[idx, 1].axis('off')

        im = axes[idx, 2].imshow(conf, cmap='jet')
        axes[idx, 2].set_title(f"Confidence: {metrics['confidence_rate']:.2%}", fontsize=12)
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