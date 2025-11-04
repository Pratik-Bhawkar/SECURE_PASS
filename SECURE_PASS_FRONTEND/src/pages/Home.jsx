import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // Add login logic here
    if (username === 'admin') navigate('/admin');
    else if (username === 'manager') navigate('/manager');
    else if (username === 'security') navigate('/security');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#031834]">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-[#1a2a44] p-8 shadow-lg border border-[#00d9a6]">
        <h1 className="text-3xl font-bold text-center text-white">Secure Pass Home</h1>
        <p className="text-center text-[#a0a8b7]">
          Welcome to the Secure Pass system. Use the navigation to access dashboards.
        </p>
        <div className="mt-8 p-4 bg-[#0a1931] rounded-lg border border-blue-900">
          <h3 className="text-blue-200 font-semibold mb-2">Demo Credentials:</h3>
          <div className="space-y-1 text-sm text-blue-100">
            <p><span className="font-bold text-white">Admin:</span> admin / admin123</p>
            <p><span className="font-bold text-white">Manager:</span> manager / manager123</p>
            <p><span className="font-bold text-white">Security:</span> security / security123</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;