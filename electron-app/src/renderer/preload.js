const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Permission methods
  getPermissions: () => ipcRenderer.invoke('get-permissions'),
  
  // Recording methods
  startRecording: () => ipcRenderer.invoke('start-recording'),
  stopRecording: () => ipcRenderer.invoke('stop-recording'),
  
  // Configuration methods
  configureApp: (config) => ipcRenderer.invoke('configure-app', config),
  getStatus: () => ipcRenderer.invoke('get-status'),
  
  // Dialog methods
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  
  // Listen for messages from main process
  onPythonMessage: (callback) => {
    ipcRenderer.on('python-message', (event, data) => callback(data));
  },
  
  onStartRecording: (callback) => {
    ipcRenderer.on('start-recording', callback);
  },
  
  // Remove listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});