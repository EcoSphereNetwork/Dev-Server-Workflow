// src/pages/UserSettings.tsx
import React, { useState } from 'react';
import styled from 'styled-components';
import { Container, Card, Button, Input } from '../design-system';
import { useSettings } from '../context/SettingsContext';
import { ColorScheme, UIDensity, Language } from '../types/settings';

// Styled-Components für die Settings-Seite
const PageContainer = styled.div`
  padding: ${props => props.theme.spacing.md};
`;

const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const PageTitle = styled.h1`
  font-size: ${props => props.theme.typography.fontSize.xl};
  margin: 0;
`;

const SettingsContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.lg};
  
  @media (max-width: ${props => props.theme.breakpoints.md}) {
    flex-direction: column;
  }
`;

const SettingsSidebar = styled.div`
  width: 250px;
  
  @media (max-width: ${props => props.theme.breakpoints.md}) {
    width: 100%;
  }
`;

const SettingsContent = styled.div`
  flex: 1;
`;

const SettingsNavigation = styled.nav`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
`;

const SettingsNavItem = styled.button<{ $active: boolean }>`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background-color: ${props => props.$active ? props.theme.colors.primary + '20' : 'transparent'};
  color: ${props => props.$active ? props.theme.colors.primary : props.theme.colors.text.primary};
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  cursor: pointer;
  text-align: left;
  font-weight: ${props => props.$active ? props.theme.typography.fontWeight.medium : props.theme.typography.fontWeight.regular};
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.$active ? props.theme.colors.primary + '30' : props.theme.colors.background.paper};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const SettingsNavIcon = styled.span`
  margin-right: ${props => props.theme.spacing.sm};
  font-size: 1.2em;
`;

const SettingsSection = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const SettingsSectionTitle = styled.h2`
  font-size: ${props => props.theme.typography.fontSize.lg};
  margin: 0 0 ${props => props.theme.spacing.md} 0;
  padding-bottom: ${props => props.theme.spacing.xs};
  border-bottom: 1px solid ${props => props.theme.colors.divider};
`;

const SettingsGroup = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SettingsGroupTitle = styled.h3`
  font-size: ${props => props.theme.typography.fontSize.md};
  margin: 0 0 ${props => props.theme.spacing.sm} 0;
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const SettingsGroupDescription = styled.p`
  margin: 0 0 ${props => props.theme.spacing.md} 0;
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

const SettingsControls = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const SettingsRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  @media (max-width: ${props => props.theme.breakpoints.sm}) {
    flex-direction: column;
    align-items: flex-start;
    gap: ${props => props.theme.spacing.sm};
  }
`;

const SettingsLabel = styled.label`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const SettingsControl = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
`;

const SettingsButton = styled.button<{ $active: boolean }>`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background-color: ${props => props.$active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.$active ? 'white' : props.theme.colors.text.primary};
  border: 1px solid ${props => props.$active ? props.theme.colors.primary : props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.md};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.$active ? props.theme.colors.primaryDark : props.theme.colors.background.paper};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const SettingsSwitch = styled.label`
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
`;

const SettingsSwitchInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
  
  &:checked + span {
    background-color: ${props => props.theme.colors.primary};
  }
  
  &:checked + span:before {
    transform: translateX(24px);
  }
  
  &:focus + span {
    box-shadow: 0 0 1px ${props => props.theme.colors.primary};
  }
`;

const SettingsSwitchSlider = styled.span`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${props => props.theme.colors.neutral[300]};
  transition: 0.4s;
  border-radius: 24px;
  
  &:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.4s;
    border-radius: 50%;
  }
`;

const SettingsActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.xl};
`;

const SettingsSlider = styled.input`
  width: 100%;
  max-width: 200px;
`;

