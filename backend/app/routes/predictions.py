from flask import Blueprint, request, jsonify
import os
import shutil
from app.ai.model_loader import (
    model,
    device,
    inference_single_slice,
    load_image_file,
    calculate_metrics_for_slice,
    process_multiple_slices,
    extract_zip,
    create_batch_visualization,
)

predictions_bp = Blueprint("predictions", __name__)
bp = predictions_bp

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"npy", "png", "jpg", "jpeg", "zip"}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@predictions_bp.route("/api/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Handle ZIP batch uploads
    if filename.lower().endswith('.zip'):
        tmpdir = None
        try:
            tmpdir = os.path.join(UPLOAD_FOLDER, f"extracted_{os.path.splitext(filename)[0]}")
            os.makedirs(tmpdir, exist_ok=True)
            slice_files = extract_zip(filepath, tmpdir)

            if not slice_files:
                return jsonify({"error": "No .npy files found inside zip"}), 400

            top_slices = process_multiple_slices(slice_files, device)
            visualization = create_batch_visualization(top_slices)

            # Build summary and top results
            total_slices = len(slice_files)
            tumor_slices = sum(1 for s in top_slices)
            max_tumor_size = max((s['metrics']['tumor_size_mm'] for s in top_slices), default=0)
            avg_confidence = float(
                sum((s['metrics']['confidence_rate'] for s in top_slices), 0.0) / (len(top_slices) or 1)
            )

            top_results = []
            for s in top_slices:
                m = s['metrics']
                top_results.append({
                    'slice_index': s['slice_index'],
                    'filename': s['filename'],
                    'tumor_size_mm': m['tumor_size_mm'],
                    'tumor_pixels': m['tumor_pixels'],
                    'confidence_rate': m['confidence_rate'],
                    'tumor_percentage': m['tumor_percentage']
                })

            summary = {
                'total_slices': total_slices,
                'tumor_slices': tumor_slices,
                'max_tumor_size': max_tumor_size,
                'avg_confidence': avg_confidence,
                'top_slice_index': top_results[0]['slice_index'] if top_results else None,
                'top_slice_filename': top_results[0]['filename'] if top_results else None
            }

            return jsonify({
                'success': True,
                'batch_mode': True,
                'summary': summary,
                'top_results': top_results,
                'visualization': visualization
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)
            if tmpdir and os.path.exists(tmpdir):
                try:
                    shutil.rmtree(tmpdir)
                except Exception:
                    pass

    # Single file handling
    try:
        img_array = load_image_file(filepath)
        pred_mask, confidence = inference_single_slice(model, img_array, device)
        metrics = calculate_metrics_for_slice(pred_mask, confidence, img_array.shape)

        # Optionally create visualization for single slice
        # reuse batch visualization for single entry
        visualization = None
        try:
            visualization = create_batch_visualization([
                {
                    'slice_index': 0,
                    'filename': filename,
                    'image': img_array,
                    'pred_mask': pred_mask,
                    'confidence': confidence,
                    'metrics': metrics
                }
            ])
        except Exception:
            visualization = None

        return jsonify({
            "success": True,
            "batch_mode": False,
            "metrics": metrics,
            "visualization": visualization
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
