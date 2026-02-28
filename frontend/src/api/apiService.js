/**
 * API Service Examples
 * 
 * This file demonstrates how to add more API endpoints for future features.
 * Copy these patterns when implementing Admin Panel and System Logs.
 */

import axiosInstance from './axiosConfig';

// ============================================
// AUTHENTICATION SERVICES (Already implemented in AuthContext)
// ============================================

export const authService = {
  login: async (email, password) => {
    const response = await axiosInstance.post('/api/auth/login', { email, password });
    return response.data;
  },

  register: async (username, email, password) => {
    const response = await axiosInstance.post('/api/auth/register', { username, email, password });
    return response.data;
  },

  logout: async () => {
    const response = await axiosInstance.post('/api/auth/logout');
    return response.data;
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await axiosInstance.post('/api/auth/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    });
    return response.data;
  },

  forgotPassword: async (email) => {
    const response = await axiosInstance.post('/api/auth/forgot-password', { email });
    return response.data;
  },

  resetPassword: async (token, newPassword) => {
    const response = await axiosInstance.post('/api/auth/reset-password', { token, new_password: newPassword });
    return response.data;
  },
};

// ============================================
// IMAGE SERVICES
// ============================================

export const imageService = {
  uploadImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axiosInstance.post('/api/images/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  getImages: async (page = 1, perPage = 10) => {
    const response = await axiosInstance.get('/api/images', {
      params: { page, per_page: perPage }
    });
    return response.data;
  },

  getImage: async (imageId) => {
    const response = await axiosInstance.get(`/api/images/${imageId}`);
    return response.data;
  },

  deleteImage: async (imageId) => {
    const response = await axiosInstance.delete(`/api/images/${imageId}`);
    return response.data;
  },
};

// ============================================
// PREDICTION SERVICES
// ============================================

export const predictionService = {
  makePrediction: async (imageId) => {
    const response = await axiosInstance.post('/api/predictions/predict', {
      image_id: imageId
    });
    return response.data;
  },

  getPredictions: async (page = 1, perPage = 10) => {
    const response = await axiosInstance.get('/api/predictions', {
      params: { page, per_page: perPage }
    });
    return response.data;
  },

  getPrediction: async (predictionId) => {
    const response = await axiosInstance.get(`/api/predictions/${predictionId}`);
    return response.data;
  },

  getPredictionHistory: async (imageId) => {
    const response = await axiosInstance.get(`/api/predictions/history/${imageId}`);
    return response.data;
  },
};

// ============================================
// ADMIN SERVICES (For future Admin Panel)
// ============================================

export const adminService = {
  // Get all users with pagination
  getAllUsers: async (page = 1, perPage = 20) => {
    const response = await axiosInstance.get('/api/admin/users', {
      params: { page, per_page: perPage }
    });
    return response.data;
  },

  // Get specific user by ID
  getUser: async (userId) => {
    const response = await axiosInstance.get(`/api/admin/users/${userId}`);
    return response.data;
  },

  // Activate or deactivate user
  activateUser: async (userId, isActive) => {
    const response = await axiosInstance.put(`/api/admin/users/${userId}/activate`, {
      is_active: isActive
    });
    return response.data;
  },

  // Get system statistics
  getStatistics: async () => {
    const response = await axiosInstance.get('/api/admin/statistics');
    return response.data;
  },
};

// ============================================
// LOG SERVICES (For future System Logs page)
// ============================================

export const logService = {
  // Get logs with filters
  getLogs: async (filters = {}) => {
    const { page = 1, perPage = 20, userId, action, startDate, endDate } = filters;
    
    const params = {
      page,
      per_page: perPage,
    };
    
    if (userId) params.user_id = userId;
    if (action) params.action = action;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await axiosInstance.get('/api/logs', { params });
    return response.data;
  },

  // Get distinct log actions
  getLogActions: async () => {
    const response = await axiosInstance.get('/api/logs/actions');
    return response.data;
  },
};

// ============================================
// USAGE EXAMPLES
// ============================================

/**
 * Example 1: Using in a component
 * 
 * import { adminService } from '../api/apiService';
 * import useApi from '../hooks/useApi';
 * 
 * const AdminPanel = () => {
 *   const { loading, error, data, execute } = useApi();
 *   
 *   useEffect(() => {
 *     execute(async () => {
 *       return await adminService.getAllUsers();
 *     });
 *   }, []);
 *   
 *   if (loading) return <LoadingSpinner />;
 *   if (error) return <div>Error: {error}</div>;
 *   
 *   return (
 *     <div>
 *       {data?.users.map(user => (
 *         <UserCard key={user.id} user={user} />
 *       ))}
 *     </div>
 *   );
 * };
 */

/**
 * Example 2: Direct usage with try-catch
 * 
 * const handleActivateUser = async (userId, isActive) => {
 *   try {
 *     const result = await adminService.activateUser(userId, isActive);
 *     console.log('User updated:', result);
 *   } catch (error) {
 *     console.error('Failed to update user:', error);
 *   }
 * };
 */

/**
 * Example 3: Using with pagination
 * 
 * const [page, setPage] = useState(1);
 * 
 * const loadLogs = async () => {
 *   const logs = await logService.getLogs({
 *     page,
 *     perPage: 20,
 *     action: 'LOGIN',
 *     startDate: '2024-01-01',
 *   });
 *   setLogs(logs.logs);
 * };
 */
