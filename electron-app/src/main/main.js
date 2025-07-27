const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, systemPreferences } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;
let tray = null;
let pythonProcess = null;

// Enable live reload for development
if (process.argv.includes('--dev')) {
  require('electron-reload')(__dirname, {
    electron: path.join(__dirname, '..', 'node_modules', '.bin', 'electron'),
    hardResetMethod: 'exit'
  });
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 500,
    height: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, '..', 'renderer', 'preload.js')
    },
    titleBarStyle: 'hiddenInset',
    // icon: path.join(__dirname, '..', '..', 'build', 'icon.icns'), // Skip for now
    show: false
  });

  // Load the app
  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle window minimize to tray
  mainWindow.on('minimize', (event) => {
    event.preventDefault();
    mainWindow.hide();
  });

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }
}

function createTray() {
  const iconPath = path.join(__dirname, '..', '..', 'build', 'tray-icon.png');
  
  // Check if icon exists, create a simple tray without icon if it doesn't
  try {
    if (fs.existsSync(iconPath)) {
      tray = new Tray(iconPath);
    } else {
      // Create a minimal tray icon (this will use a default system icon)
      console.log('Tray icon not found, using default');
      // Skip tray creation for now - we'll add it later
      return;
    }
  } catch (error) {
    console.log('Failed to create tray:', error.message);
    return;
  }
  
  const contextMenu = Menu.buildFromTemplate([
    { 
      label: 'Show WisprFlow Lite', 
      click: () => {
        if (mainWindow) {
          mainWindow.show();
        }
      }
    },
    { 
      label: 'Start Recording', 
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('start-recording');
        }
      }
    },
    { type: 'separator' },
    { 
      label: 'Quit', 
      click: () => {
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('WisprFlow Lite - Voice Transcription');
  tray.setContextMenu(contextMenu);
  
  // Show window on tray click
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
      }
    }
  });
}

async function checkMacOSPermissions() {
  if (process.platform !== 'darwin') {
    return { microphone: true, accessibility: true };
  }

  const microphoneStatus = systemPreferences.getMediaAccessStatus('microphone');
  const microphoneGranted = microphoneStatus === 'granted';

  // Request microphone permission if not granted
  if (!microphoneGranted && microphoneStatus !== 'denied') {
    await systemPreferences.askForMediaAccess('microphone');
  }

  return {
    microphone: systemPreferences.getMediaAccessStatus('microphone') === 'granted',
    accessibility: true // We'll handle this in the Python process
  };
}

function startPythonProcess() {
  if (pythonProcess) {
    pythonProcess.kill();
  }

  const pythonExecutable = path.join(__dirname, '..', '..', 'dist', 'python', 'voice_transcriber');
  
  // Check if Python executable exists, use development version if not
  let pythonCommand, pythonArgs;
  
  if (fs.existsSync(pythonExecutable)) {
    pythonCommand = pythonExecutable;
    pythonArgs = ['--ipc'];
  } else {
    // Development mode - use Python script directly
    console.log('Using development Python script');
    pythonCommand = 'python3';
    pythonArgs = [path.join(__dirname, '..', 'python', 'voice_transcriber_ipc.py'), '--ipc'];
  }

  pythonProcess = spawn(pythonCommand, pythonArgs, {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  pythonProcess.stdout.on('data', (data) => {
    const message = data.toString().trim();
    console.log('Python stdout:', message);
    
    try {
      const parsed = JSON.parse(message);
      if (mainWindow) {
        mainWindow.webContents.send('python-message', parsed);
      }
    } catch (e) {
      // Not JSON, treat as log
      console.log('Python log:', message);
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('Python stderr:', data.toString());
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    pythonProcess = null;
  });

  return pythonProcess;
}

// App event handlers
app.whenReady().then(async () => {
  // Check permissions first
  const permissions = await checkMacOSPermissions();
  
  createWindow();
  createTray();
  
  // Start Python process
  startPythonProcess();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

// IPC handlers
ipcMain.handle('get-permissions', async () => {
  return await checkMacOSPermissions();
});

ipcMain.handle('start-recording', () => {
  if (pythonProcess) {
    pythonProcess.stdin.write(JSON.stringify({ command: 'start_recording' }) + '\n');
    return { success: true };
  }
  return { success: false, error: 'Python process not running' };
});

ipcMain.handle('stop-recording', () => {
  if (pythonProcess) {
    pythonProcess.stdin.write(JSON.stringify({ command: 'stop_recording' }) + '\n');
    return { success: true };
  }
  return { success: false, error: 'Python process not running' };
});

ipcMain.handle('configure-app', (event, config) => {
  if (pythonProcess) {
    pythonProcess.stdin.write(JSON.stringify({ command: 'configure', config }) + '\n');
    return { success: true };
  }
  return { success: false, error: 'Python process not running' };
});

ipcMain.handle('get-status', () => {
  if (pythonProcess) {
    pythonProcess.stdin.write(JSON.stringify({ command: 'get_status' }) + '\n');
    return { success: true };
  }
  return { success: false, error: 'Python process not running' };
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});