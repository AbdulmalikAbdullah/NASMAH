import { useState } from 'react';
import Button from '../common/Button';

/**
 * File Upload Component for DICOM Images
 * Handles medical image file validation and upload
 */
const FileUpload = ({ onUploadSuccess, loading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  // Validate file type (supports multiple medical image formats)
  const validateFile = (file) => {
    const validExtensions = ['.dcm', '.dicom', '.npy', '.png', '.jpg', '.jpeg', '.zip'];
    const fileName = file.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValid) {
      setError('Invalid file type. Supported formats: DICOM (.dcm), NumPy (.npy), Images (.png, .jpg, .jpeg), or ZIP archive');
      return false;
    }

    // Check file size (max 500MB for batch uploads)
    const maxSize = 500 * 1024 * 1024; // 500MB in bytes
    if (file.size > maxSize) {
      setError('File size exceeds 500MB limit');
      return false;
    }

    setError('');
    return true;
  };

  // Handle file input change
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  };

  // Handle drag events
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  // Handle drop event
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  // Handle upload button click
  const handleUpload = () => {
    if (selectedFile) {
      onUploadSuccess(selectedFile);
    }
  };

  // Reset file selection
  const handleReset = () => {
    setSelectedFile(null);
    setError('');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 box-border">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Upload Medical Image</h2>
      
      {/* Drag and drop area */}
      <div
        className={`w-full border-2 border-dashed rounded-lg p-8 text-center transition-all ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
          aria-hidden="true"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        
        <div className="mt-4">
          <label
            htmlFor="file-upload"
            className="cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
          >
            <span>Click to upload</span>
            <input
              id="file-upload"
              name="file-upload"
              type="file"
              className="sr-only"
              accept=".dcm,.dicom,.npy,.png,.jpg,.jpeg,.zip"
              onChange={handleFileChange}
              disabled={loading}
            />
          </label>
          <p className="text-gray-600 ml-1">or drag and drop</p>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Supported: DICOM (.dcm), NumPy (.npy), Images (.png, .jpg), ZIP archives - Max 500MB
        </p>
      </div>

      {/* Error message */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Selected file info */}
      {selectedFile && !error && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <button
              onClick={handleReset}
              className="text-red-600 hover:text-red-800"
              disabled={loading}
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Upload button */}
      <div className="mt-6">
        <Button
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          loading={loading}
          variant="primary"
          fullWidth
        >
          {loading ? 'Uploading & Analyzing...' : 'Upload and Analyze'}
        </Button>
      </div>
    </div>
  );
};

export default FileUpload;
