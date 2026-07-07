import os
import json

base_dir = r"d:\Downloads\Project - Q 30 (Day)\Mini_Project_2\quantum-platform-enterprise\frontend"

folders = [
    "src/app",
    "src/features/auth",
    "src/features/experiments",
    "src/features/analytics",
    "src/features/providers",
    "src/features/monitoring",
    "src/features/users",
    "src/features/settings",
    "src/features/quantum",
    "src/shared",
    "src/components/ui",
    "src/layouts",
    "src/hooks",
    "src/services/api",
    "src/store",
    "src/lib",
    "src/types",
    "src/utils",
    "src/styles",
    "tests/components",
    "tests/e2e",
    "docs/frontend"
]

files = {
    # Types
    "src/types/index.ts": """
export interface User {
  id: string;
  email: string;
  username: string;
  role: 'admin' | 'researcher' | 'student' | 'viewer';
}
""",
    # API Layer (Axios instance with interceptors)
    "src/services/api/client.ts": """
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/authStore';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
""",
    # State Management (Zustand)
    "src/store/authStore.ts": """
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      login: (user, token) => set({ user, accessToken: token, isAuthenticated: true }),
      logout: () => set({ user: null, accessToken: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
""",
    # Layout System
    "src/layouts/DashboardLayout.tsx": """
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
""",
    # Shared UI Component (Shadcn-like structure)
    "src/components/ui/Button.tsx": """
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
}

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', className = '', ...props }) => {
  const baseStyles = "px-4 py-2 rounded font-medium focus:outline-none focus:ring-2 transition-colors";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 dark:bg-gray-700 dark:text-gray-100",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500"
  };

  return (
    <button className={`${baseStyles} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
};
""",
    # Feature Architecture (Experiment Module)
    "src/features/experiments/api/index.ts": """
import apiClient from '@/services/api/client';

export const getExperiments = async () => {
  const response = await apiClient.get('/experiments');
  return response.data;
};
""",
    "src/features/experiments/components/ExperimentList.tsx": """
import React from 'react';

export const ExperimentList = () => {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Experiment Explorer</h2>
      <p>Data grid will be loaded here using React Query.</p>
    </div>
  );
};
""",
    # Docs
    "docs/frontend/architecture.md": """
# Frontend Architecture
This document outlines the Feature-First architecture used in the Quantum Platform Enterprise frontend.
- **Features**: Highly cohesive modules containing their own API, components, and hooks.
- **Shared**: Global components like UI kit (Button, Modal, Tables).
- **Services**: Global Axios instance and interceptors.
- **Store**: Zustand for client state, TanStack Query for server state.
"""
}

# Create folders
for folder in folders:
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
    with open(os.path.join(base_dir, folder, ".gitkeep"), "w") as f:
        pass

# Create files
for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n")

# Update package.json to include dependencies like zustand, axios, react-query
pkg_path = os.path.join(base_dir, "package.json")
if os.path.exists(pkg_path):
    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg_data = json.load(f)
    
    if "dependencies" not in pkg_data:
        pkg_data["dependencies"] = {}
    
    pkg_data["dependencies"].update({
        "axios": "^1.6.0",
        "@tanstack/react-query": "^5.0.0",
        "zustand": "^4.4.0",
        "lucide-react": "^0.292.0",
        "clsx": "^2.0.0",
        "tailwind-merge": "^2.0.0"
    })
    
    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(pkg_data, f, indent=2)

print("Phase 10 Frontend Platform Architecture Created.")
