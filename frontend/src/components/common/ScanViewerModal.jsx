import { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

/**
 * ScanViewerModal Component
 * Displays detailed scan analysis with S3 image viewer and clinical data
 * 
 * Features:
 * - S3 presigned URL image display with error handling
 * - Cancer stage and confidence score visualization
 * - Conditional batch analysis summary (if available)
 * - Modal controls: backdrop click, X button, Escape key
 * - Loading states and graceful fallbacks
 */
const ScanViewerModal = ({ isOpen, onClose, prediction }) => {
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);
  const [imageSource, setImageSource] = useState(null);

  // Load image when prediction changes
  useEffect(() => {
    if (prediction?.s3_url) {
      setImageSource(prediction.s3_url);
      setImageLoading(true);
      setImageError(false);
    } else {
      setImageError(true);
      setImageLoading(false);
    }
  }, [prediction]);

  // Handle Escape key press
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Event handlers
  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = (e) => {
    // Prevent infinite error loop
    if (e?.target) {
      e.target.onerror = null;
    }
    setImageError(true);
    setImageLoading(false);
  };

  const handleBackdropClick = (e) => {
    // Only close if clicking backdrop, not modal content
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Helper function to get cancer stage label with proper formatting
  const getStageLabel = (stage) => {
    const stageMap = {
      '0': 'Negative',
      '1': 'Stage I',
      '2': 'Stage II',
      '3': 'Stage III',
      '4': 'Stage IV'
    };
    return stageMap[stage] || 'Unknown';
  };

  // Helper function to get stage color
  const getStageColor = (stage) => {
    const colorMap = {
      '0': 'green',
      '1': 'yellow',
      '2': 'orange',
      '3': 'red',
      '4': 'darkred'
    };
    return colorMap[stage] || 'gray';
  };

  if (!isOpen || !prediction) return null;

  return (
    <div 
      className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div 
        className="relative bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b sticky top-0 bg-white z-10">
          <h2 className="text-2xl font-bold text-gray-900">Scan Analysis Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors p-2 hover:bg-gray-100 rounded-lg"
            aria-label="Close modal"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          {/* Image Section */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Visualization</h3>
            <div className="bg-gray-50 rounded-lg overflow-hidden min-h-[300px] flex items-center justify-center">
              {imageLoading && !imageError && (
                <div className="p-8">
                  <LoadingSpinner message="Loading visualization..." />
                </div>
              )}
              
              {imageError ? (
                <div className="bg-red-50 border-2 border-red-200 rounded-lg p-8 text-center m-4">
                  <svg className="h-16 w-16 text-red-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-red-800 font-semibold mb-2">Image Unavailable</p>
                  <p className="text-red-600 text-sm">
                    The visualization is currently processing or unavailable. 
                    Clinical data is still accessible below.
                  </p>
                </div>
              ) : (
                <img
                  src={imageSource}
                  alt="AI Scan Analysis"
                  className={`w-full rounded-lg ${imageLoading ? 'hidden' : 'block'}`}
                  onLoad={handleImageLoad}
                  onError={handleImageError}
                />
              )}
            </div>
          </div>

          {/* AI Clinical Data */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Clinical Assessment</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Cancer Stage */}
              <div className={`${
                prediction.cancer_stage === '0' ? 'bg-green-50 border-green-200' :
                prediction.cancer_stage === '1' ? 'bg-yellow-50 border-yellow-200' :
                prediction.cancer_stage === '2' ? 'bg-orange-50 border-orange-200' :
                prediction.cancer_stage === '3' ? 'bg-red-50 border-red-200' :
                prediction.cancer_stage === '4' ? 'bg-red-900 border-red-900' :
                'bg-gray-50 border-gray-200'
              } border-2 rounded-lg p-4`}>
                <p className={`text-sm font-medium mb-1 ${
                  prediction.cancer_stage === '4' ? 'text-red-200' : 'text-gray-600'
                }`}>Cancer Stage</p>
                <p className={`text-3xl font-bold ${
                  prediction.cancer_stage === '0' ? 'text-green-800' :
                  prediction.cancer_stage === '1' ? 'text-yellow-800' :
                  prediction.cancer_stage === '2' ? 'text-orange-800' :
                  prediction.cancer_stage === '3' ? 'text-red-800' :
                  prediction.cancer_stage === '4' ? 'text-white' :
                  'text-gray-800'
                }`}>
                  {getStageLabel(prediction.cancer_stage)}
                </p>
                <p className={`text-xs mt-2 ${
                  prediction.cancer_stage === '4' ? 'text-red-200' : 'text-gray-500'
                }`}>
                  {prediction.cancer_stage === '0' ? 'No malignancy detected' : 'Malignancy detected'}
                </p>
              </div>

              {/* Confidence Score */}
              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-600 mb-1">AI Confidence Score</p>
                <p className="text-3xl font-bold text-blue-800">{prediction.confidence}%</p>
                
                {/* Confidence Progress Bar */}
                <div className="mt-3 w-full bg-blue-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${prediction.confidence}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {prediction.confidence >= 90 ? 'High confidence' : 
                   prediction.confidence >= 70 ? 'Moderate confidence' : 'Low confidence'}
                </p>
              </div>
            </div>
          </div>

          {/* Conditional Batch Analysis Summary */}
          {prediction.batch_summary && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Batch Analysis Summary</h3>
              
              {/* Summary Cards Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-blue-700 font-medium mb-1">Total Slices</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {prediction.batch_summary.total_slices}
                  </p>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-red-700 font-medium mb-1">Tumors Detected</p>
                  <p className="text-2xl font-bold text-red-900">
                    {prediction.batch_summary.slices_with_tumors || prediction.batch_summary.tumor_slices || 0}
                  </p>
                </div>

                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-orange-700 font-medium mb-1">Max Tumor Size</p>
                  <p className="text-2xl font-bold text-orange-900">
                    {prediction.batch_summary.max_tumor_size}
                    {typeof prediction.batch_summary.max_tumor_size === 'number' && 'mm'}
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-green-700 font-medium mb-1">Avg Confidence</p>
                  <p className="text-2xl font-bold text-green-900">
                    {typeof prediction.batch_summary.avg_confidence === 'number' 
                      ? `${prediction.batch_summary.avg_confidence.toFixed(1)}%`
                      : prediction.batch_summary.avg_confidence}
                  </p>
                </div>
              </div>

              {/* Top Affected Slices Table */}
              {prediction.batch_summary.top_slices && prediction.batch_summary.top_slices.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Top Affected Slices</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="px-4 py-2 text-left font-medium text-gray-700">Slice #</th>
                          <th className="px-4 py-2 text-left font-medium text-gray-700">Stage</th>
                          <th className="px-4 py-2 text-left font-medium text-gray-700">Confidence</th>
                          <th className="px-4 py-2 text-left font-medium text-gray-700">Tumor Size</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {prediction.batch_summary.top_slices.map((slice, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-4 py-2">
                              {slice.slice_number || slice.slice_index || index + 1}
                            </td>
                            <td className="px-4 py-2">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${getStageColor(slice.stage)}-100 text-${getStageColor(slice.stage)}-800`}>
                                {slice.stage_label || getStageLabel(slice.stage)}
                              </span>
                            </td>
                            <td className="px-4 py-2">
                              {typeof slice.confidence === 'number' 
                                ? `${slice.confidence.toFixed(1)}%`
                                : slice.confidence_rate
                                ? `${(slice.confidence_rate * 100).toFixed(1)}%`
                                : 'N/A'}
                            </td>
                            <td className="px-4 py-2">
                              {slice.tumor_size || slice.tumor_size_mm 
                                ? `${(slice.tumor_size || slice.tumor_size_mm).toFixed(1)} mm`
                                : 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Model Information */}
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Deep Learning Model</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                <span className="text-sm text-gray-700 font-medium">
                  {prediction.model_name || 'U-Net Lung Segmentation'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 text-sm text-gray-600 flex flex-wrap gap-4 justify-between items-center">
          <div className="flex items-center space-x-2">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span className="font-medium">File:</span>
            <span className="text-gray-700">{prediction.image_name || 'Unknown'}</span>
          </div>

          <div className="flex items-center space-x-2">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
            </svg>
            <span className="font-medium">ID:</span>
            <span className="text-gray-700">{prediction.image_id}</span>
          </div>

          <div className="flex items-center space-x-2">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">Analyzed:</span>
            <span className="text-gray-700">
              {prediction.timestamp 
                ? new Date(prediction.timestamp).toLocaleString()
                : 'Unknown'}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span className="font-medium">Mode:</span>
            <span className="text-gray-700">
              {prediction.batch_summary ? 'Batch (Multiple Slices)' : 'Single Image'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanViewerModal;
