import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiCamera, FiUpload, FiLogOut, FiShield, FiAlertTriangle, FiCheckCircle, FiClock } from 'react-icons/fi';

function SecurityDashboard() {
  const navigate = useNavigate();
  const [detections, setDetections] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [lastDetection, setLastDetection] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Static demo detections
    const demoDetections = [
      {
        id: 1,
        licensePlate: 'MH12AB1234',
        timestamp: '2024-11-04 10:30:25',
        location: 'Main Gate',
        status: 'authorized',
        confidence: 95.6
      },
      {
        id: 2,
        licensePlate: 'DL05CD5678',
        timestamp: '2024-11-04 09:15:42',
        location: 'Parking Lot A',
        status: 'authorized',
        confidence: 92.3
      },
      {
        id: 3,
        licensePlate: 'XX99ZZ1111',
        timestamp: '2024-11-04 11:45:18',
        location: 'Side Entrance',
        status: 'unauthorized',
        confidence: 88.7
      }
    ];
    
    setDetections(demoDetections);
    setLoading(false);
  }, []);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsProcessing(true);
    setUploadedImage(URL.createObjectURL(file));

    // Simulate processing
    setTimeout(() => {
      // Random demo detection result
      const demoPlates = ['MH12AB1234', 'DL05CD5678', 'KA03EF9012', 'UP16GH3456', 'XX99ZZ1111'];
      const randomPlate = demoPlates[Math.floor(Math.random() * demoPlates.length)];
      const confidence = Math.floor(Math.random() * 20) + 80; // 80-99%
      const status = randomPlate === 'XX99ZZ1111' ? 'unauthorized' : 'authorized';
      
      const detection = {
        id: Date.now(),
        licensePlate: randomPlate,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        location: 'Live Detection',
        status: status,
        confidence: confidence
      };
      
      setLastDetection(detection);
      setDetections(prev => [detection, ...prev.slice(0, 9)]);
      setIsProcessing(false);
    }, 2000);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'authorized': return 'text-green-400 bg-green-900/30';
      case 'unauthorized': return 'text-red-400 bg-red-900/30';
      case 'pending': return 'text-yellow-400 bg-yellow-900/30';
      default: return 'text-gray-400 bg-gray-900/30';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'authorized': return <FiCheckCircle className="text-green-400" />;
      case 'unauthorized': return <FiAlertTriangle className="text-red-400" />;
      case 'pending': return <FiClock className="text-yellow-400" />;
      default: return <FiShield className="text-gray-400" />;
    }
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
            <h1 className="text-2xl font-bold text-white">Secure Pass - Security</h1>
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
        {/* License Plate Scanner */}
        <div className="mb-8">
          <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
            <h3 className="text-white text-xl font-semibold mb-4 flex items-center">
              <FiCamera className="mr-2" />
              License Plate Scanner
            </h3>
            
            {/* Upload Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-[#00d9a6]/50 rounded-lg cursor-pointer bg-[#031834] hover:bg-[#041a37] transition-colors">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <FiUpload className="w-8 h-8 mb-4 text-[#00d9a6]" />
                    <p className="mb-2 text-sm text-gray-300">
                      <span className="font-semibold">Click to upload</span> license plate image
                    </p>
                    <p className="text-xs text-gray-400">PNG, JPG or GIF (MAX. 10MB)</p>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    disabled={isProcessing}
                  />
                </label>

                {uploadedImage && (
                  <div className="mt-4">
                    <img
                      src={uploadedImage}
                      alt="Uploaded"
                      className="w-full h-48 object-cover rounded-lg border border-[#00d9a6]/30"
                    />
                  </div>
                )}
              </div>

              {/* Processing Result */}
              <div className="flex flex-col justify-center">
                {isProcessing ? (
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#00d9a6] mx-auto mb-4"></div>
                    <p className="text-white">Processing license plate...</p>
                  </div>
                ) : lastDetection ? (
                  <div className="bg-[#031834] p-6 rounded-lg border border-[#00d9a6]/30">
                    <h4 className="text-white font-semibold mb-4">Detection Result</h4>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">License Plate:</span>
                        <span className="text-white font-mono text-lg">{lastDetection.licensePlate}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">Confidence:</span>
                        <span className="text-[#00d9a6] font-semibold">{lastDetection.confidence}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">Status:</span>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(lastDetection.status)}
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(lastDetection.status)}`}>
                            {lastDetection.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-400">
                    <FiCamera className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Upload an image to detect license plates</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Detections */}
        <div className="bg-[#1a2a44] p-6 rounded-xl border border-[#00d9a6]/30">
          <h3 className="text-white text-xl font-semibold mb-4">Recent Detections</h3>
          <div className="space-y-3">
            {detections.map((detection) => (
              <div key={detection.id} className="flex items-center justify-between p-4 bg-[#031834] rounded-lg border border-[#00d9a6]/20 hover:border-[#00d9a6]/40 transition-colors">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(detection.status)}
                  <div>
                    <p className="text-white font-mono text-lg">{detection.licensePlate}</p>
                    <p className="text-gray-400 text-sm">{detection.location} • {detection.timestamp}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-[#00d9a6] text-sm font-semibold">{detection.confidence}%</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(detection.status)}`}>
                    {detection.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Demo Notice */}
        <div className="mt-8 p-4 bg-blue-900/20 border border-blue-500/30 rounded-xl">
          <h4 className="text-blue-300 font-semibold mb-2">🎯 Demo Mode</h4>
          <p className="text-blue-200 text-sm">
            This is a demonstration of the license plate recognition system. Upload any image to see how the system would process it.
            In a real deployment, this would connect to live camera feeds and actual vehicle databases.
          </p>
        </div>
      </main>
    </div>
  );
}

export default SecurityDashboard;