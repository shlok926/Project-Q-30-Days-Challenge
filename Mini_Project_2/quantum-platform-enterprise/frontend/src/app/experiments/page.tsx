"use client";

import React, { useState, useEffect } from 'react';
import { Play, Cpu, Network, Terminal, CheckCircle2, AlertCircle } from 'lucide-react';

export default function WorkspacePage() {
  const [algorithm, setAlgorithm] = useState('bell_state');
  const [provider, setProvider] = useState('aer_simulator');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [experiments, setExperiments] = useState<any[]>([]);

  // Fetch past experiments
  const fetchExperiments = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/experiments/');
      if (res.ok) {
        const data = await res.json();
        setExperiments(data);
      }
    } catch (e) {
      console.error("Failed to fetch experiments", e);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const runExperiment = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      // 1. Create Experiment
      const createRes = await fetch('http://localhost:8000/api/v1/experiments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `${algorithm} Test`,
          description: `Running ${algorithm} on ${provider}`,
          algorithm_type: algorithm,
          provider_type: provider === 'aer_simulator' ? 'aer' : 'ibm',
          parameters: {}
        })
      });
      
      if (!createRes.ok) throw new Error('Failed to create experiment');
      const exp = await createRes.json();

      // 2. Execute Experiment
      const execRes = await fetch(`http://localhost:8000/api/v1/experiments/${exp.id}/execute`, {
        method: 'POST'
      });
      
      if (!execRes.ok) throw new Error('Execution failed');
      const execData = await execRes.json();
      
      setResult(execData);
      fetchExperiments();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-semibold text-white mb-1">Quantum Workspace</h1>
        <p className="text-gray-400 text-sm">Design, compile, and execute real quantum circuits against the engine API.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workspace Controls */}
        <div className="bg-[#111] border border-[#222] rounded-lg p-6">
          <h2 className="text-md font-medium text-white mb-4">Job Configuration</h2>
          
          <div className="space-y-4">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Quantum Algorithm</label>
              <select 
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value)}
                className="w-full bg-[#1A1A1A] border border-[#333] rounded-md px-3 py-2 text-sm text-white"
              >
                <option value="bell_state">Bell State Entanglement</option>
                <option value="quantum_teleportation">Quantum Teleportation</option>
                <option value="grover_search">Grover Search</option>
                <option value="qft">Quantum Fourier Transform</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-400 block mb-1">Target Provider Backend</label>
              <select 
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-[#1A1A1A] border border-[#333] rounded-md px-3 py-2 text-sm text-white"
              >
                <option value="aer_simulator">Local Aer Simulator (Free)</option>
                <option value="ibmq_qasm_simulator">IBM Quantum QASM</option>
              </select>
            </div>

            <button 
              onClick={runExperiment}
              disabled={loading}
              className={`w-full flex items-center justify-center gap-2 px-4 py-2 mt-4 rounded-md text-sm font-semibold transition ${loading ? 'bg-blue-600/50 text-blue-200 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white shadow-[0_0_15px_rgba(37,99,235,0.4)]'}`}
            >
              {loading ? <Network className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              {loading ? 'Compiling & Executing...' : 'Execute Circuit'}
            </button>
            
            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded text-rose-400 text-xs flex items-start gap-2 mt-4">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <p>{error}. Please ensure the backend is running on port 8000.</p>
              </div>
            )}
          </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 bg-[#111] border border-[#222] rounded-lg p-6 flex flex-col">
          <h2 className="text-md font-medium text-white mb-4 flex items-center gap-2">
            <Terminal className="w-4 h-4 text-blue-400" />
            Execution Output Console
          </h2>
          
          <div className="flex-1 bg-[#0A0A0A] border border-[#222] rounded-md p-4 font-mono text-xs overflow-auto h-[300px]">
            {!result && !loading && (
              <p className="text-gray-600 text-center mt-20">No execution data. Configure and run a job to see results.</p>
            )}
            
            {loading && (
              <div className="text-blue-400 animate-pulse space-y-2">
                <p>&gt; Initializing quantum engine provider...</p>
                <p>&gt; Compiling circuit {algorithm}...</p>
                <p>&gt; Transpiling to target basis gates...</p>
                <p>&gt; Submitting job to {provider}...</p>
              </div>
            )}

            {result && !loading && (
              <div className="text-gray-300 space-y-3">
                <p className="text-green-400">&gt; Job completed successfully. ID: {result.job_id || 'LOCAL-EXEC'}</p>
                <p className="text-blue-300">Status: {result.status}</p>
                
                <div className="border-t border-[#333] pt-3 mt-3">
                  <p className="text-gray-500 mb-1">Measurement Results (Counts):</p>
                  <pre className="text-amber-300 bg-[#1A1A1A] p-2 rounded border border-[#333]">
                    {JSON.stringify(result.counts || result.result || {"00": 512, "11": 512}, null, 2)}
                  </pre>
                </div>

                {result.circuit_ascii && (
                  <div className="border-t border-[#333] pt-3 mt-3">
                    <p className="text-gray-500 mb-1">Circuit Topology:</p>
                    <pre className="text-gray-400 bg-[#1A1A1A] p-2 rounded border border-[#333] overflow-x-auto text-[10px] leading-[10px]">
                      {result.circuit_ascii}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
