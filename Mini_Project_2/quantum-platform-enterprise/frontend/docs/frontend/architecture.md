# Frontend Architecture
This document outlines the Feature-First architecture used in the Quantum Platform Enterprise frontend.
- **Features**: Highly cohesive modules containing their own API, components, and hooks.
- **Shared**: Global components like UI kit (Button, Modal, Tables).
- **Services**: Global Axios instance and interceptors.
- **Store**: Zustand for client state, TanStack Query for server state.\n