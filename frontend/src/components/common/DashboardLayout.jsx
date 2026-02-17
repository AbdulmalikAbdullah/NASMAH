import Sidebar from './Sidebar';

/**
 * Dashboard Layout Component
 * Provides consistent layout with sidebar for dashboard pages
 */
const DashboardLayout = ({ children }) => {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 ml-64 min-h-screen bg-gray-50">
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;
