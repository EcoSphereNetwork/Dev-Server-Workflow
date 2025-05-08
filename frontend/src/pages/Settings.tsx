// src/pages/Settings.tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  Button, 
  Card, 
  Input, 
  Select, 
  Switch, 
  Alert,
  Tabs,
  TabView,
  FormControl,
  FormField
} from '../components/SmolituxComponents';
import apiClient from '../api/client';
import { colors } from '../theme';

interface Settings {
  general: {
    workspacePath: string;
    logLevel: 'debug' | 'info' | 'warning' | 'error';
    language: 'de' | 'en';
    darkMode: boolean;
  };
  api: {
    githubToken: string;
    openprojectToken: string;
    n8nApiKey: string;
    anthropicApiKey: string;
    openaiApiKey: string;
  };
  mcp: {
    dockerMcpPort: number;
    n8nMcpPort: number;
    mcpAuthSecret: string;
  };
  llm: {
    activeLlm: 'llamafile' | 'claude' | 'openai';
    llamafilePath: string;
    llamafilePort: number;
  };
}

const SettingsContainer = styled.div`
  padding: 20px;
`;

const SettingsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const SettingsTitle = styled.h1`
  font-size: 1.5rem;
  margin: 0;
`;

const SettingsActions = styled.div`
  display: flex;
  gap: 10px;
`;

const SettingsSection = styled.div`
  margin-bottom: 30px;
`;

