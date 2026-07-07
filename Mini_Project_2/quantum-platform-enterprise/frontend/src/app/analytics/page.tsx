import React from 'react';

export default function AnalyticsPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-semibold text-white mb-2">Telemetry & Logs</h1>
      <p className="text-gray-400 text-sm mb-6">System logs and detailed metrics.</p>
      <div className="bg-[#111] border border-[#222] rounded-lg p-5 font-mono text-xs text-gray-400">
        <div className="flex gap-4 border-b border-[#222] pb-2 mb-2"><span className="text-green-500">[INFO]</span><span>2026-07-07 18:00:01</span><span className="text-gray-300">System initialization complete</span></div>
        <div className="flex gap-4 border-b border-[#222] pb-2 mb-2"><span className="text-green-500">[INFO]</span><span>2026-07-07 18:00:05</span><span className="text-gray-300">Connected to IBM Quantum Provider</span></div>
        <div className="flex gap-4 border-b border-[#222] pb-2 mb-2"><span className="text-yellow-500">[WARN]</span><span>2026-07-07 18:02:14</span><span className="text-gray-300">Queue latency elevated on provider Aer Simulator</span></div>
        <div className="flex gap-4 border-b border-[#222] pb-2 mb-2"><span className="text-green-500">[INFO]</span><span>2026-07-07 18:05:22</span><span className="text-gray-300">Experiment Grover Search completed successfully</span></div>
      </div>
    </div>
  );
}
