import React from 'react';

export default function HardwarePage() {
  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-semibold text-white mb-2">Hardware & Nodes</h1>
      <p className="text-gray-400 text-sm mb-6">View status of all connected quantum backends.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#111] border border-[#222] rounded-lg p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-md font-medium text-white">IBM Quantum</h3>
            <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded border border-green-500/20">Online</span>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between border-b border-[#222] pb-2"><span className="text-gray-500">Backend</span><span className="text-gray-300">ibmq_qasm_simulator</span></div>
            <div className="flex justify-between border-b border-[#222] pb-2"><span className="text-gray-500">Qubits</span><span className="text-gray-300">32</span></div>
            <div className="flex justify-between pb-2"><span className="text-gray-500">Current Queue</span><span className="text-gray-300">0 jobs</span></div>
          </div>
        </div>
        
        <div className="bg-[#111] border border-[#222] rounded-lg p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-md font-medium text-white">Local Aer Simulator</h3>
            <span className="px-2 py-1 bg-green-500/10 text-green-400 text-xs rounded border border-green-500/20">Online</span>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between border-b border-[#222] pb-2"><span className="text-gray-500">Backend</span><span className="text-gray-300">aer_simulator</span></div>
            <div className="flex justify-between border-b border-[#222] pb-2"><span className="text-gray-500">Qubits</span><span className="text-gray-300">∞</span></div>
            <div className="flex justify-between pb-2"><span className="text-gray-500">Current Queue</span><span className="text-gray-300">Idle</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
