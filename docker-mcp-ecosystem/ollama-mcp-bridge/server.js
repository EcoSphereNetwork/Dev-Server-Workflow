const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { Ollama } = require('ollama');

// Konfiguration laden
const configPath = process.env.CONFIG_PATH || path.join(__dirname, 'bridge_config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Umgebungsvariablen in der Konfiguration ersetzen
const replaceEnvVars = (obj) => {
  if (typeof obj !== 'object' || obj === null) return obj;
  
  if (Array.isArray(obj)) {
    return obj.map(replaceEnvVars);
  }
  
  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => {
      if (typeof value === 'string' && value.startsWith('${') && value.endsWith('}')) {
        const envVar = value.slice(2, -1);
        return [key, process.env[envVar] || value];
      }
      if (typeof value === 'object' && value !== null) {
        return [key, replaceEnvVars(value)];
      }
      return [key, value];
    })
  );
};

const processedConfig = replaceEnvVars(config);

// Express-App erstellen
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Ollama-Client initialisieren
const ollama = new Ollama({
  host: processedConfig.llm.baseUrl || 'http://ollama:11434'
});

// MCP-Server starten
const mcpServers = {};
Object.entries(processedConfig.mcpServers).forEach(([name, serverConfig]) => {
  if (serverConfig.command && serverConfig.args) {
    console.log(`Starting MCP server: ${name}`);
    const env = { ...process.env, ...(serverConfig.env || {}) };
    const server = spawn(serverConfig.command, serverConfig.args, { env });
    
    server.stdout.on('data', (data) => {
      console.log(`[${name}] ${data.toString().trim()}`);
    });
    
    server.stderr.on('data', (data) => {
      console.error(`[${name}] ERROR: ${data.toString().trim()}`);
    });
    
    server.on('close', (code) => {
      console.log(`[${name}] MCP server exited with code ${code}`);
    });
    
    mcpServers[name] = server;
  }
});

// MCP-Bridge-Endpunkt
app.post('/mcp', express.json(), async (req, res) => {
  try {
    const { method, params, id } = req.body;
    
    if (method === 'mcp.listTools') {
      // Werkzeuge auflisten
      const tools = [];
      // Hier würden wir die Werkzeuge von allen MCP-Servern sammeln
      res.json({ jsonrpc: '2.0', id, result: tools });
    } else if (method.startsWith('mcp.')) {
      // MCP-Anfrage an den entsprechenden Server weiterleiten
      // Hier würde die Logik zur Weiterleitung implementiert
      res.json({ jsonrpc: '2.0', id, result: 'Not implemented yet' });
    } else {
      res.status(400).json({ 
        jsonrpc: '2.0', 
        id, 
        error: { code: -32601, message: 'Method not found' } 
      });
    }
  } catch (error) {
    console.error('Error processing MCP request:', error);
    res.status(500).json({ 
      jsonrpc: '2.0', 
      id: req.body.id, 
      error: { code: -32603, message: 'Internal error' } 
    });
  }
});

// Chat-Endpunkt
app.post('/chat', express.json(), async (req, res) => {
  try {
    const { prompt, model } = req.body;
    
    const response = await ollama.chat({
      model: model || processedConfig.llm.model,
      messages: [{ role: 'user', content: prompt }],
      options: {
        temperature: processedConfig.llm.temperature || 0.7,
        top_p: processedConfig.llm.top_p || 0.9,
        max_tokens: processedConfig.llm.maxTokens || 2048
      }
    });
    
    res.json(response);
  } catch (error) {
    console.error('Error processing chat request:', error);
    res.status(500).json({ error: error.message });
  }
});

// Gesundheitscheck-Endpunkt
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Server starten
const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
  console.log(`Ollama MCP Bridge running on port ${PORT}`);
});

// Aufräumen beim Beenden
process.on('SIGINT', () => {
  console.log('Shutting down MCP servers...');
  Object.values(mcpServers).forEach(server => {
    server.kill();
  });
  process.exit(0);
});