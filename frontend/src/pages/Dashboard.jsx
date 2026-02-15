import { useState } from 'react';
import axiosInstance from '../api/axiosConfig';
import useApi from '../hooks/useApi';
import FileUpload from '../components/dashboard/FileUpload';
import PredictionResult from '../components/dashboard/PredictionResult';
import LoadingSpinner from '../components/common/LoadingSpinner';

/**
 * Dashboard Page Component
 * Main interface for uploading DICOM images and viewing predictions
 */
const Dashboard = () => {
  const [prediction, setPrediction] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const { loading, error, execute, setError } = useApi();

  /**
   * Handle file upload and prediction workflow
   * 1. Upload DICOM file to /api/images/upload
   * 2. Get image_id from response
   * 3. Request prediction using /api/predictions/predict
   * 4. Display result
   */
  const handleFileUpload = async (file) => {
    try {
      // Step 1: Upload DICOM image
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

        // Step 2: Request prediction
        const predictionResponse = await axiosInstance.post('/api/predictions/predict', {
          image_id: imageId,
        });

        const { prediction, metrics, visualization, batch_mode, summary, top_results } = predictionResponse.data;
        
        // Step 3: Update state with prediction and additional data
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

        // Add to recent predictions
        setRecentPredictions(prev => [
          {
            ...prediction,
            image_id: imageId,
            fileName: file.name,
            timestamp: new Date().toISOString(),
          },
          ...prev.slice(0, 4), // Keep only 5 most recent
        ]);

        return prediction;
      });
    } catch (err) {
      console.error('Upload/Prediction error:', err);
      setError(err.response?.data?.error || err.response?.data?.message || 'Failed to process image. Please try again.');
    }
  };

  /**
   * Handle viewing a previous prediction
   */
  const handleViewPrediction = (pred) => {
    setPrediction(pred);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Prediction Dashboard</h1>
          <p className="mt-2 text-gray-600">Upload DICOM images for lung cancer stage prediction</p>
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

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - File Upload */}
          <div className="lg:col-span-2">
            <FileUpload onUploadSuccess={handleFileUpload} loading={loading} />
            
            {/* Loading State */}
            {loading && (
              <LoadingSpinner message="Uploading and analyzing image... This may take a moment." />
            )}

            {/* Prediction Result */}
            {prediction && !loading && (
              <PredictionResult prediction={prediction} />
            )}
          </div>

          {/* Right Column - Recent Predictions */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Predictions</h2>
              
              {recentPredictions.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500">No predictions yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentPredictions.map((pred, index) => (
                    <div
                      key={index}
                      className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => handleViewPrediction(pred)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {pred.fileName || `Image ${pred.image_id}`}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(pred.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <div className="ml-3 flex-shrink-0">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            pred.cancer_stage === '0' ? 'bg-green-100 text-green-800' :
                            pred.cancer_stage === '1' ? 'bg-yellow-100 text-yellow-800' :
                            pred.cancer_stage === '2' ? 'bg-orange-100 text-orange-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            Stage {pred.cancer_stage}
                          </span>
                        </div>
                      </div>
                      <div className="mt-1">
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${
                              pred.confidence >= 0.9 ? 'bg-green-500' : 
                              pred.confidence >= 0.7 ? 'bg-yellow-500' : 
                              'bg-orange-500'
                            }`}
                            style={{ width: `${pred.confidence * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Stats */}
            <div className="mt-6 bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Session Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Predictions</span>
                  <span className="text-lg font-bold text-blue-600">{recentPredictions.length}</span>
                </div>
                {recentPredictions.length > 0 && (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Average Confidence</span>
                      <span className="text-lg font-bold text-green-600">
                        {(recentPredictions.reduce((acc, p) => acc + p.confidence, 0) / recentPredictions.length * 100).toFixed(1)}%
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
