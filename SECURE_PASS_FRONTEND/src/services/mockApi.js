import { mockUsers, mockVehicles, mockDetections, mockLogs, mockStats } from './mockData.js';

// Simulate network delay
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

// Mock authentication
let currentUser = null;
let authToken = null;

export const mockApi = {
  // Authentication
  async login(credentials) {
    await delay(800);
    
    // Demo credentials
    const validCredentials = [
      { username: 'admin', password: 'admin123', role: 'admin' },
      { username: 'manager', password: 'manager123', role: 'manager' },
      { username: 'security', password: 'security123', role: 'security' }
    ];

    const user = validCredentials.find(u => 
      u.username === credentials.username && u.password === credentials.password
    );

    if (user) {
      currentUser = { id: Date.now(), ...user };
      authToken = `mock-token-${Date.now()}`;
      
      // Store in localStorage for persistence
      localStorage.setItem('token', authToken);
      localStorage.setItem('user', JSON.stringify(currentUser));
      localStorage.setItem('role', user.role);
      
      return {
        success: true,
        user: currentUser,
        token: authToken,
        role: user.role
      };
    } else {
      throw new Error('Invalid credentials');
    }
  },

  async logout() {
    await delay(200);
    currentUser = null;
    authToken = null;
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('role');
    
    return { success: true };
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  getCurrentRole() {
    return localStorage.getItem('role') || null;
  },

  // Vehicles
  async getVehicles() {
    await delay();
    return [...mockVehicles];
  },

  async addVehicle(vehicleData) {
    await delay(800);
    const newVehicle = {
      id: Date.now(),
      ...vehicleData,
      status: 'pending',
      registeredDate: new Date().toISOString().split('T')[0],
      lastSeen: 'Never'
    };
    mockVehicles.push(newVehicle);
    return newVehicle;
  },

  async updateVehicle(id, updates) {
    await delay(600);
    const vehicleIndex = mockVehicles.findIndex(v => v.id === id);
    if (vehicleIndex !== -1) {
      mockVehicles[vehicleIndex] = { ...mockVehicles[vehicleIndex], ...updates };
      return mockVehicles[vehicleIndex];
    }
    throw new Error('Vehicle not found');
  },

  async deleteVehicle(id) {
    await delay(400);
    const vehicleIndex = mockVehicles.findIndex(v => v.id === id);
    if (vehicleIndex !== -1) {
      const deleted = mockVehicles.splice(vehicleIndex, 1)[0];
      return deleted;
    }
    throw new Error('Vehicle not found');
  },

  // Detections
  async getDetections() {
    await delay();
    return [...mockDetections];
  },

  async processPlate(imageFile) {
    await delay(1500); // Simulate OCR processing time
    
    // Simulate different outcomes
    const outcomes = [
      { plate: 'MH12AB1234', confidence: 95.6, status: 'authorized' },
      { plate: 'DL05CD5678', confidence: 92.3, status: 'authorized' },
      { plate: 'XX99ZZ1111', confidence: 88.7, status: 'unauthorized' },
      { plate: 'KA03EF9012', confidence: 91.2, status: 'pending' },
      { plate: 'UP16GH3456', confidence: 89.5, status: 'rejected' }
    ];
    
    const randomOutcome = outcomes[Math.floor(Math.random() * outcomes.length)];
    
    const detection = {
      id: Date.now(),
      licensePlate: randomOutcome.plate,
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      location: 'Live Detection',
      status: randomOutcome.status,
      confidence: randomOutcome.confidence,
      imageUrl: URL.createObjectURL(imageFile)
    };
    
    mockDetections.unshift(detection);
    return detection;
  },

  // Logs
  async getLogs() {
    await delay();
    return [...mockLogs];
  },

  // Statistics
  async getStats() {
    await delay();
    return {
      ...mockStats,
      totalVehicles: mockVehicles.length,
      authorizedVehicles: mockVehicles.filter(v => v.status === 'authorized').length,
      pendingVehicles: mockVehicles.filter(v => v.status === 'pending').length,
      rejectedVehicles: mockVehicles.filter(v => v.status === 'rejected').length,
      todayDetections: mockDetections.filter(d => d.timestamp.startsWith(new Date().toISOString().split('T')[0])).length
    };
  },

  // Users (Admin only)
  async getUsers() {
    await delay();
    return [...mockUsers];
  },

  async addUser(userData) {
    await delay(600);
    const newUser = {
      id: Date.now(),
      ...userData
    };
    mockUsers.push(newUser);
    return newUser;
  },

  async updateUser(id, updates) {
    await delay(500);
    const userIndex = mockUsers.findIndex(u => u.id === id);
    if (userIndex !== -1) {
      mockUsers[userIndex] = { ...mockUsers[userIndex], ...updates };
      return mockUsers[userIndex];
    }
    throw new Error('User not found');
  },

  async deleteUser(id) {
    await delay(400);
    const userIndex = mockUsers.findIndex(u => u.id === id);
    if (userIndex !== -1) {
      const deleted = mockUsers.splice(userIndex, 1)[0];
      return deleted;
    }
    throw new Error('User not found');
  }
};

export default mockApi;