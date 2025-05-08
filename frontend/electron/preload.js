const { contextBridge, ipcRenderer } = require('electron');

// Exponiere geschützte Methoden, die es dem Renderer-Prozess erlauben,
// mit dem Hauptprozess über das contextBridge-API zu kommunizieren.
contextBridge.exposeInMainWorld(
  'electron',
  {
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
    onNavigate: (callback) => {
      ipcRenderer.on('navigate', (_, path) => callback(path));
    }
  }
);