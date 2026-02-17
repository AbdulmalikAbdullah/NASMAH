import { useState, useEffect } from 'react';
import DashboardLayout from '../components/common/DashboardLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import axiosInstance from '../api/axiosConfig';
import toast from 'react-hot-toast';

/**
 * Prediction History Page
 * View all past predictions with filtering
 */
const PredictionHistory = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, 0, 1, 2, 3
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const abortController = new AbortController();
    
    const fetchPredictions = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get('/api/predictions/history', {
          signal: abortController.signal
        });
        setPredictions(response.data.predictions || []);
      } catch (error) {
        if (error.name === 'AbortError' || error.name === 'CanceledError') {
          return;
        }
        console.error('Error fetching predictions:', error);
        toast.error('Failed to load prediction history');
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      }
    };

    fetchPredictions();

    return () => {
      abortController.abort();
    };
  }, []);

  const handleViewDetails = (prediction) => {
    setSelectedPrediction(prediction);
    setShowModal(true);
  };

  const handleDeleteImage = async (imageId, predictionId) => {
    if (!confirm('Are you sure you want to delete this image and its prediction?')) return;

    try {
      await axiosInstance.delete(`/api/images/${imageId}`);
      toast.success('Image deleted successfully');
      // Remove from local state
      setPredictions(predictions.filter(p => p.prediction_id !== predictionId));
    } catch (error) {
      console.error('Error deleting image:', error);
      toast.error('Failed to delete image');
    }
  };

  const filteredPredictions = filter === 'all' 
    ? predictions 
    : predictions.filter(p => p.cancer_stage === filter);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <LoadingSpinner message="Loading predictions..." />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Prediction History</h1>
          <p className="mt-2 text-gray-600">View all your past AI predictions</p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All ({predictions.length})
          </button>
          <button
            onClick={() => setFilter('0')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === '0' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Negative ({predictions.filter(p => p.cancer_stage === '0').length})
          </button>
          <button
            onClick={() => setFilter('1')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === '1' ? 'bg-yellow-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Stage I ({predictions.filter(p => p.cancer_stage === '1').length})
          </button>
          <button
            onClick={() => setFilter('2')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === '2' ? 'bg-orange-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Stage II ({predictions.filter(p => p.cancer_stage === '2').length})
          </button>
          <button
            onClick={() => setFilter('3')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === '3' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Stage III ({predictions.filter(p => p.cancer_stage === '3').length})
          </button>
        </div>

        {/* Predictions List */}
        {filteredPredictions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-4 text-gray-500">No predictions found</p>
            <a href="/upload" className="mt-4 inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Create Your First Prediction
            </a>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stage</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredPredictions.map((pred) => (
                    <tr key={pred.prediction_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(pred.timestamp).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {pred.image_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          pred.cancer_stage === '0' ? 'bg-green-100 text-green-800' :
                          pred.cancer_stage === '1' ? 'bg-yellow-100 text-yellow-800' :
                          pred.cancer_stage === '2' ? 'bg-orange-100 text-orange-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {pred.prediction_label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className={`h-2 rounded-full ${
                                pred.confidence >= 90 ? 'bg-green-500' : 
                                pred.confidence >= 70 ? 'bg-yellow-500' : 
                                'bg-orange-500'
                              }`}
                              style={{ width: `${pred.confidence}%` }}
                            ></div>
                          </div>
                          <span>{pred.confidence.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {pred.model_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <button 
                          onClick={() => handleViewDetails(pred)}
                          className="text-blue-600 hover:text-blue-900 font-medium"
                        >
                          View
                        </button>
                        <button 
                          onClick={() => handleDeleteImage(pred.image_id, pred.prediction_id)}
                          className="text-red-600 hover:text-red-900 font-medium"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Details Modal */}
        {showModal && selectedPrediction && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen px-4">
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowModal(false)}></div>
              
              <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-2xl font-bold text-gray-900">Prediction Details</h3>
                  <button
                    onClick={() => setShowModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Image Name</p>
                      <p className="mt-1 text-sm text-gray-900">{selectedPrediction.image_name}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Date</p>
                      <p className="mt-1 text-sm text-gray-900">{new Date(selectedPrediction.timestamp).toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Prediction</p>
                      <p className="mt-1">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          selectedPrediction.cancer_stage === '0' ? 'bg-green-100 text-green-800' :
                          selectedPrediction.cancer_stage === '1' ? 'bg-yellow-100 text-yellow-800' :
                          selectedPrediction.cancer_stage === '2' ? 'bg-orange-100 text-orange-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {selectedPrediction.prediction_label}
                        </span>
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Confidence</p>
                      <p className="mt-1 text-sm text-gray-900">{selectedPrediction.confidence.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Model</p>
                      <p className="mt-1 text-sm text-gray-900">{selectedPrediction.model_name}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Image ID</p>
                      <p className="mt-1 text-sm text-gray-900">#{selectedPrediction.image_id}</p>
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <p className="text-sm font-medium text-gray-500 mb-2">AI Segmentation Result</p>
                    <div className="bg-gray-100 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-500">Visualization available in future update</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default PredictionHistory;
