import React from 'react';
import { Settings, Shield, Bell, HardDrive, Cpu } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-semibold text-white mb-1">Platform Settings</h1>
        <p className="text-gray-400 text-sm">Manage configuration, integrations, and preferences.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        
        {/* Settings Navigation */}
        <div className="col-span-1 space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium bg-[#1A1A1A] text-white rounded-md border border-[#333]">
            <Cpu className="w-4 h-4" /> Provider APIs
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-[#111] rounded-md transition-colors">
            <HardDrive className="w-4 h-4" /> Data Retention
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-[#111] rounded-md transition-colors">
            <Bell className="w-4 h-4" /> Notifications
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-[#111] rounded-md transition-colors">
            <Shield className="w-4 h-4" /> Security & Access
          </button>
        </div>

        {/* Settings Content */}
        <div className="col-span-3 space-y-6">
          
          {/* Section 1: Provider */}
          <div className="bg-[#111] border border-[#222] rounded-lg p-6">
            <h3 className="text-md font-medium text-white mb-4">Quantum Provider Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 block mb-1">IBM Quantum API Token</label>
                <input type="password" value="*************************" disabled className="w-full bg-[#1A1A1A] border border-[#333] rounded-md px-3 py-2 text-sm text-gray-500"/>
                <p className="text-[10px] text-gray-500 mt-1">Stored securely in HashiCorp Vault. Contact admin to rotate.</p>
              </div>
              <div>
                <label className="text-xs text-gray-400 block mb-1">Default Execution Target</label>
                <select className="w-full bg-[#1A1A1A] border border-[#333] rounded-md px-3 py-2 text-sm text-white">
                  <option>Aer Simulator (Local - Free)</option>
                  <option>IBM Quantum (Production QPU)</option>
                  <option>IonQ Aria (Priority Queue)</option>
                </select>
              </div>
              <div className="flex items-center justify-between pt-2">
                <span className="text-sm text-gray-300">Enable Auto-Failover to Simulator</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-9 h-5 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Section 2: Telemetry */}
          <div className="bg-[#111] border border-[#222] rounded-lg p-6">
            <h3 className="text-md font-medium text-white mb-4">Telemetry & Diagnostics</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-gray-400 block mb-1">Data Retention Period (Days)</label>
                <input type="number" defaultValue={30} className="w-full bg-[#1A1A1A] border border-[#333] rounded-md px-3 py-2 text-sm text-white"/>
              </div>
              <div className="flex items-center justify-between pt-2">
                <span className="text-sm text-gray-300">Detailed Execution Tracing</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-9 h-5 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <button className="px-4 py-2 bg-[#1A1A1A] text-gray-300 rounded-md text-sm font-medium hover:bg-[#222] transition-colors border border-[#333]">
              Cancel
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-500 shadow-[0_0_15px_rgba(37,99,235,0.2)] transition-colors">
              Save Changes
            </button>
          </div>
          
        </div>
      </div>
    </div>
  );
}
