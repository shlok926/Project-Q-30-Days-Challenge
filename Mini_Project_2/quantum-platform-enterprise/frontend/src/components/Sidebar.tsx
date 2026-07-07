"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Settings, BarChart2, Cpu, Grid, LayoutDashboard, Search } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Experiments', path: '/experiments', icon: Grid },
    { name: 'Hardware & Nodes', path: '/hardware', icon: Cpu },
    { name: 'Telemetry & Logs', path: '/analytics', icon: BarChart2 },
    { name: 'Settings', path: '/settings', icon: Settings }
  ];

  return (
    <aside className="w-[240px] border-r border-[#222] bg-[#111] flex-shrink-0 flex flex-col hidden md:flex">
      <div className="h-14 flex items-center px-4 border-b border-[#222]">
        <div className="flex items-center gap-2 text-gray-100">
          <div className="w-6 h-6 rounded bg-white text-black flex items-center justify-center font-bold text-xs">Q</div>
          <span className="font-semibold text-sm tracking-tight">Quantum Enterprise</span>
        </div>
      </div>
      <div className="p-3">
        <div className="relative">
          <Search className="absolute left-2.5 top-2 h-4 w-4 text-gray-500" />
          <input 
            type="text" 
            placeholder="Search..." 
            className="w-full bg-[#1A1A1A] border border-[#333] rounded-md pl-9 pr-3 py-1.5 text-sm focus:outline-none focus:border-gray-500 text-gray-200 placeholder-gray-500"
          />
        </div>
      </div>
      <nav className="flex-1 px-3 py-2 space-y-0.5">
        {navItems.map((item) => {
          const isActive = pathname === item.path;
          return (
            <Link 
              key={item.name} 
              href={item.path} 
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${isActive ? 'bg-[#222] text-white' : 'text-gray-400 hover:text-white hover:bg-[#1A1A1A]'}`}
            >
              <item.icon className="w-4 h-4" />
              <span className="font-medium text-xs">{item.name}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-[#222]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500"></div>
          <div className="flex flex-col">
            <span className="text-xs font-medium text-white">Admin User</span>
            <span className="text-[10px] text-gray-500">admin@quantum.com</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
