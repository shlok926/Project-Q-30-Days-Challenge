import React from 'react';

export default function SettingsPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-semibold text-white mb-2">Settings</h1>
      <p className="text-gray-400 text-sm mb-6">Manage platform configuration.</p>
      
      <div className="bg-[#111] border border-[#222] rounded-lg p-6 max-w-2xl">
        <h3 className="text-md font-medium text-white mb-4">API Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="text-xs text-gray-400 block mb-1">IBM Quantum API Token</label>
            <input type="password" value="*************************" disabled className="w-full bg-[#1A1A1A] border border-[#333] rounded-md px-3 py-2 text-sm text-gray-500"/>
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Default Provider</label>
            <select className="w-full bg-[#1A1A1A] border border-[#333] rounded-md px-3 py-2 text-sm text-white">
              <option>Aer Simulator (Local)</option>
              <option>IBM Quantum</option>
            </select>
          </div>
          <button className="bg-white text-black px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 mt-2">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
