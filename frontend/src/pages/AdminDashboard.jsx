import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import DashboardLayout from '../components/common/DashboardLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import axiosInstance from '../api/axiosConfig';
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';

/**
 * AdminDashboard Component
 * System-wide oversight and AI performance monitoring for administrators
 */
const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axiosInstance.get('/api/admin/stats', {
          signal: controller.signal
        });

        if (response.data.stats) {
          setStats(response.data.stats);
        }
      } catch (err) {
        if (err.name !== 'AbortError' && err.name !== 'CanceledError') {
          console.error('Error fetching admin stats:', err);
          setError(err.response?.data?.error || 'Failed to load statistics');
          toast.error('Failed to load system statistics');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStats();

    return () => controller.abort();
  }, []);

  // Transform predictions.by_stage to chart data
  const getChartData = () => {
    if (!stats?.predictions?.by_stage) return [];

    const stageLabels = {
      '0': 'Negative',
      '1': 'Stage I',
      '2': 'Stage II',
      '3': 'Stage III',
      '4': 'Stage IV'
    };

    const stageColors = {
      '0': '#10B981',
      '1': '#FBBF24',
      '2': '#F97316',
      '3': '#EF4444',
      '4': '#DC2626'
    };

    return Object.keys(stats.predictions.by_stage).map(stage => ({
      stage: stage,
      label: stageLabels[stage] || `Stage ${stage}`,
      count: stats.predictions.by_stage[stage],
      color: stageColors[stage]
    }));
  };

  const refetch = () => {
    setLoading(true);
    setError(null);
    window.location.reload();
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <LoadingSpinner message="Loading system statistics..." />
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <svg className="h-12 w-12 text-red-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Statistics</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={refetch}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!stats) {
    return (
      <DashboardLayout>
        <div className="p-8">
          <div className="text-center text-gray-500">No statistics available</div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">System Overview</h1>
          <p className="mt-2 text-gray-600">
            Platform-wide health monitoring and AI performance metrics
          </p>
        </div>

        {/* Section A: User Metrics */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">User Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Total Users */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Total Users</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stats.users.total}
                  </p>
                </div>
                <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Active Users */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Active Users</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">
                    {stats.users.active}
                  </p>
                </div>
                <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">
                {stats.users.total > 0 ? ((stats.users.active / stats.users.total) * 100).toFixed(1) : 0}% of total
              </p>
            </div>

            {/* Deactivated Users */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Deactivated</p>
                  <p className="text-3xl font-bold text-red-600 mt-2">
                    {stats.users.deactivated}
                  </p>
                </div>
                <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">Inactive accounts</p>
            </div>

            {/* New Signups (30d) */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">New Signups (30d)</p>
                  <p className="text-3xl font-bold text-blue-600 mt-2">
                    {stats.users.new_30_days}
                  </p>
                </div>
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">Last 30 days</p>
            </div>

            {/* Admins */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Admins</p>
                  <p className="text-3xl font-bold text-indigo-600 mt-2">
                    {stats.users.admins}
                  </p>
                </div>
                <div className="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">System administrators</p>
            </div>

            {/* Patients */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Patients</p>
                  <p className="text-3xl font-bold text-purple-600 mt-2">
                    {stats.users.patients}
                  </p>
                </div>
                <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">Regular users</p>
            </div>
          </div>
        </div>

        {/* Section B: AI Health KPIs */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Performance Monitoring</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Average Confidence Score */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm font-medium text-purple-700">Avg. Confidence Score</p>
                  <p className="text-4xl font-bold text-purple-900 mt-2">
                    {stats.predictions.average_confidence}%
                  </p>
                </div>
                <div className="h-14 w-14 bg-purple-200 rounded-full flex items-center justify-center">
                  <svg className="h-8 w-8 text-purple-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div className="w-full bg-purple-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${stats.predictions.average_confidence}%` }}
                />
              </div>
            </div>

            {/* Inference Success Rate */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm font-medium text-green-700">Inference Success Rate</p>
                  <p className="text-4xl font-bold text-green-900 mt-2">
                    {stats.ai.inference_success_rate}%
                  </p>
                </div>
                <div className="h-14 w-14 bg-green-200 rounded-full flex items-center justify-center">
                  <svg className="h-8 w-8 text-green-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-green-700">Valid images with predictions</p>
            </div>

            {/* Total Predictions */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm font-medium text-blue-700">Total Predictions</p>
                  <p className="text-4xl font-bold text-blue-900 mt-2">
                    {stats.predictions.total.toLocaleString()}
                  </p>
                </div>
                <div className="h-14 w-14 bg-blue-200 rounded-full flex items-center justify-center">
                  <svg className="h-8 w-8 text-blue-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-blue-700">
                {stats.predictions.recent_30_days} in last 30 days
              </p>
            </div>
          </div>
        </div>

        {/* Section C: Classification Distribution */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Classification Distribution</h2>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-4">
              <h3 className="text-lg font-medium text-gray-900">Breakdown by Cancer Stage</h3>
              <p className="text-sm text-gray-500 mt-1">
                Distribution of predictions across all cancer stages
              </p>
            </div>

            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" name="Predictions">
                  {getChartData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* Stage Summary Table */}
            <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
              {getChartData().map((stage) => (
                <div
                  key={stage.stage}
                  className="border rounded-lg p-3 text-center hover:shadow-md transition-shadow"
                >
                  <div
                    className="w-4 h-4 rounded-full mx-auto mb-2"
                    style={{ backgroundColor: stage.color }}
                  />
                  <p className="text-xs font-medium text-gray-600">{stage.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stage.count}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Additional System Info */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">System Activity</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Total Images */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Total Images</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stats.images.total}
                  </p>
                </div>
                <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">
                {stats.images.recent_30_days} uploaded in last 30 days
              </p>
            </div>

            {/* Valid Images */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Valid Images</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">
                    {stats.images.valid}
                  </p>
                </div>
                <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">
                {stats.images.total > 0 ? ((stats.images.valid / stats.images.total) * 100).toFixed(1) : 0}% validation rate
              </p>
            </div>

            {/* Recent Predictions */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Recent Predictions</p>
                  <p className="text-3xl font-bold text-blue-600 mt-2">
                    {stats.predictions.recent_30_days}
                  </p>
                </div>
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">Last 30 days</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;
