import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/common/DashboardLayout';
import FileUpload from '../components/dashboard/FileUpload';
import PredictionResult from '../components/dashboard/PredictionResult';
import LoadingSpinner from '../components/common/LoadingSpinner';
import axiosInstance from '../api/axiosConfig';
import useApi from '../hooks/useApi';
import toast from 'react-hot-toast';

/**
 * Upload Scan Page
 * Dedicated page for uploading and analyzing medical images
 */
const UploadScan = () => {
  const navigate = useNavigate();
  const [prediction, setPrediction] = useState(null);
  const { loading, error, execute, setError } = useApi();

  const handleFileUpload = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      await execute(async () => {
        // Upload image
        const uploadResponse = await axiosInstance.post('/api/images/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        const imageId = uploadResponse.data.image_id;
        toast.success('Image uploaded successfully!');

        // Request prediction
        const predictionResponse = await axiosInstance.post('/api/predictions/predict', {
          image_id: imageId,
        });

        const { prediction, metrics, visualization, batch_mode, summary, top_results } = predictionResponse.data;
        
        setPrediction({
          ...prediction,
          metrics,
          visualization,
          batch_mode,
          summary,
          top_results,
          image_id: imageId,
          fileName: file.name,
          timestamp: new Date().toISOString(),
        });

        toast.success('Analysis complete!');
        return prediction;
      });
    } catch (err) {
      console.error('Upload/Prediction error:', err);
      const errorMsg = err.response?.data?.error || err.response?.data?.message || 'Failed to process image. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Upload Medical Scan</h1>
          <p className="mt-2 text-gray-600">Upload lung CT scans for AI-powered analysis</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <svg className="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="ml-3 text-sm text-red-600">{error}</p>
            </div>
          </div>
        )}

        <div className="max-w-4xl">
          {/* File Upload Component */}
          <FileUpload onUploadSuccess={handleFileUpload} loading={loading} />
          
          {/* Loading State */}
          {loading && (
            <div className="mt-6">
              <LoadingSpinner message="Uploading and analyzing image... This may take a moment." />
            </div>
          )}

          {/* Prediction Result */}
          {prediction && !loading && (
            <PredictionResult prediction={prediction} />
          )}

          {/* Actions */}
          {prediction && !loading && (
            <div className="mt-6 flex space-x-4">
              <button
                onClick={() => setPrediction(null)}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Upload Another Scan
              </button>
              <button
                onClick={() => navigate('/history')}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
              >
                View All Predictions
              </button>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default UploadScan;
