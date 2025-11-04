import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUsers, FiTruck, FiActivity, FiSettings, FiLogOut, FiShield } from 'react-icons/fi';

function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [vehicles, setVehicles] = useState([]);
  const [users, setUsers] = useState([]);
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Static demo data
    const demoStats = {
      totalVehicles: 25,
      authorizedVehicles: 18,
      pendingVehicles: 4,
      rejectedVehicles: 3
    };
    
    const demoUsers = [
      { id: 1, username: 'admin', email: 'admin@securepass.com', role: 'admin' },
      { id: 2, username: 'manager1', email: 'manager@securepass.com', role: 'manager' },
      { id: 3, username: 'security1', email: 'security@securepass.com', role: 'security' }
    ];
    
    const demoDetections = [
      {
        id: 1,
        licensePlate: 'MH12AB1234',
        timestamp: '2024-11-04 10:30:25',
        location: 'Main Gate',
        status: 'authorized'
      },
      {
        id: 2,
        licensePlate: 'DL05CD5678',
        timestamp: '2024-11-04 09:15:42',
        location: 'Parking Lot A',
        status: 'authorized'
      },
      {
        id: 3,
        licensePlate: 'XX99ZZ1111',
        timestamp: '2024-11-04 11:45:18',
        location: 'Side Entrance',
        status: 'unauthorized'
      }
    ];
    
    setStats(demoStats);
    setUsers(demoUsers);
    setDetections(demoDetections);
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#031834]">
        <div className="text-white text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#031834]">
      {/* Header */}
      <header className="bg-[#1a2a44] border-b border-[#00d9a6]/30 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <FiShield className="text-[#00d9a6] text-2xl" />
            <h1 className="text-2xl font-bold text-white">Secure Pass - Admin</h1>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
          >
            <FiLogOut />
            <span>Logout</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Vehicles</p>
                <p className="text-white text-2xl font-bold">{stats?.totalVehicles || 0}</p>
              </div>
              <FiTruck className="text-[#00d9a6] text-3xl" />
            </div>
          </div>

          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Authorized</p>
                <p className="text-green-400 text-2xl font-bold">{stats?.authorizedVehicles || 0}</p>
              </div>
              <FiShield className="text-green-400 text-3xl" />
            </div>
          </div>

          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Pending</p>
                <p className="text-yellow-400 text-2xl font-bold">{stats?.pendingVehicles || 0}</p>
              </div>
              <FiActivity className="text-yellow-400 text-3xl" />
            </div>
          </div>

          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Users</p>
                <p className="text-blue-400 text-2xl font-bold">{users?.length || 0}</p>
              </div>
              <FiUsers className="text-blue-400 text-3xl" />
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Detections */}
          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <h3 className="text-white text-xl font-semibold mb-4">Recent Detections</h3>
            <div className="space-y-3">
              {detections.map((detection) => (
                <div key={detection.id} className="flex items-center justify-between p-3 bg-[#031834] rounded-lg">
                  <div>
                    <p className="text-white font-medium">{detection.licensePlate}</p>
                    <p className="text-gray-400 text-sm">{detection.location} • {detection.timestamp}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    detection.status === 'authorized' ? 'bg-green-900 text-green-300' :
                    detection.status === 'unauthorized' ? 'bg-red-900 text-red-300' :
                    'bg-yellow-900 text-yellow-300'
                  }`}>
                    {detection.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* User Management */}
          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <h3 className="text-white text-xl font-semibold mb-4">User Management</h3>
            <div className="space-y-3">
              {users.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-3 bg-[#031834] rounded-lg">
                  <div>
                    <p className="text-white font-medium">{user.username}</p>
                    <p className="text-gray-400 text-sm">{user.email}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    user.role === 'admin' ? 'bg-purple-900 text-purple-300' :
                    user.role === 'manager' ? 'bg-blue-900 text-blue-300' :
                    'bg-green-900 text-green-300'
                  }`}>
                    {user.role}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Demo Notice */}
        <div className="mt-8 p-4 bg-blue-900/20 border border-blue-500/30 rounded-xl">
          <h4 className="text-blue-300 font-semibold mb-2">🎯 Demo Mode</h4>
          <p className="text-blue-200 text-sm">
            This is a demonstration version of the Secure Pass system. All data shown is simulated for demo purposes.
            In a real deployment, this would connect to actual databases and camera systems.
          </p>
        </div>
      </main>
    </div>
  );
}

export default AdminDashboard;