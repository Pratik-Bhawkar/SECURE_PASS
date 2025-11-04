import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getApiUrl, API_ENDPOINTS } from '../config/api';
import { FiLogOut, FiMenu, FiX, FiShield, FiCamera, FiCheckCircle, FiXCircle, FiClock } from 'react-icons/fi';
import sciFiLogo from '../assets/sci-fi-logo.png';

const SecurityDashboard = () => {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Real-time data state
  const [recentScans, setRecentScans] = useState([]);
  const [currentScan, setCurrentScan] = useState(null);
  const [stats, setStats] = useState({
    totalScans: 0,
    authorized: 0,
    denied: 0,
    pending: 0
  });



  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    
    fetchData();
    // Set up real-time updates
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, [navigate]);

  const fetchData = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      // Fetch recent scan logs
      const logsResponse = await axios.get(`${getApiUrl(API_ENDPOINTS.LOGS)}/?limit=20`);
      setRecentScans(logsResponse.data);
      
      // Calculate stats
      const logs = logsResponse.data;
      setStats({
        totalScans: logs.length,
        authorized: logs.filter(log => log.authorized).length,
        denied: logs.filter(log => !log.authorized).length,
        pending: 0 // Placeholder for pending scans
      });
      
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to fetch data: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  const getStatusColor = (authorized) => {
    return authorized ? 'text-green-400' : 'text-red-400';
  };

  const getStatusBg = (authorized) => {
    return authorized ? 'bg-green-500/20 border-green-500/30' : 'bg-red-500/20 border-red-500/30';
  };

  const StatCard = ({ title, value, icon: Icon, color = 'emerald', description }) => (
    <div className="bg-gray-800/40 backdrop-blur-md p-6 rounded-xl border border-gray-700/50 hover:border-gray-600/50 transition-all duration-200">
      <div className="flex items-center justify-between mb-2">
        <div className={`p-3 rounded-lg bg-${color}-500/20`}>
          <Icon className={`w-6 h-6 text-${color}-400`} />
        </div>
        <span className="text-2xl font-bold text-white">{value}</span>
      </div>
      <h3 className="text-gray-300 font-medium">{title}</h3>
      {description && <p className="text-gray-400 text-sm mt-1">{description}</p>}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex">
      {/* Mobile menu button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-gray-800/80 backdrop-blur-md text-white hover:bg-gray-700/80 transition-colors"
      >
        {sidebarOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40 w-80 lg:w-72 xl:w-80
        bg-gray-800/20 backdrop-blur-xl border-r border-gray-700/50
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full p-6">
          {/* Logo */}
          <div className="flex items-center justify-center mb-8">
            <img 
              src={sciFiLogo} 
              alt="Secure Pass" 
              className="w-20 h-20 sm:w-24 sm:h-24 animate-pulse hover:animate-spin transition-all duration-500"
            />
          </div>
          
          <div className="text-center mb-8">
            <h2 className="text-xl font-bold text-white">Security Dashboard</h2>
            <p className="text-sm text-gray-400">Live Monitoring</p>
          </div>
          
          {/* Status Indicator */}
          <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-300 font-medium">System Online</span>
            </div>
            <p className="text-green-400/70 text-sm mt-1">All systems operational</p>
          </div>
          
          {/* Quick Actions */}
          <div className="flex-1">
            <h3 className="text-gray-400 text-sm font-medium mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-700/30 hover:text-white transition-all duration-200">
                <FiCamera size={20} />
                <span>Manual Scan</span>
              </button>
              <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-700/30 hover:text-white transition-all duration-200">
                <FiShield size={20} />
                <span>Security Settings</span>
              </button>
            </div>
          </div>
          
          {/* Logout button */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg
                     text-red-300 hover:bg-red-600/20 hover:text-red-200
                     transition-all duration-200 font-medium border border-red-500/20"
          >
            <FiLogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto p-4 sm:p-6 lg:p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2">
              Security Monitoring
            </h1>
            <p className="text-gray-400">
              Real-time license plate recognition and access control
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-300 flex items-center justify-between">
              <span>{error}</span>
              <button onClick={() => setError('')} className="text-red-400 hover:text-red-300">
                <FiX size={16} />
              </button>
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard 
              title="Total Scans Today" 
              value={stats.totalScans} 
              icon={FiCamera} 
              color="blue"
              description="License plates scanned"
            />
            <StatCard 
              title="Authorized Access" 
              value={stats.authorized} 
              icon={FiCheckCircle} 
              color="green"
              description="Approved entries"
            />
            <StatCard 
              title="Denied Access" 
              value={stats.denied} 
              icon={FiXCircle} 
              color="red"
              description="Blocked entries"
            />
            <StatCard 
              title="Pending Review" 
              value={stats.pending} 
              icon={FiClock} 
              color="yellow"
              description="Awaiting approval"
            />
          </div>

          {/* Live Feed Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Camera Feed Placeholder */}
            <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
              <h2 className="text-xl font-semibold text-emerald-400 mb-4 flex items-center">
                <FiCamera className="mr-2" />
                Live Camera Feed
              </h2>
              
              <div className="aspect-video bg-gray-900/50 rounded-lg flex items-center justify-center border border-gray-700/30">
                <div className="text-center">
                  <FiCamera size={48} className="mx-auto mb-4 text-gray-500" />
                  <p className="text-gray-400">Camera feed will appear here</p>
                  <p className="text-gray-500 text-sm">Connect camera to start monitoring</p>
                </div>
              </div>
              
              <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-green-300 text-sm">Camera Active</span>
                </div>
                <div className="text-gray-400 text-sm">
                  Resolution: 1920x1080
                </div>
              </div>
            </div>

            {/* Current Scan Info */}
            <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
              <h2 className="text-xl font-semibold text-emerald-400 mb-4">
                Latest Scan Result
              </h2>
              
              {recentScans.length > 0 ? (
                <div className="space-y-4">
                  {recentScans.slice(0, 1).map((scan) => (
                    <div key={scan.id} className={`p-4 rounded-lg border ${getStatusBg(scan.authorized)}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-mono font-bold text-lg">{scan.plate_number}</span>
                        <span className={`font-medium ${getStatusColor(scan.authorized)}`}>
                          {scan.authorized ? '✓ AUTHORIZED' : '✗ DENIED'}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Confidence:</span>
                          <div className="flex items-center mt-1">
                            <div className="flex-1 bg-gray-700 rounded-full h-2 mr-2">
                              <div 
                                className="bg-emerald-500 h-2 rounded-full" 
                                style={{width: `${Math.min(scan.confidence * 100, 100)}%`}}
                              />
                            </div>
                            <span className="text-white">{(scan.confidence * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                        <div>
                          <span className="text-gray-400">Time:</span>
                          <p className="text-white">{new Date(scan.timestamp).toLocaleTimeString()}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FiShield size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No recent scans</p>
                  <p className="text-sm">Scan results will appear here</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-emerald-400 flex items-center">
                <FiShield className="mr-2" />
                Recent Activity
              </h2>
              <button 
                onClick={fetchData}
                className="px-4 py-2 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 rounded-lg transition-colors text-sm border border-emerald-500/30"
              >
                Refresh
              </button>
            </div>
            
            {recentScans.length > 0 ? (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {recentScans.map((scan) => (
                  <div key={scan.id} className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg hover:bg-gray-700/50 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div className={`w-4 h-4 rounded-full ${scan.authorized ? 'bg-green-500' : 'bg-red-500'}`} />
                      <div>
                        <p className="text-white font-mono font-bold">{scan.plate_number}</p>
                        <p className="text-gray-400 text-sm">
                          {new Date(scan.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className={`font-medium text-sm ${getStatusColor(scan.authorized)}`}>
                          {scan.authorized ? 'AUTHORIZED' : 'DENIED'}
                        </p>
                        <p className="text-gray-400 text-xs">
                          {(scan.confidence * 100).toFixed(1)}% confidence
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <FiClock size={48} className="mx-auto mb-4 opacity-50" />
                <p>No activity recorded</p>
                <p className="text-sm">License plate scans will appear here in real-time</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default SecurityDashboard;