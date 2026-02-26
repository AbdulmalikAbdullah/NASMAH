from flask import Blueprint, request, jsonify, current_app
import os
import shutil
import tempfile
import base64
import io
import json
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
from app.models import TumorImage, Prediction
from app.extensions import db
from app.utils.decorators import token_required
from app.services.s3_service import get_s3_service

predictions_bp = Blueprint("predictions", __name__)
bp = predictions_bp

# Initialize S3 service
s3_service = get_s3_service()

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
                    'stage': m['tumor_stage'],
                    'stage_label': m['tumor_stage_label']
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


@predictions_bp.route("/api/predictions/predict", methods=["POST"])
@token_required
def predict_from_image_id(current_user):
    """
    Predict cancer stage from an uploaded image using image_id
    Expected JSON body: { "image_id": <int> }
    """
    data = request.get_json()
    
    if not data or 'image_id' not in data:
        return jsonify({"error": "image_id is required"}), 400
    
    image_id = data['image_id']
    
    # Get image from database
    image = TumorImage.query.filter_by(
        image_id=image_id,
        user_id=current_user.user_id
    ).first()
    
    if not image:
        return jsonify({"error": "Image not found"}), 404
    
    if not image.is_valid:
        return jsonify({"error": "Image is not valid for prediction"}), 400
    
    filepath = image.image_path
    
    if not os.path.exists(filepath):
        return jsonify({"error": "Image file not found on server"}), 404
    
    try:
        # Handle ZIP batch uploads
        if filepath.lower().endswith('.zip'):
            tmpdir = None
            try:
                tmpdir = tempfile.mkdtemp(prefix='lung_predict_')
                slice_files = extract_zip(filepath, tmpdir)
                
                if not slice_files:
                    return jsonify({"error": "No valid image files found inside zip"}), 400
                
                top_slices = process_multiple_slices(slice_files, device, top_k=10)
                
                if not top_slices:
                    # No tumors detected
                    prediction = Prediction(
                        user_id=current_user.user_id,
                        image_id=image_id,
                        cancer_stage='0',
                        confidence=0.95,
                        model_name='unet_lung_segmentation'
                    )
                    db.session.add(prediction)
                    db.session.commit()
                    
                    return jsonify({
                        "success": True,
                        "batch_mode": True,
                        "prediction": prediction.to_dict(),
                        "message": "No tumors detected in any slices"
                    })
                
                # Get the slice with the largest tumor
                largest_tumor_slice = top_slices[0]
                metrics = largest_tumor_slice['metrics']
                visualization = create_batch_visualization(top_slices)
                
                # Create prediction record using the worst case (largest tumor)
                cancer_stage = str(metrics.get('tumor_stage', 0))
                confidence = metrics.get('confidence_rate', 0.0)
                
                prediction = Prediction(
                    user_id=current_user.user_id,
                    image_id=image_id,
                    cancer_stage=cancer_stage,
                    confidence=confidence,
                    model_name='unet_lung_segmentation'
                )
                db.session.add(prediction)
                db.session.commit()
                
                # Build detailed response
                total_slices = len(slice_files)
                tumor_slices = len(top_slices)
                
                # Upload visualization to S3
                if visualization and s3_service.is_configured():
                    try:
                        # Decode base64 visualization to bytes
                        viz_bytes = base64.b64decode(visualization)
                        viz_file = io.BytesIO(viz_bytes)
                        
                        # Generate descriptive filename
                        original_name = os.path.splitext(os.path.basename(filepath))[0]
                        viz_filename = f"Analysis_Result_{original_name}.png"
                        
                        # Upload to S3
                        s3_result = s3_service.upload_file_to_s3(
                            viz_file,
                            current_user.user_id,
                            viz_filename,
                            content_type='image/png'
                        )
                        
                        # Update image record with S3 info
                        if s3_result['success']:
                            image.s3_url = s3_result['s3_url']
                            image.s3_key = s3_result['s3_key']
                            image.s3_bucket = s3_result['s3_bucket']
                            db.session.commit()
                            current_app.logger.info(f"Visualization uploaded to S3: {s3_result['s3_url']}")
                        else:
                            current_app.logger.warning(f"S3 upload failed: {s3_result.get('error')}, visualization not persisted")
                    except Exception as e:
                        current_app.logger.error(f"Error uploading visualization to S3: {str(e)}")
                
                top_results = []
                for s in top_slices:
                    m = s['metrics']
                    top_results.append({
                        'slice_index': s['slice_index'],
                        'filename': s['filename'],
                        'tumor_size_mm': m['tumor_size_mm'],
                        'tumor_pixels': m['tumor_pixels'],
                        'confidence_rate': m['confidence_rate'],
                        'stage': m['tumor_stage'],
                        'stage_label': m['tumor_stage_label']
                    })
                
                return jsonify({
                    "success": True,
                    "batch_mode": True,
                    "prediction": prediction.to_dict(),
                    "summary": {
                        'total_slices': total_slices,
                        'tumor_slices': tumor_slices,
                        'max_tumor_size': metrics['tumor_size_mm'],
                        'avg_confidence': confidence,
                    },
                    'top_results': top_results,
                    'visualization': visualization
                })
                
            finally:
                # Cleanup temp directory
                if tmpdir and os.path.exists(tmpdir):
                    try:
                        shutil.rmtree(tmpdir)
                    except Exception:
                        pass
        
        # Single file handling (npy, png, jpg, jpeg)
        img_array = load_image_file(filepath)
        pred_mask, confidence_map = inference_single_slice(model, img_array, device)
        metrics = calculate_metrics_for_slice(pred_mask, confidence_map, img_array.shape)
        
        # Create visualization
        visualization = None
        try:
            visualization = create_batch_visualization([
                {
                    'slice_index': 0,
                    'filename': os.path.basename(filepath),
                    'image': img_array,
                    'pred_mask': pred_mask,
                    'confidence': confidence_map,
                    'metrics': metrics
                }
            ])
        except Exception as e:
            print(f"Warning: Could not create visualization: {e}")
        
        # Save prediction to database
        cancer_stage = str(metrics.get('tumor_stage', 0))
        confidence = metrics.get('confidence_rate', 0.0)
        
        prediction = Prediction(
            user_id=current_user.user_id,
            image_id=image_id,
            cancer_stage=cancer_stage,
            confidence=confidence,
            model_name='unet_lung_segmentation'
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "batch_mode": False,
            "prediction": prediction.to_dict(),
            "metrics": metrics,
            "visualization": visualization
        })
        
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@predictions_bp.route("/api/predictions/history", methods=["GET"])
@token_required
def get_prediction_history(current_user):
    """Get all predictions for the current user"""
    try:
        # Query predictions for current user with image information
        predictions = Prediction.query.filter_by(user_id=current_user.user_id).order_by(Prediction.created_at.desc()).all()
        
        results = []
        for pred in predictions:
            # Get associated image
            image = TumorImage.query.filter_by(image_id=pred.image_id).first()
            
            # Generate presigned URL if S3 key exists
            image_url = None
            if image and image.s3_key:
                image_url = s3_service.generate_presigned_url(image.s3_key, expiration=3600)
                if not image_url:
                    current_app.logger.warning(f"Failed to generate presigned URL for image {image.image_id}")
            elif image and image.image_path:
                # Fallback to local path for old records
                image_url = image.image_path
            
            # Map cancer stage to prediction label
            stage_labels = {
                '0': 'Negative',
                '1': 'Stage I',
                '2': 'Stage II',
                '3': 'Stage III',
                '4': 'Stage IV'
            }
            
            results.append({
                'prediction_id': pred.prediction_id,
                'image_id': pred.image_id,
                'image_name': os.path.basename(image.image_path) if image and image.image_path else 'Unknown',
                's3_url': image_url,
                's3_key': image.s3_key if image else None,
                'timestamp': pred.created_at.isoformat() if pred.created_at else None,
                'prediction_label': stage_labels.get(pred.cancer_stage, 'Unknown'),
                'cancer_stage': pred.cancer_stage,
                'confidence': round(pred.confidence * 100, 2),
                'model_name': pred.model_name
            })
        
        return jsonify({
            'message': 'Prediction history retrieved successfully',
            'count': len(results),
            'predictions': results
        }), 200
        
    except Exception as e:
        print(f"Error retrieving prediction history: {str(e)}")
        return jsonify({'error': f'Failed to retrieve history: {str(e)}'}), 500

