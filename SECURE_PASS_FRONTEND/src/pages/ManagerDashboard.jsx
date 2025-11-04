import React from 'react';

function ManagerDashboard() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-2xl space-y-8 rounded-xl bg-[#1a2a44] p-8 shadow-lg border border-[#00d9a6]">
        <h1 className="text-3xl font-bold text-center text-white">Manager Dashboard</h1>
        <p className="text-center text-[#a0a8b7]">
          This is the manager dashboard. Add your manager features here.
        </p>
      </div>
    </div>
  );
}

export default ManagerDashboard;