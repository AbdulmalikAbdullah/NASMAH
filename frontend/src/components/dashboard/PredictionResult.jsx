/**
 * Prediction Result Component
 * Displays AI model prediction results with visual indicators
 */
const PredictionResult = ({ prediction }) => {
  if (!prediction) {
    return null;
  }

  const { 
    cancer_stage, 
    confidence, 
    timestamp, 
    image_id, 
    metrics, 
    visualization,
    batch_mode,
    summary,
    top_results,
    fileName
  } = prediction;
  // determine whether this prediction represents a batch upload
  const isBatch = Boolean(batch_mode) || Boolean(summary);

  // Get color based on prediction stage
  const getStageColor = (stage) => {
    const stageColors = {
      '0': 'bg-green-100 text-green-800 border-green-300',
      '1': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      '2': 'bg-orange-100 text-orange-800 border-orange-300',
      '3': 'bg-red-100 text-red-800 border-red-300',
    };
    return stageColors[stage] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  // Get confidence color
  const getConfidenceColor = (conf) => {
    if (conf >= 0.9) return 'text-green-600';
    if (conf >= 0.7) return 'text-yellow-600';
    return 'text-orange-600';
  };

  // Format timestamp
  const formatTimestamp = (ts) => {
    if (!ts) return 'N/A';
    try {
      return new Date(ts).toLocaleString();
    } catch {
      return ts;
    }
  };

  // Get stage label
  const getStageLabel = () => {
    if (metrics?.tumor_stage_label) return metrics.tumor_stage_label;
    const labels = {
      '0': 'Negative (No tumor or < 10mm)',
      '1': 'Stage I (10-39mm)',
      '2': 'Stage II (40-69mm)',
      '3': 'Stage III (≥ 70mm)',
      '4': 'Stage IV (≥ 70mm)'
    };
    return labels[cancer_stage] || `Stage ${cancer_stage}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Prediction Result</h2>
        <svg className="h-8 w-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <div className="space-y-4">
        {/* Predicted Stage */}
        <div className="border-b pb-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Predicted Cancer Stage</h3>
          <div className={`inline-block px-6 py-3 rounded-lg border-2 ${getStageColor(cancer_stage)}`}>
            <span className="text-3xl font-bold">Stage {cancer_stage}</span>
          </div>
          <p className="text-sm text-gray-600 mt-2">{getStageLabel()}</p>
        </div>

        {/* Confidence Score */}
        <div className="border-b pb-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Confidence Score</h3>
          <div className="flex items-center space-x-4">
            <div className="flex-1 bg-gray-200 rounded-full h-4">
              <div
                className={`h-4 rounded-full ${
                  confidence >= 0.9 ? 'bg-green-500' : confidence >= 0.7 ? 'bg-yellow-500' : 'bg-orange-500'
                }`}
                style={{ width: `${confidence * 100}%` }}
              ></div>
            </div>
            <span className={`text-2xl font-bold ${getConfidenceColor(confidence)}`}>
              {(confidence * 100).toFixed(1)}%
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {confidence >= 0.9 ? 'High confidence' : confidence >= 0.7 ? 'Medium confidence' : 'Low confidence - Consider reviewing manually'}
          </p>
        </div>

        {/* Tumor Metrics (if available) */}
        {metrics && (
          <div className="border-b pb-4">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Tumor Analysis</h3>
            <div className="grid grid-cols-2 gap-4">
              {metrics.has_tumor !== undefined && (
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-xs text-gray-500">Tumor Detected</p>
                  <p className={`text-lg font-bold ${metrics.has_tumor ? 'text-red-600' : 'text-green-600'}`}>
                    {metrics.has_tumor ? 'Yes' : 'No'}
                  </p>
                </div>
              )}
              {metrics.tumor_size_mm !== undefined && (
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-xs text-gray-500">Tumor Size</p>
                  <p className="text-lg font-bold text-gray-900">{metrics.tumor_size_mm.toFixed(2)} mm²</p>
                </div>
              )}
              {metrics.tumor_pixels !== undefined && (
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-xs text-gray-500">Tumor Pixels</p>
                  <p className="text-lg font-bold text-gray-900">{metrics.tumor_pixels.toLocaleString()}</p>
                </div>
              )}
              {metrics.confidence_rate !== undefined && (
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-xs text-gray-500">Region Confidence</p>
                  <p className="text-lg font-bold text-gray-900">{(metrics.confidence_rate * 100).toFixed(1)}%</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Batch Summary (if batch mode) */}
        {isBatch && summary && (
          <div className="border-b pb-4">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Batch Analysis Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-xs text-blue-600">Total Slices</p>
                <p className="text-lg font-bold text-blue-900">{summary.total_slices}</p>
              </div>
              <div className="bg-red-50 p-3 rounded">
                <p className="text-xs text-red-600">Slices with Tumors</p>
                <p className="text-lg font-bold text-red-900">{summary.tumor_slices}</p>
              </div>
              <div className="bg-orange-50 p-3 rounded">
                <p className="text-xs text-orange-600">Max Tumor Size</p>
                <p className="text-lg font-bold text-orange-900">{summary.max_tumor_size?.toFixed(2)} mm²</p>
              </div>
              <div className="bg-green-50 p-3 rounded">
                <p className="text-xs text-green-600">Avg Confidence</p>
                <p className="text-lg font-bold text-green-900">{(summary.avg_confidence * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        )}

        {/* Visualization Image */}
        {visualization && (
          <div className="border-b pb-4">
            <h3 className="text-sm font-medium text-gray-500 mb-3">AI Visualization</h3>
            <div className="bg-gray-100 p-2 rounded-lg">
              <img 
                src={`data:image/png;base64,${visualization}`} 
                alt="Prediction visualization"
                className="w-full h-auto rounded"
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {isBatch 
                ? 'Showing top slices with detected tumors (Original | Overlay | Confidence Map)'
                : 'Left: Original | Center: Tumor Overlay | Right: Confidence Map'}
            </p>
          </div>
        )}

        {/* Top Results (if batch mode) */}
        {isBatch && top_results && top_results.length > 0 && (
          <div className="border-b pb-4">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Top Affected Slices</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Slice</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Size (mm²)</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Stage</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {top_results.slice(0, 5).map((result, idx) => (
                    <tr key={idx}>
                      <td className="px-3 py-2 text-sm text-gray-900">#{result.slice_index}</td>
                      <td className="px-3 py-2 text-sm text-gray-900">{result.tumor_size_mm.toFixed(2)}</td>
                      <td className="px-3 py-2 text-sm">
                        <span className={`px-2 py-1 rounded text-xs ${getStageColor(String(result.stage))}`}>
                          {result.stage_label || `Stage ${result.stage}`}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-sm text-gray-900">{(result.confidence_rate * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Additional Information */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">File Name</h3>
            <p className="text-gray-900 text-sm truncate">{fileName || 'N/A'}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">Image ID</h3>
            <p className="text-gray-900 font-mono text-sm">{image_id || 'N/A'}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">Analysis Time</h3>
            <p className="text-gray-900 text-sm">{formatTimestamp(timestamp)}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">Mode</h3>
            <p className="text-gray-900 text-sm">{isBatch ? 'Batch (Multiple Slices)' : 'Single Image'}</p>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <div className="flex">
            <svg className="h-5 w-5 text-blue-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Medical Disclaimer</h3>
              <p className="text-sm text-blue-700 mt-1">
                This AI prediction is for research purposes only and should not be used as a substitute for professional medical diagnosis. 
                Please consult with a qualified healthcare provider for medical advice.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionResult;
