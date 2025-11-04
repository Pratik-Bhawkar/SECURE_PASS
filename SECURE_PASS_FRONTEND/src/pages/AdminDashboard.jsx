import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FiLogOut, FiTrash2, FiPlus, FiUsers, FiShield, FiSettings, FiMenu, FiX, FiEye, FiTruck } from 'react-icons/fi';
import { getApiUrl, API_ENDPOINTS } from '../config/api';
import sciFiLogo from '../assets/sci-fi-logo.png';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Data state
  const [logs, setLogs] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Form state
  const [formData, setFormData] = useState({
    plate_number: '',
    owner_name: '',
    vehicle_type: '',
  });
  const [formError, setFormError] = useState('');



  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [navigate]);

  const fetchData = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    try {
      // Fetch all data in parallel
      const [logsRes, vehiclesRes, photosRes] = await Promise.all([
        axios.get(`${getApiUrl(API_ENDPOINTS.LOGS)}/?limit=10`).catch(() => ({ data: [] })),
        axios.get(getApiUrl(API_ENDPOINTS.VEHICLES), { headers }).catch(() => ({ data: [] })),
        axios.get(`${getApiUrl(API_ENDPOINTS.PHOTOS)}/`, { headers }).catch(() => ({ data: [] }))
      ]);

      setLogs(logsRes.data);
      setVehicles(vehiclesRes.data);
      setPhotos(photosRes.data);
    } catch (err) {
      setError('Failed to fetch data: ' + (err.response?.data?.detail || err.message));
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setFormError(''); // Clear form error when user types
  };

  const validatePlate = (plate) => {
    const regex = /^[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{1,4}$|^[A-Z]{2}\d{3,5}$/;
    return regex.test(plate.toUpperCase());
  };

  const handleAddVehicle = async (e) => {
    e.preventDefault();
    setFormError('');
    setError('');

    const token = localStorage.getItem('token');
    if (!token) {
      setError('Please log in to add vehicles');
      navigate('/login');
      return;
    }

    if (!validatePlate(formData.plate_number)) {
      setFormError('Invalid plate format. Use formats like MH12MB8677, GJ01XY1234, or JK12345.');
      return;
    }

    setLoading(true);
    try {
      await axios.post(getApiUrl(API_ENDPOINTS.VEHICLES), {
        ...formData,
        plate_number: formData.plate_number.toUpperCase()
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setFormData({ plate_number: '', owner_name: '', vehicle_type: '' });
      fetchData(); // Refresh data
    } catch (err) {
      setError('Failed to add vehicle: ' + (err.response?.data?.detail || err.message));
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteVehicle = async (plate_number) => {
    if (!window.confirm(`Are you sure you want to delete vehicle ${plate_number}?`)) return;

    const token = localStorage.getItem('token');
    setLoading(true);
    try {
      await axios.delete(`${getApiUrl(API_ENDPOINTS.VEHICLES)}/${plate_number}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData(); // Refresh data
    } catch (err) {
      setError('Failed to delete vehicle: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  const menuItems = [
    { id: 'overview', label: 'Overview', icon: FiUsers },
    { id: 'vehicles', label: 'Vehicles', icon: FiTruck },
    { id: 'logs', label: 'Access Logs', icon: FiShield },
    { id: 'photos', label: 'Photos', icon: FiEye },
  ];

  const StatCard = ({ title, value, icon: Icon, color = 'emerald' }) => (
    <div className="bg-gray-800/40 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg bg-${color}-500/20`}>
          <Icon className={`w-6 h-6 text-${color}-400`} />
        </div>
      </div>
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
            <h2 className="text-xl font-bold text-white">Admin Dashboard</h2>
            <p className="text-sm text-gray-400">System Management</p>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setSidebarOpen(false);
                  }}
                  className={`
                    w-full flex items-center space-x-3 px-4 py-3 rounded-lg
                    transition-all duration-200 font-medium text-left
                    ${activeTab === item.id 
                      ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 shadow-lg' 
                      : 'text-gray-300 hover:bg-gray-700/30 hover:text-white'
                    }
                  `}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
          
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
              {menuItems.find(item => item.id === activeTab)?.label || 'Dashboard'}
            </h1>
            <p className="text-gray-400">
              Manage your secure pass system
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

          {/* Loading Indicator */}
          {loading && (
            <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-300 flex items-center">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mr-3" />
              Loading...
            </div>
          )}

          {/* Content Sections */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard 
                  title="Total Vehicles" 
                  value={vehicles.length} 
                  icon={FiTruck} 
                  color="emerald" 
                />
                <StatCard 
                  title="Recent Logs" 
                  value={logs.length} 
                  icon={FiShield} 
                  color="blue" 
                />
                <StatCard 
                  title="Photos" 
                  value={photos.length} 
                  icon={FiEye} 
                  color="purple" 
                />
                <StatCard 
                  title="Authorized Today" 
                  value={logs.filter(log => log.authorized).length} 
                  icon={FiUsers} 
                  color="green" 
                />
              </div>

              {/* Recent Activity */}
              <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
                <h3 className="text-xl font-semibold text-emerald-400 mb-4">Recent Activity</h3>
                {logs.slice(0, 5).length > 0 ? (
                  <div className="space-y-3">
                    {logs.slice(0, 5).map((log) => (
                      <div key={log.id} className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${log.authorized ? 'bg-green-500' : 'bg-red-500'}`} />
                          <span className="text-white font-medium">{log.plate_number}</span>
                          <span className="text-gray-400 text-sm">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          log.authorized ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
                        }`}>
                          {log.authorized ? 'Authorized' : 'Denied'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400">No recent activity</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'vehicles' && (
            <div className="space-y-6">
              {/* Add Vehicle Form */}
              <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
                <h2 className="text-xl font-semibold text-emerald-400 mb-4 flex items-center">
                  <FiPlus className="mr-2" />
                  Add Authorized Vehicle
                </h2>
                
                {formError && (
                  <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-300 text-sm">
                    {formError}
                  </div>
                )}
                
                <form onSubmit={handleAddVehicle} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <input
                      type="text"
                      name="plate_number"
                      placeholder="Plate Number (e.g., MH12MB8677)"
                      value={formData.plate_number}
                      onChange={handleInputChange}
                      className="px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg
                               text-white placeholder-gray-400 focus:outline-none 
                               focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20
                               transition-all duration-200 uppercase"
                      required
                    />
                    
                    <input
                      type="text"
                      name="owner_name"
                      placeholder="Owner Name"
                      value={formData.owner_name}
                      onChange={handleInputChange}
                      className="px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg
                               text-white placeholder-gray-400 focus:outline-none 
                               focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20
                               transition-all duration-200"
                      required
                    />
                    
                    <select
                      name="vehicle_type"
                      value={formData.vehicle_type}
                      onChange={handleInputChange}
                      className="px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg
                               text-white focus:outline-none focus:border-emerald-500 
                               focus:ring-2 focus:ring-emerald-500/20 transition-all duration-200"
                      required
                    >
                      <option value="">Select Vehicle Type</option>
                      <option value="Car">Car</option>
                      <option value="Motorcycle">Motorcycle</option>
                      <option value="Truck">Truck</option>
                      <option value="Bus">Bus</option>
                      <option value="Van">Van</option>
                    </select>
                  </div>
                  
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-emerald-600 to-emerald-500
                             hover:from-emerald-500 hover:to-emerald-400 disabled:from-gray-600 
                             disabled:to-gray-500 text-white font-medium rounded-lg
                             transition-all duration-200 flex items-center justify-center"
                  >
                    {loading ? (
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <FiPlus className="mr-2" />
                        Add Vehicle
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Vehicles List */}
              <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
                <h2 className="text-xl font-semibold text-emerald-400 mb-4 flex items-center">
                  <FiTruck className="mr-2" />
                  Authorized Vehicles ({vehicles.length})
                </h2>
                
                {vehicles.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-700/50">
                          <th className="text-left py-3 px-2 text-gray-300 font-medium">Plate Number</th>
                          <th className="text-left py-3 px-2 text-gray-300 font-medium">Owner</th>
                          <th className="text-left py-3 px-2 text-gray-300 font-medium">Type</th>
                          <th className="text-left py-3 px-2 text-gray-300 font-medium">Added</th>
                          <th className="text-center py-3 px-2 text-gray-300 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {vehicles.map((vehicle) => (
                          <tr key={vehicle.plate_number} className="border-b border-gray-700/30 hover:bg-gray-700/20 transition-colors">
                            <td className="py-4 px-2 text-white font-mono font-bold">{vehicle.plate_number}</td>
                            <td className="py-4 px-2 text-gray-300">{vehicle.owner_name}</td>
                            <td className="py-4 px-2">
                              <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-sm">
                                {vehicle.vehicle_type}
                              </span>
                            </td>
                            <td className="py-4 px-2 text-gray-400 text-sm">
                              {new Date(vehicle.added_at).toLocaleDateString()}
                            </td>
                            <td className="py-4 px-2 text-center">
                              <button
                                onClick={() => handleDeleteVehicle(vehicle.plate_number)}
                                className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/20 
                                         rounded-lg transition-all duration-200"
                                title="Delete Vehicle"
                              >
                                <FiTrash2 size={16} />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <FiTruck size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No authorized vehicles found.</p>
                    <p className="text-sm">Add your first vehicle using the form above.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
              <h2 className="text-xl font-semibold text-emerald-400 mb-4 flex items-center">
                <FiShield className="mr-2" />
                Access Logs ({logs.length})
              </h2>
              
              {logs.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-700/50">
                        <th className="text-left py-3 px-2 text-gray-300 font-medium">Plate Number</th>
                        <th className="text-left py-3 px-2 text-gray-300 font-medium">Timestamp</th>
                        <th className="text-left py-3 px-2 text-gray-300 font-medium">Confidence</th>
                        <th className="text-center py-3 px-2 text-gray-300 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {logs.map((log) => (
                        <tr key={log.id} className="border-b border-gray-700/30 hover:bg-gray-700/20 transition-colors">
                          <td className="py-4 px-2 text-white font-mono font-bold">{log.plate_number}</td>
                          <td className="py-4 px-2 text-gray-300 text-sm">
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td className="py-4 px-2 text-gray-300">
                            <div className="flex items-center">
                              <div className="w-16 bg-gray-700 rounded-full h-2 mr-2">
                                <div 
                                  className="bg-emerald-500 h-2 rounded-full" 
                                  style={{width: `${Math.min(log.confidence * 100, 100)}%`}}
                                />
                              </div>
                              <span className="text-sm">{(log.confidence * 100).toFixed(1)}%</span>
                            </div>
                          </td>
                          <td className="py-4 px-2 text-center">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                              log.authorized 
                                ? 'bg-green-500/20 text-green-300' 
                                : 'bg-red-500/20 text-red-300'
                            }`}>
                              {log.authorized ? '✓ Authorized' : '✗ Denied'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FiShield size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No access logs available.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'photos' && (
            <div className="bg-gray-800/30 backdrop-blur-md p-6 rounded-xl border border-gray-700/50">
              <h2 className="text-xl font-semibold text-emerald-400 mb-4 flex items-center">
                <FiEye className="mr-2" />
                Captured Photos ({photos.length})
              </h2>
              
              {photos.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {photos.map((photo) => (
                    <div key={photo.id} className="bg-gray-700/30 rounded-lg overflow-hidden">
                      <img
                        src={`data:image/jpeg;base64,${photo.image_data}`}
                        alt={photo.plate_number}
                        className="w-full h-48 object-cover"
                      />
                      <div className="p-4">
                        <p className="text-white font-mono font-bold">{photo.plate_number}</p>
                        <p className="text-gray-400 text-sm">
                          {new Date(photo.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <FiEye size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No photos available.</p>
                  <p className="text-sm">Photos will appear here when the system captures license plates.</p>
                </div>
              )}
            </div>
          )}
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

export default AdminDashboard;