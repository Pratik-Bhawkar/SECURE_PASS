import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './pages/AdminDashboard';
import SecurityDashboard from './pages/SecurityDashboard';
import ManagerDashboard from './pages/ManagerDashboard';
import Home from './pages/Home';
import './styles/globals.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#031834]">
        <Routes>
          {/* Landing page should be Home so users see the navigation links immediately */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/security" element={<SecurityDashboard />} />
          <Route path="/manager" element={<ManagerDashboard />} />
          <Route path="/home" element={<Home />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;