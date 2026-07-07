import React from 'react';

export const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <aside className="w-64 bg-white dark:bg-gray-800 border-r dark:border-gray-700">
        <nav className="p-4 space-y-2">
          {/* Sidebar Navigation */}
          <div>Experiments</div>
          <div>Analytics</div>
          <div>Providers</div>
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
};
