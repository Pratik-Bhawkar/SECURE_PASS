import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiLogOut, FiShield, FiUsers, FiTruck, FiPlus, FiEdit, FiTrash } from 'react-icons/fi';

function ManagerDashboard() {
  const navigate = useNavigate();
  const [vehicles, setVehicles] = useState([
    { id: 1, licensePlate: 'MH12AB1234', ownerName: 'John Doe', status: 'authorized' },
    { id: 2, licensePlate: 'DL05CD5678', ownerName: 'Jane Smith', status: 'pending' },
    { id: 3, licensePlate: 'KA03EF9012', ownerName: 'Mike Wilson', status: 'rejected' }
  ]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  const updateVehicleStatus = (id, newStatus) => {
    setVehicles(vehicles.map(v => 
      v.id === id ? { ...v, status: newStatus } : v
    ));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'authorized': return 'text-green-400 bg-green-900/30';
      case 'rejected': return 'text-red-400 bg-red-900/30';
      case 'pending': return 'text-yellow-400 bg-yellow-900/30';
      default: return 'text-gray-400 bg-gray-900/30';
    }
  };

  return (
    <div className="min-h-screen bg-[#031834]">
      {/* Header */}
      <header className="bg-[#1a2a44] border-b border-[#00d9a6]/30 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <FiShield className="text-[#00d9a6] text-2xl" />
            <h1 className="text-2xl font-bold text-white">Secure Pass - Manager</h1>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Vehicles</p>
                <p className="text-white text-2xl font-bold">{vehicles.length}</p>
              </div>
              <FiTruck className="text-[#00d9a6] text-3xl" />
            </div>
          </div>

          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Authorized</p>
                <p className="text-green-400 text-2xl font-bold">
                  {vehicles.filter(v => v.status === 'authorized').length}
                </p>
              </div>
              <FiShield className="text-green-400 text-3xl" />
            </div>
          </div>

          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Pending</p>
                <p className="text-yellow-400 text-2xl font-bold">
                  {vehicles.filter(v => v.status === 'pending').length}
                </p>
              </div>
              <FiUsers className="text-yellow-400 text-3xl" />
            </div>
          </div>
        </div>

        {/* Vehicle Management */}
        <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-white text-xl font-semibold">Vehicle Management</h3>
            <button className="flex items-center space-x-2 px-4 py-2 bg-[#00d9a6] hover:bg-[#00c491] text-white rounded-lg transition-colors">
              <FiPlus />
              <span>Add Vehicle</span>
            </button>
          </div>

          <div className="space-y-4">
            {vehicles.map((vehicle) => (
              <div key={vehicle.id} className="flex items-center justify-between p-4 bg-[#031834] rounded-lg border border-[#00d9a6]/20">
                <div>
                  <p className="text-white font-mono text-lg">{vehicle.licensePlate}</p>
                  <p className="text-gray-400 text-sm">Owner: {vehicle.ownerName}</p>
                </div>
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(vehicle.status)}`}>
                    {vehicle.status}
                  </span>
                  <div className="flex space-x-2">
                    {vehicle.status === 'pending' && (
                      <>
                        <button
                          onClick={() => updateVehicleStatus(vehicle.id, 'authorized')}
                          className="px-3 py-1 bg-green-600 hover:bg-green-500 text-white rounded text-sm transition-colors"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => updateVehicleStatus(vehicle.id, 'rejected')}
                          className="px-3 py-1 bg-red-600 hover:bg-red-500 text-white rounded text-sm transition-colors"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    <button className="p-2 text-gray-400 hover:text-white transition-colors">
                      <FiEdit />
                    </button>
                    <button className="p-2 text-red-400 hover:text-red-300 transition-colors">
                      <FiTrash />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Demo Notice */}
        <div className="mt-8 p-4 bg-blue-900/20 border border-blue-500/30 rounded-xl">
          <h4 className="text-blue-300 font-semibold mb-2">🎯 Demo Mode</h4>
          <p className="text-blue-200 text-sm">
            This is the Manager Dashboard demo. You can approve/reject pending vehicles and manage the vehicle database.
            All data is simulated for demonstration purposes.
          </p>
        </div>
      </main>
    </div>
  );
}

export default ManagerDashboard;