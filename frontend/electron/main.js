const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('path');
const url = require('url');
const fs = require('fs');
const { spawn } = require('child_process');

// Behalte eine globale Referenz auf das Fenster-Objekt.
// Wenn du dies nicht tust, wird das Fenster automatisch geschlossen,
// sobald das JavaScript-Objekt Garbage-collected wird.
let mainWindow;
let serverProcess = null;

function createWindow() {
  // Erstelle das Browser-Fenster.
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../build/icon.png')
  });

  // und lade die index.html der App.
  const startUrl = process.env.ELECTRON_START_URL || url.format({
    pathname: path.join(__dirname, '../build/index.html'),
    protocol: 'file:',
    slashes: true
  });
  
  mainWindow.loadURL(startUrl);

  // Öffne die DevTools.
  if (process.env.ELECTRON_START_URL) {
    mainWindow.webContents.openDevTools();
  }

  // Emittiert, wenn das Fenster geschlossen wird.
  mainWindow.on('closed', function () {
    // Dereferenziere das Fenster-Objekt, normalerweise würdest du Fenster
    // in einem Array speichern, falls deine App mehrere Fenster unterstützt,
    // dies ist der Zeitpunkt, an dem du das zugehörige Element löschen solltest.
    mainWindow = null;
    
    // Beende den Server-Prozess, wenn das Fenster geschlossen wird
    if (serverProcess) {
      serverProcess.kill();
      serverProcess = null;
    }
  });

  // Erstelle das Anwendungsmenü
  const template = [
    {
      label: 'Datei',
      submenu: [
        {
          label: 'Einstellungen',
          click() {
            mainWindow.webContents.send('navigate', '/settings');
          }
        },
        { type: 'separator' },
        {
          label: 'Beenden',
          accelerator: process.platform === 'darwin' ? 'Command+Q' : 'Ctrl+Q',
          click() {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Bearbeiten',
      submenu: [
        { role: 'undo', label: 'Rückgängig' },
        { role: 'redo', label: 'Wiederholen' },
        { type: 'separator' },
        { role: 'cut', label: 'Ausschneiden' },
        { role: 'copy', label: 'Kopieren' },
        { role: 'paste', label: 'Einfügen' },
        { role: 'delete', label: 'Löschen' },
        { role: 'selectAll', label: 'Alles auswählen' }
      ]
    },
    {
      label: 'Ansicht',
      submenu: [
        { role: 'reload', label: 'Neu laden' },
        { role: 'forceReload', label: 'Neu laden erzwingen' },
        { role: 'toggleDevTools', label: 'Entwicklertools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Zoom zurücksetzen' },
        { role: 'zoomIn', label: 'Vergrößern' },
        { role: 'zoomOut', label: 'Verkleinern' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Vollbild' }
      ]
    },
    {
      label: 'Komponenten',
      submenu: [
        {
          label: 'Dashboard',
          click() {
            mainWindow.webContents.send('navigate', '/');
          }
        },
        {
          label: 'MCP-Server',
          click() {
            mainWindow.webContents.send('navigate', '/mcp-servers');
          }
        },
        {
          label: 'Workflows',
          click() {
            mainWindow.webContents.send('navigate', '/workflows');
          }
        }
      ]
    },
    {
      label: 'Hilfe',
      submenu: [
        {
          label: 'Dokumentation',
          click() {
            shell.openExternal('https://github.com/EcoSphereNetwork/Dev-Server-Workflow/tree/main/docs');
          }
        },
        {
          label: 'Über',
          click() {
            dialog.showMessageBox(mainWindow, {
              title: 'Über Dev-Server-Workflow',
              message: 'Dev-Server-Workflow',
              detail: 'Version: 1.0.0\nEine umfassende Lösung zur Integration von n8n-Workflows, MCP-Servern und OpenHands für die KI-gestützte Automatisierung von Entwicklungsprozessen.',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Diese Methode wird aufgerufen, wenn Electron die Initialisierung
// abgeschlossen hat und bereit ist, Browser-Fenster zu erstellen.
// Einige APIs können nur nach dem Auftreten dieses Events genutzt werden.
app.on('ready', () => {
  createWindow();
  
  // Starte den Backend-Server
  startBackendServer();
});

// Beende, wenn alle Fenster geschlossen sind.
app.on('window-all-closed', function () {
  // Unter macOS ist es üblich, dass Anwendungen und ihre Menüleiste
  // aktiv bleiben, bis der Nutzer explizit mit Cmd + Q die App beendet.
  if (process.platform !== 'darwin') {
    app.quit();
  }
  
  // Beende den Server-Prozess, wenn alle Fenster geschlossen sind
  if (serverProcess) {
    serverProcess.kill();
    serverProcess = null;
  }
});

app.on('activate', function () {
  // Unter macOS ist es üblich, ein neues Fenster der App zu erstellen, wenn
  // das Dock-Icon angeklickt wird und keine anderen Fenster offen sind.
  if (mainWindow === null) {
    createWindow();
  }
});

// In dieser Datei kannst du den Rest des App-spezifischen
// Hauptprozess-Codes einfügen. Du kannst den Code auch
// auf mehrere Dateien aufteilen und diese hier einbinden.

// IPC-Kommunikation mit dem Renderer-Prozess
ipcMain.on('start-component', (event, component) => {
  // Hier würde der Code zum Starten einer Komponente stehen
  console.log(`Starte Komponente: ${component}`);
  
  // Beispiel für die Ausführung eines Shell-Befehls
  const scriptPath = path.join(app.getAppPath(), '..', 'cli', 'dev-server.sh');
  const childProcess = spawn('bash', [scriptPath, 'start', component]);
  
  childProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
    event.reply('component-output', { component, output: data.toString() });
  });
  
  childProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    event.reply('component-error', { component, error: data.toString() });
  });
  
  childProcess.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    event.reply('component-status', { component, status: code === 0 ? 'success' : 'error', code });
  });
});

ipcMain.on('stop-component', (event, component) => {
  // Hier würde der Code zum Stoppen einer Komponente stehen
  console.log(`Stoppe Komponente: ${component}`);
  
  // Beispiel für die Ausführung eines Shell-Befehls
  const scriptPath = path.join(app.getAppPath(), '..', 'cli', 'dev-server.sh');
  const childProcess = spawn('bash', [scriptPath, 'stop', component]);
  
  childProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
    event.reply('component-output', { component, output: data.toString() });
  });
  
  childProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    event.reply('component-error', { component, error: data.toString() });
  });
  
  childProcess.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    event.reply('component-status', { component, status: code === 0 ? 'success' : 'error', code });
  });
});

// Funktion zum Starten des Backend-Servers
function startBackendServer() {
  // Hier würde der Code zum Starten des Backend-Servers stehen
  console.log('Starte Backend-Server...');
  
  // Beispiel für die Ausführung eines Shell-Befehls
  const scriptPath = path.join(app.getAppPath(), '..', 'cli', 'dev-server.sh');
  
  // Prüfe, ob das Skript existiert
  if (fs.existsSync(scriptPath)) {
    serverProcess = spawn('bash', [scriptPath, 'start', 'all']);
    
    serverProcess.stdout.on('data', (data) => {
      console.log(`Server stdout: ${data}`);
    });
    
    serverProcess.stderr.on('data', (data) => {
      console.error(`Server stderr: ${data}`);
    });
    
    serverProcess.on('close', (code) => {
      console.log(`Server process exited with code ${code}`);
      serverProcess = null;
    });
  } else {
    console.error(`Skript nicht gefunden: ${scriptPath}`);
  }
}