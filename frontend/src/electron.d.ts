// src/electron.d.ts

interface ElectronAPI {
  startComponent: (component: string) => void;
  stopComponent: (component: string) => void;
  onComponentOutput: (callback: (data: { component: string, output: string }) => void) => void;
  onComponentError: (callback: (data: { component: string, error: string }) => void) => void;
  onComponentStatus: (callback: (data: { component: string, status: string, code: number }) => void) => void;
  onNavigate: (callback: (path: string) => void) => void;
}

declare global {
  interface Window {
    electron?: ElectronAPI;
  }
}