// Settings-Komponente
const UserSettings: React.FC = () => {
  // Settings Context
  const { 
    settings, 
    updateAppearance, 
    updateDashboard, 
    updateNotifications, 
    updateAssistant, 
    updateSecurity, 
    updateAdvanced,
    resetSettings,
    setColorScheme,
    setDensity,
    setLanguage,
  } = useSettings();
  
  // State für aktiven Tab
  const [activeTab, setActiveTab] = useState<
    'appearance' | 'dashboard' | 'notifications' | 'assistant' | 'services' | 'security' | 'advanced'
  >('appearance');
  
  // Rendere den aktiven Tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'appearance':
        return (
          <SettingsSection>
            <SettingsSectionTitle>Erscheinungsbild</SettingsSectionTitle>
            
            <SettingsGroup>
              <SettingsGroupTitle>Farbschema</SettingsGroupTitle>
              <SettingsGroupDescription>
                Wählen Sie das Farbschema für die Benutzeroberfläche.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Farbschema</SettingsLabel>
                  <SettingsControl>
                    <SettingsButton
                      $active={settings.appearance.colorScheme === 'light'}
                      onClick={() => setColorScheme('light')}
                    >
                      Hell
                    </SettingsButton>
                    <SettingsButton
                      $active={settings.appearance.colorScheme === 'dark'}
                      onClick={() => setColorScheme('dark')}
                    >
                      Dunkel
                    </SettingsButton>
                    <SettingsButton
                      $active={settings.appearance.colorScheme === 'system'}
                      onClick={() => setColorScheme('system')}
                    >
                      System
                    </SettingsButton>
                  </SettingsControl>
                </SettingsRow>
              </SettingsControls>
            </SettingsGroup>
            
            <SettingsGroup>
              <SettingsGroupTitle>Dichte</SettingsGroupTitle>
              <SettingsGroupDescription>
                Passen Sie die Dichte der Benutzeroberfläche an.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Dichte</SettingsLabel>
                  <SettingsControl>
                    <SettingsButton
                      $active={settings.appearance.density === 'compact'}
                      onClick={() => setDensity('compact')}
                    >
                      Kompakt
                    </SettingsButton>
                    <SettingsButton
                      $active={settings.appearance.density === 'comfortable'}
                      onClick={() => setDensity('comfortable')}
                    >
                      Komfortabel
                    </SettingsButton>
                    <SettingsButton
                      $active={settings.appearance.density === 'spacious'}
                      onClick={() => setDensity('spacious')}
                    >
                      Geräumig
                    </SettingsButton>
                  </SettingsControl>
                </SettingsRow>
              </SettingsControls>
            </SettingsGroup>
            
            <SettingsGroup>
              <SettingsGroupTitle>Schriftgröße</SettingsGroupTitle>
              <SettingsGroupDescription>
                Passen Sie die Schriftgröße der Benutzeroberfläche an.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Schriftgröße: {settings.appearance.fontSize}%</SettingsLabel>
                  <SettingsControl>
                    <SettingsSlider
                      type="range"
                      min="75"
                      max="150"
                      step="5"
                      value={settings.appearance.fontSize}
                      onChange={(e) => updateAppearance({ fontSize: parseInt(e.target.value) })}
                    />
                  </SettingsControl>
                </SettingsRow>
              </SettingsControls>
            </SettingsGroup>
            
            <SettingsGroup>
              <SettingsGroupTitle>Animationen</SettingsGroupTitle>
              <SettingsGroupDescription>
                Aktivieren oder deaktivieren Sie Animationen in der Benutzeroberfläche.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Animationen aktivieren</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.appearance.animations}
                        onChange={(e) => updateAppearance({ animations: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
              </SettingsControls>
            </SettingsGroup>
          </SettingsSection>
        );
      
      case 'dashboard':
        return (
          <SettingsSection>
            <SettingsSectionTitle>Dashboard</SettingsSectionTitle>
            
            <SettingsGroup>
              <SettingsGroupTitle>Aktualisierung</SettingsGroupTitle>
              <SettingsGroupDescription>
                Konfigurieren Sie die automatische Aktualisierung des Dashboards.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Automatische Aktualisierung</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.dashboard.autoRefresh}
                        onChange={(e) => updateDashboard({ autoRefresh: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
                
                {settings.dashboard.autoRefresh && (
                  <SettingsRow>
                    <SettingsLabel>Aktualisierungsintervall: {settings.dashboard.refreshInterval} Sekunden</SettingsLabel>
                    <SettingsControl>
                      <SettingsSlider
                        type="range"
                        min="5"
                        max="120"
                        step="5"
                        value={settings.dashboard.refreshInterval}
                        onChange={(e) => updateDashboard({ refreshInterval: parseInt(e.target.value) })}
                      />
                    </SettingsControl>
                  </SettingsRow>
                )}
              </SettingsControls>
            </SettingsGroup>
          </SettingsSection>
        );
      
      case 'notifications':
        return (
          <SettingsSection>
            <SettingsSectionTitle>Benachrichtigungen</SettingsSectionTitle>
            
            <SettingsGroup>
              <SettingsGroupTitle>Benachrichtigungseinstellungen</SettingsGroupTitle>
              <SettingsGroupDescription>
                Konfigurieren Sie, wie und wann Sie Benachrichtigungen erhalten.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Benachrichtigungen aktivieren</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.notifications.enabled}
                        onChange={(e) => updateNotifications({ enabled: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
                
                {settings.notifications.enabled && (
                  <>
                    <SettingsRow>
                      <SettingsLabel>Desktop-Benachrichtigungen</SettingsLabel>
                      <SettingsControl>
                        <SettingsSwitch>
                          <SettingsSwitchInput
                            type="checkbox"
                            checked={settings.notifications.desktop}
                            onChange={(e) => updateNotifications({ desktop: e.target.checked })}
                          />
                          <SettingsSwitchSlider />
                        </SettingsSwitch>
                      </SettingsControl>
                    </SettingsRow>
                    
                    <SettingsRow>
                      <SettingsLabel>E-Mail-Benachrichtigungen</SettingsLabel>
                      <SettingsControl>
                        <SettingsSwitch>
                          <SettingsSwitchInput
                            type="checkbox"
                            checked={settings.notifications.email}
                            onChange={(e) => updateNotifications({ email: e.target.checked })}
                          />
                          <SettingsSwitchSlider />
                        </SettingsSwitch>
                      </SettingsControl>
                    </SettingsRow>
                  </>
                )}
              </SettingsControls>
            </SettingsGroup>
            
            {settings.notifications.enabled && (
              <SettingsGroup>
                <SettingsGroupTitle>Benachrichtigungstypen</SettingsGroupTitle>
                <SettingsGroupDescription>
                  Wählen Sie, welche Arten von Benachrichtigungen Sie erhalten möchten.
                </SettingsGroupDescription>
                <SettingsControls>
                  <SettingsRow>
                    <SettingsLabel>System-Benachrichtigungen</SettingsLabel>
                    <SettingsControl>
                      <SettingsSwitch>
                        <SettingsSwitchInput
                          type="checkbox"
                          checked={settings.notifications.types.system}
                          onChange={(e) => updateNotifications({ 
                            types: { 
                              ...settings.notifications.types, 
                              system: e.target.checked 
                            } 
                          })}
                        />
                        <SettingsSwitchSlider />
                      </SettingsSwitch>
                    </SettingsControl>
                  </SettingsRow>
                  
                  <SettingsRow>
                    <SettingsLabel>Dienst-Benachrichtigungen</SettingsLabel>
                    <SettingsControl>
                      <SettingsSwitch>
                        <SettingsSwitchInput
                          type="checkbox"
                          checked={settings.notifications.types.services}
                          onChange={(e) => updateNotifications({ 
                            types: { 
                              ...settings.notifications.types, 
                              services: e.target.checked 
                            } 
                          })}
                        />
                        <SettingsSwitchSlider />
                      </SettingsSwitch>
                    </SettingsControl>
                  </SettingsRow>
                  
                  <SettingsRow>
                    <SettingsLabel>Workflow-Benachrichtigungen</SettingsLabel>
                    <SettingsControl>
                      <SettingsSwitch>
                        <SettingsSwitchInput
                          type="checkbox"
                          checked={settings.notifications.types.workflows}
                          onChange={(e) => updateNotifications({ 
                            types: { 
                              ...settings.notifications.types, 
                              workflows: e.target.checked 
                            } 
                          })}
                        />
                        <SettingsSwitchSlider />
                      </SettingsSwitch>
                    </SettingsControl>
                  </SettingsRow>
                  
                  <SettingsRow>
                    <SettingsLabel>Sicherheits-Benachrichtigungen</SettingsLabel>
                    <SettingsControl>
                      <SettingsSwitch>
                        <SettingsSwitchInput
                          type="checkbox"
                          checked={settings.notifications.types.security}
                          onChange={(e) => updateNotifications({ 
                            types: { 
                              ...settings.notifications.types, 
                              security: e.target.checked 
                            } 
                          })}
                        />
                        <SettingsSwitchSlider />
                      </SettingsSwitch>
                    </SettingsControl>
                  </SettingsRow>
                </SettingsControls>
              </SettingsGroup>
            )}
          </SettingsSection>
        );
      
      case 'assistant':
        return (
          <SettingsSection>
            <SettingsSectionTitle>KI-Assistent</SettingsSectionTitle>
            
            <SettingsGroup>
              <SettingsGroupTitle>Assistent-Einstellungen</SettingsGroupTitle>
              <SettingsGroupDescription>
                Konfigurieren Sie den KI-Assistenten nach Ihren Bedürfnissen.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Assistent aktivieren</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.assistant.enabled}
                        onChange={(e) => updateAssistant({ enabled: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
                
                {settings.assistant.enabled && (
                  <>
                    <SettingsRow>
                      <SettingsLabel>Vorschläge anzeigen</SettingsLabel>
                      <SettingsControl>
                        <SettingsSwitch>
                          <SettingsSwitchInput
                            type="checkbox"
                            checked={settings.assistant.suggestions}
                            onChange={(e) => updateAssistant({ suggestions: e.target.checked })}
                          />
                          <SettingsSwitchSlider />
                        </SettingsSwitch>
                      </SettingsControl>
                    </SettingsRow>
                    
                    <SettingsRow>
                      <SettingsLabel>Automatische Vervollständigung</SettingsLabel>
                      <SettingsControl>
                        <SettingsSwitch>
                          <SettingsSwitchInput
                            type="checkbox"
                            checked={settings.assistant.autoComplete}
                            onChange={(e) => updateAssistant({ autoComplete: e.target.checked })}
                          />
                          <SettingsSwitchSlider />
                        </SettingsSwitch>
                      </SettingsControl>
                    </SettingsRow>
                    
                    <SettingsRow>
                      <SettingsLabel>Sprachsteuerung</SettingsLabel>
                      <SettingsControl>
                        <SettingsSwitch>
                          <SettingsSwitchInput
                            type="checkbox"
                            checked={settings.assistant.voice}
                            onChange={(e) => updateAssistant({ voice: e.target.checked })}
                          />
                          <SettingsSwitchSlider />
                        </SettingsSwitch>
                      </SettingsControl>
                    </SettingsRow>
                  </>
                )}
              </SettingsControls>
            </SettingsGroup>
          </SettingsSection>
        );
      
      case 'services':
        return (
          <SettingsSection>
            <SettingsSectionTitle>Dienste</SettingsSectionTitle>
            
            <SettingsGroup>
              <SettingsGroupTitle>Dienste-Einstellungen</SettingsGroupTitle>
              <SettingsGroupDescription>
                Konfigurieren Sie die Anzeige und Verwaltung von Diensten.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Standard-Ansicht</SettingsLabel>
                  <SettingsControl>
                    <SettingsButton
                      $active={settings.services.defaultView === 'grid'}
                      onClick={() => updateServices({ defaultView: 'grid' })}
                    >
                      Raster
                    </SettingsButton>
                    <SettingsButton
                      $active={settings.services.defaultView === 'list'}
                      onClick={() => updateServices({ defaultView: 'list' })}
                    >
                      Liste
                    </SettingsButton>
                  </SettingsControl>
                </SettingsRow>
              </SettingsControls>
            </SettingsGroup>
          </SettingsSection>
        );
      
      case 'security':
        return (
          <SettingsSection>
            <SettingsSectionTitle>Sicherheit</SettingsSectionTitle>
            
            <SettingsGroup>
              <SettingsGroupTitle>Sicherheitseinstellungen</SettingsGroupTitle>
              <SettingsGroupDescription>
                Konfigurieren Sie die Sicherheitseinstellungen für Ihr Konto.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Sitzungs-Timeout: {settings.security.sessionTimeout} Minuten</SettingsLabel>
                  <SettingsControl>
                    <SettingsSlider
                      type="range"
                      min="5"
                      max="120"
                      step="5"
                      value={settings.security.sessionTimeout}
                      onChange={(e) => updateSecurity({ sessionTimeout: parseInt(e.target.value) })}
                    />
                  </SettingsControl>
                </SettingsRow>
                
                <SettingsRow>
                  <SettingsLabel>Zwei-Faktor-Authentifizierung</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.security.twoFactorAuth}
                        onChange={(e) => updateSecurity({ twoFactorAuth: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
              </SettingsControls>
            </SettingsGroup>
          </SettingsSection>
        );
      
      case 'advanced':
        return (
          <SettingsSection>
            <SettingsSectionTitle>Erweitert</SettingsSectionTitle>
            
            <SettingsGroup>
              <SettingsGroupTitle>Erweiterte Einstellungen</SettingsGroupTitle>
              <SettingsGroupDescription>
                Konfigurieren Sie erweiterte Einstellungen für die Anwendung.
              </SettingsGroupDescription>
              <SettingsControls>
                <SettingsRow>
                  <SettingsLabel>Entwicklermodus</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.advanced.developerMode}
                        onChange={(e) => updateAdvanced({ developerMode: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
                
                <SettingsRow>
                  <SettingsLabel>Experimentelle Funktionen</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.advanced.experimentalFeatures}
                        onChange={(e) => updateAdvanced({ experimentalFeatures: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
                
                <SettingsRow>
                  <SettingsLabel>Logging</SettingsLabel>
                  <SettingsControl>
                    <SettingsSwitch>
                      <SettingsSwitchInput
                        type="checkbox"
                        checked={settings.advanced.logging}
                        onChange={(e) => updateAdvanced({ logging: e.target.checked })}
                      />
                      <SettingsSwitchSlider />
                    </SettingsSwitch>
                  </SettingsControl>
                </SettingsRow>
              </SettingsControls>
            </SettingsGroup>
          </SettingsSection>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <Container size="xl">
      <PageContainer>
        <PageHeader>
          <PageTitle>Benutzereinstellungen</PageTitle>
        </PageHeader>
        
        <Card>
          <SettingsContainer>
            <SettingsSidebar>
              <SettingsNavigation>
                <SettingsNavItem
                  $active={activeTab === 'appearance'}
                  onClick={() => setActiveTab('appearance')}
                >
                  <SettingsNavIcon>🎨</SettingsNavIcon>
                  Erscheinungsbild
                </SettingsNavItem>
                <SettingsNavItem
                  $active={activeTab === 'dashboard'}
                  onClick={() => setActiveTab('dashboard')}
                >
                  <SettingsNavIcon>📊</SettingsNavIcon>
                  Dashboard
                </SettingsNavItem>
                <SettingsNavItem
                  $active={activeTab === 'notifications'}
                  onClick={() => setActiveTab('notifications')}
                >
                  <SettingsNavIcon>🔔</SettingsNavIcon>
                  Benachrichtigungen
                </SettingsNavItem>
                <SettingsNavItem
                  $active={activeTab === 'assistant'}
                  onClick={() => setActiveTab('assistant')}
                >
                  <SettingsNavIcon>🤖</SettingsNavIcon>
                  KI-Assistent
                </SettingsNavItem>
                <SettingsNavItem
                  $active={activeTab === 'services'}
                  onClick={() => setActiveTab('services')}
                >
                  <SettingsNavIcon>🌐</SettingsNavIcon>
                  Dienste
                </SettingsNavItem>
                <SettingsNavItem
                  $active={activeTab === 'security'}
                  onClick={() => setActiveTab('security')}
                >
                  <SettingsNavIcon>🔒</SettingsNavIcon>
                  Sicherheit
                </SettingsNavItem>
                <SettingsNavItem
                  $active={activeTab === 'advanced'}
                  onClick={() => setActiveTab('advanced')}
                >
                  <SettingsNavIcon>⚙️</SettingsNavIcon>
                  Erweitert
                </SettingsNavItem>
              </SettingsNavigation>
            </SettingsSidebar>
            
            <SettingsContent>
              {renderTabContent()}
              
              <SettingsActions>
                <Button
                  variant="outlined"
                  onClick={resetSettings}
                >
                  Zurücksetzen
                </Button>
              </SettingsActions>
            </SettingsContent>
          </SettingsContainer>
        </Card>
      </PageContainer>
    </Container>
  );
};

export default UserSettings;