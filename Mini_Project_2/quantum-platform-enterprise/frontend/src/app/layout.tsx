import React from 'react';
import '../styles/globals.css';
import { Inter } from 'next/font/google';
import { Bell } from 'lucide-react';
import Sidebar from '../components/Sidebar';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Quantum Platform Enterprise',
  description: 'Enterprise Quantum Communication Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen bg-[#0A0A0A] flex text-gray-300 text-sm`}>
        <Sidebar />
        <main className="flex-1 flex flex-col min-h-screen relative overflow-hidden bg-[#0A0A0A]">
          <header className="h-14 border-b border-[#222] bg-[#0A0A0A]/80 backdrop-blur-md flex items-center justify-between px-6 z-10 sticky top-0">
            <div className="flex items-center gap-2">
              <span className="text-gray-400">Platform</span>
              <span className="text-gray-600">/</span>
              <span className="text-gray-100 font-medium">Workspace</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#111] border border-[#222]">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                <span className="text-xs text-gray-300">All Systems Operational</span>
              </div>
              <button className="text-gray-400 hover:text-white">
                <Bell className="w-4 h-4" />
              </button>
            </div>
          </header>
          
          <div className="flex-1 p-6 overflow-y-auto">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
