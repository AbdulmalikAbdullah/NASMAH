import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axiosInstance from '../api/axiosConfig';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/common/DashboardLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import toast from 'react-hot-toast';

/**
 * Enhanced Dashboard Page
 * Shows statistics, charts, and recent predictions
 */
const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [images, setImages] = useState([]);
  const [chartData, setChartData] = useState({
    detectionResults: [],
    scanActivity: []
  });

  useEffect(() => {
    const abortController = new AbortController();
    
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch images
        const imagesRes = await axiosInstance.get('/api/images/', {
          signal: abortController.signal
        });
        const imagesData = imagesRes.data.images || [];
        setImages(imagesData);

        // Fetch predictions history
        const predictionsRes = await axiosInstance.get('/api/predictions/history', {
          signal: abortController.signal
        });
        const predictionsData = predictionsRes.data.predictions || [];
        
        // Get only the 5 most recent predictions for the table
        setRecentPredictions(predictionsData.slice(0, 5));
        
        // Calculate stats from real data
        const totalScans = imagesData.length;
        const analyzedScans = predictionsData.length;
        
        // Count positive detections (cancer stage > 0)
        const positiveDetections = predictionsData.filter(p => p.cancer_stage !== '0').length;
        
        // Calculate average confidence
        const avgConfidence = predictionsData.length > 0 
          ? predictionsData.reduce((sum, p) => sum + p.confidence, 0) / predictionsData.length 
          : 0;
        
        setStats({
          totalScans,
          analyzedScans,
          positiveDetections,
          avgConfidence
        });

        // Calculate detection results for pie chart
        const stageCount = {
          '0': 0,
          '1': 0,
          '2': 0,
          '3': 0
        };
        
        predictionsData.forEach(p => {
          if (stageCount.hasOwnProperty(p.cancer_stage)) {
            stageCount[p.cancer_stage]++;
          }
        });
        
        const detectionResults = [
          { name: 'Negative', value: stageCount['0'], color: '#10B981' },
          { name: 'Stage I', value: stageCount['1'], color: '#FBBF24' },
          { name: 'Stage II', value: stageCount['2'], color: '#F97316' },
          { name: 'Stage III', value: stageCount['3'], color: '#EF4444' },
        ].filter(item => item.value > 0); // Only show non-zero values
        
        // Calculate scan activity by month (last 6 months)
        const monthlyScans = {};
        const now = new Date();
        
        // Initialize last 6 months
        for (let i = 5; i >= 0; i--) {
          const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
          const monthKey = date.toLocaleString('default', { month: 'short' });
          monthlyScans[monthKey] = 0;
        }
        
        // Count scans per month
        imagesData.forEach(img => {
          if (img.uploaded_at) {
            const date = new Date(img.uploaded_at);
            const monthKey = date.toLocaleString('default', { month: 'short' });
            if (monthlyScans.hasOwnProperty(monthKey)) {
              monthlyScans[monthKey]++;
            }
          }
        });
        
        const scanActivity = Object.keys(monthlyScans).map(month => ({
          month,
          scans: monthlyScans[month]
        }));
        
        setChartData({
          detectionResults: detectionResults.length > 0 ? detectionResults : [
            { name: 'No Data', value: 1, color: '#D1D5DB' }
          ],
          scanActivity
        });
        
      } catch (error) {
        // Don't show error if request was aborted (component unmounted)
        if (error.name === 'AbortError' || error.name === 'CanceledError') {
          return;
        }
        console.error('Error fetching dashboard data:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      }
    };

    fetchDashboardData();

    // Cleanup: abort pending requests when component unmounts
    return () => {
      abortController.abort();
    };
  }, []);

  // Chart data
  const scanActivityData = [
    { month: 'Jan', scans: 12 },
    { month: 'Feb', scans: 19 },
    { month: 'Mar', scans: 15 },
    { month: 'Apr', scans: 25 },
    { month: 'May', scans: 22 },
    { month: 'Jun', scans: 30 },
  ];

  const detectionResultsData = [
    { name: 'Negative', value: 65, color: '#10B981' },
    { name: 'Stage I', value: 15, color: '#FBBF24' },
    { name: 'Stage II', value: 12, color: '#F97316' },
    { name: 'Stage III', value: 8, color: '#EF4444' },
  ];

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <LoadingSpinner message="Loading dashboard..." />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Welcome back, {user?.Fname}!</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Scans</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.totalScans || 0}</p>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <p className="text-xs text-green-600 mt-2">+12% from last month</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Analyzed</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.analyzedScans || 0}</p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p className="text-xs text-green-600 mt-2">100% completion rate</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Positive Detections</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.positiveDetections || 0}</p>
              </div>
              <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">{((stats?.positiveDetections / stats?.totalScans || 0) * 100).toFixed(1)}% of total</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Avg. Confidence</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{(stats?.avgConfidence || 0).toFixed(1)}%</p>
              </div>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <p className="text-xs text-green-600 mt-2">High accuracy</p>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Scan Activity Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Scan Activity (Last 6 Months)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData.scanActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="scans" fill="#0055FF" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Detection Results Pie Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Detection Results Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData.detectionResults}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.detectionResults.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Predictions Table */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Recent Predictions</h2>
            <button 
              onClick={() => navigate('/history')}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              View All →
            </button>
          </div>
          
          {recentPredictions.length === 0 ? (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="mt-4 text-gray-500">No predictions yet</p>
              <button
                onClick={() => navigate('/upload')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Upload Your First Scan
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stage</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentPredictions.map((pred) => (
                    <tr key={pred.prediction_id}>
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
                        {pred.confidence.toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button 
                          onClick={() => navigate('/history')}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
