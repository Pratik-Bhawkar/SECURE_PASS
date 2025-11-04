// Mock data for demo purposes

export const mockUsers = [
  { id: 1, username: 'admin', email: 'admin@securepass.com', role: 'admin' },
  { id: 2, username: 'manager1', email: 'manager@securepass.com', role: 'manager' },
  { id: 3, username: 'security1', email: 'security@securepass.com', role: 'security' }
];

export const mockVehicles = [
  {
    id: 1,
    licensePlate: 'MH12AB1234',
    ownerName: 'John Doe',
    vehicleType: 'Car',
    status: 'authorized',
    registeredDate: '2023-01-15',
    lastSeen: '2024-11-04 10:30'
  },
  {
    id: 2,
    licensePlate: 'DL05CD5678',
    ownerName: 'Jane Smith',
    vehicleType: 'Motorcycle',
    status: 'authorized',
    registeredDate: '2023-03-20',
    lastSeen: '2024-11-04 09:15'
  },
  {
    id: 3,
    licensePlate: 'KA03EF9012',
    ownerName: 'Mike Wilson',
    vehicleType: 'Car',
    status: 'pending',
    registeredDate: '2024-11-03',
    lastSeen: '2024-11-04 11:45'
  },
  {
    id: 4,
    licensePlate: 'UP16GH3456',
    ownerName: 'Sarah Johnson',
    vehicleType: 'SUV',
    status: 'rejected',
    registeredDate: '2024-10-28',
    lastSeen: '2024-11-02 16:20'
  },
  {
    id: 5,
    licensePlate: 'TN09IJ7890',
    ownerName: 'David Brown',
    vehicleType: 'Truck',
    status: 'authorized',
    registeredDate: '2023-08-12',
    lastSeen: '2024-11-04 08:00'
  }
];

export const mockDetections = [
  {
    id: 1,
    licensePlate: 'MH12AB1234',
    timestamp: '2024-11-04 10:30:25',
    location: 'Main Gate',
    status: 'authorized',
    confidence: 95.6,
    imageUrl: '/demo-images/plate1.jpg'
  },
  {
    id: 2,
    licensePlate: 'DL05CD5678',
    timestamp: '2024-11-04 09:15:42',
    location: 'Parking Lot A',
    status: 'authorized',
    confidence: 92.3,
    imageUrl: '/demo-images/plate2.jpg'
  },
  {
    id: 3,
    licensePlate: 'XX99ZZ1111',
    timestamp: '2024-11-04 11:45:18',
    location: 'Side Entrance',
    status: 'unauthorized',
    confidence: 88.7,
    imageUrl: '/demo-images/plate3.jpg'
  },
  {
    id: 4,
    licensePlate: 'KA03EF9012',
    timestamp: '2024-11-04 11:45:55',
    location: 'Main Gate',
    status: 'pending',
    confidence: 91.2,
    imageUrl: '/demo-images/plate4.jpg'
  },
  {
    id: 5,
    licensePlate: 'TN09IJ7890',
    timestamp: '2024-11-04 08:00:33',
    location: 'Loading Dock',
    status: 'authorized',
    confidence: 96.8,
    imageUrl: '/demo-images/plate5.jpg'
  }
];

export const mockLogs = [
  {
    id: 1,
    action: 'Vehicle Entry',
    licensePlate: 'MH12AB1234',
    user: 'System',
    timestamp: '2024-11-04 10:30:25',
    details: 'Authorized vehicle entered through Main Gate'
  },
  {
    id: 2,
    action: 'Manual Override',
    licensePlate: 'DL05CD5678',
    user: 'security1',
    timestamp: '2024-11-04 09:15:42',
    details: 'Security officer manually approved entry'
  },
  {
    id: 3,
    action: 'Access Denied',
    licensePlate: 'XX99ZZ1111',
    user: 'System',
    timestamp: '2024-11-04 11:45:18',
    details: 'Unauthorized vehicle blocked at Side Entrance'
  },
  {
    id: 4,
    action: 'Vehicle Registration',
    licensePlate: 'KA03EF9012',
    user: 'manager1',
    timestamp: '2024-11-03 14:22:10',
    details: 'New vehicle registered by manager'
  },
  {
    id: 5,
    action: 'Status Update',
    licensePlate: 'UP16GH3456',
    user: 'admin',
    timestamp: '2024-11-02 16:20:45',
    details: 'Vehicle status changed to rejected'
  }
];

export const mockStats = {
  totalVehicles: mockVehicles.length,
  authorizedVehicles: mockVehicles.filter(v => v.status === 'authorized').length,
  pendingVehicles: mockVehicles.filter(v => v.status === 'pending').length,
  rejectedVehicles: mockVehicles.filter(v => v.status === 'rejected').length,
  todayDetections: mockDetections.filter(d => d.timestamp.startsWith('2024-11-04')).length,
  successfulEntries: mockDetections.filter(d => d.status === 'authorized' && d.timestamp.startsWith('2024-11-04')).length,
  deniedEntries: mockDetections.filter(d => d.status === 'unauthorized' && d.timestamp.startsWith('2024-11-04')).length
};