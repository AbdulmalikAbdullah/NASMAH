import { useState, useEffect } from 'react';
import DashboardLayout from '../components/common/DashboardLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import axiosInstance from '../api/axiosConfig';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

/**
 * Profile Page
 * View and edit user profile information
 */
const Profile = () => {
  const { user: authUser, setUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  
  const [profileData, setProfileData] = useState({
    fname: '',
    lname: '',
    email: ''
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    const abortController = new AbortController();
    
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get('/api/auth/me', {
          signal: abortController.signal
        });
        const userData = response.data.user;
        setProfileData({
          fname: userData.Fname || '',
          lname: userData.Lname || '',
          email: userData.email || ''
        });
      } catch (error) {
        if (error.name === 'AbortError' || error.name === 'CanceledError') {
          return;
        }
        console.error('Error fetching profile:', error);
        toast.error('Failed to load profile');
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      }
    };

    fetchProfile();

    return () => {
      abortController.abort();
    };
  }, []);

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    
    const newErrors = {};
    if (!profileData.fname) newErrors.fname = 'First name is required';
    if (!profileData.lname) newErrors.lname = 'Last name is required';
    if (!profileData.email) newErrors.email = 'Email is required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      setSaving(true);
      const response = await axiosInstance.put('/api/auth/me', profileData);
      
      // Update auth context
      const updatedUser = response.data.user;
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);
      
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Error updating profile:', error);
      const errorMsg = error.response?.data?.error || 'Failed to update profile';
      toast.error(errorMsg);
      setErrors({ general: errorMsg });
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    const newErrors = {};
    if (!passwordData.currentPassword) newErrors.currentPassword = 'Current password is required';
    if (!passwordData.newPassword) newErrors.newPassword = 'New password is required';
    if (passwordData.newPassword.length < 6) newErrors.newPassword = 'Password must be at least 6 characters';
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      setChangingPassword(true);
      await axiosInstance.post('/api/auth/change-password', {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      });
      
      toast.success('Password changed successfully');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      console.error('Error changing password:', error);
      const errorMsg = error.response?.data?.error || 'Failed to change password';
      toast.error(errorMsg);
      setErrors({ passwordGeneral: errorMsg });
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-screen">
          <LoadingSpinner message="Loading profile..." />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
          <p className="mt-2 text-gray-600">Manage your account information</p>
        </div>

        <div className="max-w-3xl">
          {/* Profile Information */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Personal Information</h2>
            
            {errors.general && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{errors.general}</p>
              </div>
            )}

            <form onSubmit={handleProfileSubmit} className="space-y-6">
              <Input
                label="First Name"
                type="text"
                name="fname"
                value={profileData.fname}
                onChange={handleProfileChange}
                error={errors.fname}
                required
                disabled={saving}
              />

              <Input
                label="Last Name"
                type="text"
                name="lname"
                value={profileData.lname}
                onChange={handleProfileChange}
                error={errors.lname}
                required
                disabled={saving}
              />

              <Input
                label="Email Address"
                type="email"
                name="email"
                value={profileData.email}
                onChange={handleProfileChange}
                error={errors.email}
                required
                disabled={saving}
              />

              <div className="flex items-center justify-between pt-4">
                <div>
                  <p className="text-sm text-gray-500">Role: <span className="font-medium text-gray-900">{authUser?.role}</span></p>
                  <p className="text-sm text-gray-500">Member since: <span className="font-medium text-gray-900">{authUser?.created_at ? new Date(authUser.created_at).toLocaleDateString() : 'N/A'}</span></p>
                </div>
                <Button
                  type="submit"
                  variant="primary"
                  loading={saving}
                  disabled={saving}
                >
                  Save Changes
                </Button>
              </div>
            </form>
          </div>

          {/* Change Password */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Change Password</h2>
            
            {errors.passwordGeneral && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{errors.passwordGeneral}</p>
              </div>
            )}

            <form onSubmit={handlePasswordSubmit} className="space-y-6">
              <Input
                label="Current Password"
                type="password"
                name="currentPassword"
                value={passwordData.currentPassword}
                onChange={handlePasswordChange}
                error={errors.currentPassword}
                required
                disabled={changingPassword}
              />

              <Input
                label="New Password"
                type="password"
                name="newPassword"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
                error={errors.newPassword}
                required
                disabled={changingPassword}
                placeholder="At least 6 characters"
              />

              <Input
                label="Confirm New Password"
                type="password"
                name="confirmPassword"
                value={passwordData.confirmPassword}
                onChange={handlePasswordChange}
                error={errors.confirmPassword}
                required
                disabled={changingPassword}
              />

              <div className="flex justify-end pt-4">
                <Button
                  type="submit"
                  variant="primary"
                  loading={changingPassword}
                  disabled={changingPassword}
                >
                  Update Password
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Profile;
