const { contextBridge, ipcRenderer, shell } = require('electron');
const os = require('os');

// Exponiere geschützte Methoden, die es dem Renderer-Prozess erlauben,
// mit dem Hauptprozess über das contextBridge-API zu kommunizieren.
contextBridge.exposeInMainWorld(
  'electron',
  {
    // Komponenten-Verwaltung
    startComponent: (component) => {
      ipcRenderer.send('start-component', component);
    },
    stopComponent: (component) => {
      ipcRenderer.send('stop-component', component);
    },
    onComponentOutput: (callback) => {
      ipcRenderer.on('component-output', (_, data) => callback(data));
    },
    onComponentError: (callback) => {
      ipcRenderer.on('component-error', (_, data) => callback(data));
    },
    onComponentStatus: (callback) => {
      ipcRenderer.on('component-status', (_, data) => callback(data));
    },
    
    // Navigation
    onNavigate: (callback) => {
      ipcRenderer.on('navigate', (_, path) => callback(path));
    },
    
    // System-Informationen
    getSystemInfo: () => {
      return {
        platform: os.platform(),
        arch: os.arch(),
        cpus: os.cpus(),
        totalMemory: os.totalmem(),
        freeMemory: os.freemem(),
        hostname: os.hostname(),
        userInfo: os.userInfo(),
        uptime: os.uptime(),
        version: process.version
      };
    },
    
    // Externe Links
    openExternal: (url) => {
      shell.openExternal(url);
    },
    
    // Dienste-Integration
    isElectron: true
  }
);