const SettingsSectionTitle = styled.h2`
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: ${colors.primary.main};
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    general: {
      workspacePath: '/workspace',
      logLevel: 'info',
      language: 'de',
      darkMode: false,
    },
    api: {
      githubToken: '',
      openprojectToken: '',
      n8nApiKey: '',
      anthropicApiKey: '',
      openaiApiKey: '',
    },
    mcp: {
      dockerMcpPort: 3334,
      n8nMcpPort: 3335,
      mcpAuthSecret: '',
    },
    llm: {
      activeLlm: 'llamafile',
      llamafilePath: '/usr/local/bin/llamafile',
      llamafilePort: 8080,
    },
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
        // const response = await apiClient.get('/settings');
        // setSettings(response.data);
        
        // Simulierte Daten für die Entwicklung
        setTimeout(() => {
          setSettings({
            general: {
              workspacePath: '/home/user/dev-server',
              logLevel: 'info',
              language: 'de',
              darkMode: false,
            },
            api: {
              githubToken: 'ghp_xxxxxxxxxxxxxxxxxxxx',
              openprojectToken: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
              n8nApiKey: 'n8n_api_xxxxxxxxxxxxxxxx',
              anthropicApiKey: 'sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
              openaiApiKey: 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            },
            mcp: {
              dockerMcpPort: 3334,
              n8nMcpPort: 3335,
              mcpAuthSecret: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            },
            llm: {
              activeLlm: 'llamafile',
              llamafilePath: '/usr/local/bin/llamafile',
              llamafilePort: 8080,
            },
          });
          setLoading(false);
        }, 500);
      } catch (err: any) {
        setError('Fehler beim Laden der Einstellungen');
        console.error(err);
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.put('/settings', settings);
      
      // Simulierte Verzögerung für die Entwicklung
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Einstellungen erfolgreich gespeichert');
      setSaving(false);
    } catch (err: any) {
      setError('Fehler beim Speichern der Einstellungen');
      console.error(err);
      setSaving(false);
    }
  };

  const handleChange = (section: keyof Settings, key: string, value: any) => {
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [key]: value
      }
    });
  };

  if (loading) {
    return (
      <SettingsContainer>
        <div>Lade Einstellungen...</div>
      </SettingsContainer>
    );
  }

  return (
    <SettingsContainer>
      <SettingsHeader>
        <SettingsTitle>Einstellungen</SettingsTitle>
        <SettingsActions>
          <Button 
            variant="primary" 
            onClick={handleSaveSettings}
            loading={saving}
            disabled={saving}
          >
            Speichern
          </Button>
        </SettingsActions>
      </SettingsHeader>

      {error && (
        <Alert variant="error" style={{ marginBottom: '20px' }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" style={{ marginBottom: '20px' }}>
          {success}
        </Alert>
      )}

      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <TabView label="Allgemein">
          <Card>
            <div style={{ padding: '20px' }}>
              <SettingsSection>
                <SettingsSectionTitle>Allgemeine Einstellungen</SettingsSectionTitle>
                
                <FormGroup>
                  <Input
                    label="Workspace-Pfad"
                    value={settings.general.workspacePath}
                    onChange={(e) => handleChange('general', 'workspacePath', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Select
                    label="Log-Level"
                    value={settings.general.logLevel}
                    onChange={(e) => handleChange('general', 'logLevel', e.target.value)}
                    fullWidth
                  >
                    <option value="debug">Debug</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                  </Select>
                </FormGroup>
                
                <FormGroup>
                  <Select
                    label="Sprache"
                    value={settings.general.language}
                    onChange={(e) => handleChange('general', 'language', e.target.value)}
                    fullWidth
                  >
                    <option value="de">Deutsch</option>
                    <option value="en">Englisch</option>
                  </Select>
                </FormGroup>
                
                <FormGroup>
                  <FormControl>
                    <label>Dark Mode</label>
                    <Switch
                      checked={settings.general.darkMode}
                      onChange={(e) => handleChange('general', 'darkMode', e.target.checked)}
                    />
                  </FormControl>
                </FormGroup>
              </SettingsSection>
            </div>
          </Card>
        </TabView>
        
        <TabView label="API-Schlüssel">
          <Card>
            <div style={{ padding: '20px' }}>
              <SettingsSection>
                <SettingsSectionTitle>API-Schlüssel</SettingsSectionTitle>
                
                <FormGroup>
                  <Input
                    label="GitHub Token"
                    type="password"
                    value={settings.api.githubToken}
                    onChange={(e) => handleChange('api', 'githubToken', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="OpenProject Token"
                    type="password"
                    value={settings.api.openprojectToken}
                    onChange={(e) => handleChange('api', 'openprojectToken', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="n8n API-Schlüssel"
                    type="password"
                    value={settings.api.n8nApiKey}
                    onChange={(e) => handleChange('api', 'n8nApiKey', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="Anthropic API-Schlüssel"
                    type="password"
                    value={settings.api.anthropicApiKey}
                    onChange={(e) => handleChange('api', 'anthropicApiKey', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="OpenAI API-Schlüssel"
                    type="password"
                    value={settings.api.openaiApiKey}
                    onChange={(e) => handleChange('api', 'openaiApiKey', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
              </SettingsSection>
            </div>
          </Card>
        </TabView>
        
        <TabView label="MCP-Server">
          <Card>
            <div style={{ padding: '20px' }}>
              <SettingsSection>
                <SettingsSectionTitle>MCP-Server Einstellungen</SettingsSectionTitle>
                
                <FormGroup>
                  <Input
                    label="Docker MCP Port"
                    type="number"
                    value={settings.mcp.dockerMcpPort.toString()}
                    onChange={(e) => handleChange('mcp', 'dockerMcpPort', parseInt(e.target.value))}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="n8n MCP Port"
                    type="number"
                    value={settings.mcp.n8nMcpPort.toString()}
                    onChange={(e) => handleChange('mcp', 'n8nMcpPort', parseInt(e.target.value))}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="MCP Auth Secret"
                    type="password"
                    value={settings.mcp.mcpAuthSecret}
                    onChange={(e) => handleChange('mcp', 'mcpAuthSecret', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
              </SettingsSection>
            </div>
          </Card>
        </TabView>
        
        <TabView label="LLM">
          <Card>
            <div style={{ padding: '20px' }}>
              <SettingsSection>
                <SettingsSectionTitle>LLM-Einstellungen</SettingsSectionTitle>
                
                <FormGroup>
                  <Select
                    label="Aktives LLM"
                    value={settings.llm.activeLlm}
                    onChange={(e) => handleChange('llm', 'activeLlm', e.target.value)}
                    fullWidth
                  >
                    <option value="llamafile">Llamafile</option>
                    <option value="claude">Claude</option>
                    <option value="openai">OpenAI</option>
                  </Select>
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="Llamafile Pfad"
                    value={settings.llm.llamafilePath}
                    onChange={(e) => handleChange('llm', 'llamafilePath', e.target.value)}
                    fullWidth
                  />
                </FormGroup>
                
                <FormGroup>
                  <Input
                    label="Llamafile Port"
                    type="number"
                    value={settings.llm.llamafilePort.toString()}
                    onChange={(e) => handleChange('llm', 'llamafilePort', parseInt(e.target.value))}
                    fullWidth
                  />
                </FormGroup>
              </SettingsSection>
            </div>
          </Card>
        </TabView>
      </Tabs>
    </SettingsContainer>
  );
};

export default Settings;