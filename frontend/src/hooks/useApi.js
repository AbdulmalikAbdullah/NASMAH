import { useState } from 'react';

/**
 * Custom hook for managing API call states
 * Handles loading, error, and data states in a consistent way
 */
const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  /**
   * Execute an API call with automatic state management
   * @param {Function} apiFunc - Async function that makes the API call
   * @param {Object} options - Optional configuration
   * @returns {Promise} - Resolves with the API response data
   */
  const execute = async (apiFunc, options = {}) => {
    const { onSuccess, onError, resetData = true } = options;

    try {
      setLoading(true);
      setError(null);
      if (resetData) {
        setData(null);
      }

      const result = await apiFunc();
      setData(result);

      if (onSuccess) {
        onSuccess(result);
      }

      return result;
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'An error occurred';
      setError(errorMessage);

      if (onError) {
        onError(errorMessage);
      }

      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset all states to initial values
   */
  const reset = () => {
    setLoading(false);
    setError(null);
    setData(null);
  };

  return {
    loading,
    error,
    data,
    execute,
    reset,
    setError,
    setData,
  };
};

export default useApi;
