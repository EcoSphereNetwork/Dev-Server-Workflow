// src/pages/Workflows.tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  Button, 
  Card, 
  Table, 
  Modal, 
  Input, 
  Select, 
  Spinner, 
  Alert,
  Badge,
  Tabs,
  TabView
} from '../components/SmolituxComponents';
import apiClient from '../api/client';
import { colors } from '../theme';

// Typen für die Workflow-Daten
interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
  type: string;
  lastRun: string | null;
  nextRun: string | null;
  createdAt: string;
  updatedAt: string;
  executionCount: number;
}

const WorkflowsContainer = styled.div`
  padding: 20px;
`;

const WorkflowsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const WorkflowsTitle = styled.h1`
  font-size: 1.5rem;
  margin: 0;
`;

const WorkflowsActions = styled.div`
  display: flex;
  gap: 10px;
`;

const StatusBadge = styled(Badge)<{ $status: 'active' | 'inactive' | 'error' }>`
  background-color: ${props => {
    switch (props.$status) {
      case 'active':
        return colors.success.main;
      case 'inactive':
        return colors.warning.main;
      case 'error':
        return colors.error.main;
      default:
        return colors.info.main;
    }
  }};
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
`;

const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    type: 'n8n',
  });

  useEffect(() => {
    const fetchWorkflows = async () => {
      try {
        setLoading(true);
        // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
        // const response = await apiClient.get('/workflows');
        // setWorkflows(response.data);
        
        // Simulierte Daten für die Entwicklung
        setWorkflows([
          {
            id: '1',
            name: 'GitHub Integration',
            description: 'Automatische Synchronisierung von GitHub-Issues',
            status: 'active',
            type: 'n8n',
            lastRun: '2025-05-08T12:30:00Z',
            nextRun: '2025-05-08T18:30:00Z',
            createdAt: '2025-04-15T10:00:00Z',
            updatedAt: '2025-05-01T14:20:00Z',
            executionCount: 128
          },
          {
            id: '2',
            name: 'Dokument-Verarbeitung',
            description: 'Extraktion von Daten aus Dokumenten mit KI',
            status: 'active',
            type: 'n8n',
            lastRun: '2025-05-08T10:15:00Z',
            nextRun: '2025-05-08T16:15:00Z',
            createdAt: '2025-04-20T09:30:00Z',
            updatedAt: '2025-05-05T11:45:00Z',
            executionCount: 87
          },
          {
            id: '3',
            name: 'Backup-Routine',
            description: 'Tägliches Backup aller Projektdaten',
            status: 'inactive',
            type: 'docker',
            lastRun: '2025-05-07T00:00:00Z',
            nextRun: null,
            createdAt: '2025-03-10T08:00:00Z',
            updatedAt: '2025-05-07T00:05:00Z',
            executionCount: 58
          },
          {
            id: '4',
            name: 'Fehlerüberwachung',
            description: 'Überwachung und Benachrichtigung bei Systemfehlern',
            status: 'error',
            type: 'docker',
            lastRun: '2025-05-08T05:00:00Z',
            nextRun: '2025-05-08T17:00:00Z',
            createdAt: '2025-04-01T15:30:00Z',
            updatedAt: '2025-05-08T05:05:00Z',
            executionCount: 112
          }
        ]);
      } catch (err: any) {
        setError('Fehler beim Laden der Workflows');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkflows();
  }, []);

  const handleAddWorkflow = async () => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // const response = await apiClient.post('/workflows', newWorkflow);
      // setWorkflows([...workflows, response.data]);
      
      // Simulierte Daten für die Entwicklung
      const newId = (workflows.length + 1).toString();
      const now = new Date().toISOString();
      setWorkflows([...workflows, {
        id: newId,
        name: newWorkflow.name,
        description: newWorkflow.description,
        status: 'inactive',
        type: newWorkflow.type,
        lastRun: null,
        nextRun: null,
        createdAt: now,
        updatedAt: now,
        executionCount: 0
      }]);
      
      setShowAddModal(false);
      setNewWorkflow({
        name: '',
        description: '',
        type: 'n8n',
      });
    } catch (err: any) {
      setError('Fehler beim Hinzufügen des Workflows');
      console.error(err);
    }
  };

  const handleDeleteWorkflow = async (id: string) => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.delete(`/workflows/${id}`);
      
      // Simulierte Daten für die Entwicklung
      setWorkflows(workflows.filter(workflow => workflow.id !== id));
    } catch (err: any) {
      setError('Fehler beim Löschen des Workflows');
      console.error(err);
    }
  };

  const handleActivateWorkflow = async (id: string) => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.post(`/workflows/${id}/activate`);
      
      // Simulierte Daten für die Entwicklung
      setWorkflows(workflows.map(workflow => 
        workflow.id === id ? { ...workflow, status: 'active' } : workflow
      ));
    } catch (err: any) {
      setError('Fehler beim Aktivieren des Workflows');
      console.error(err);
    }
  };

  const handleDeactivateWorkflow = async (id: string) => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.post(`/workflows/${id}/deactivate`);
      
      // Simulierte Daten für die Entwicklung
      setWorkflows(workflows.map(workflow => 
        workflow.id === id ? { ...workflow, status: 'inactive' } : workflow
      ));
    } catch (err: any) {
      setError('Fehler beim Deaktivieren des Workflows');
      console.error(err);
    }
  };

  const handleRunWorkflow = async (id: string) => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.post(`/workflows/${id}/run`);
      
      // Simulierte Daten für die Entwicklung
      const now = new Date().toISOString();
      setWorkflows(workflows.map(workflow => 
        workflow.id === id ? { 
          ...workflow, 
          lastRun: now,
          executionCount: workflow.executionCount + 1 
        } : workflow
      ));
    } catch (err: any) {
      setError('Fehler beim Ausführen des Workflows');
      console.error(err);
    }
  };

  if (loading && !workflows.length) {
    return (
      <WorkflowsContainer>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
          <Spinner />
        </div>
      </WorkflowsContainer>
    );
  }

  return (
    <WorkflowsContainer>
      <WorkflowsHeader>
        <WorkflowsTitle>Workflows</WorkflowsTitle>
        <WorkflowsActions>
          <Button variant="primary" onClick={() => setShowAddModal(true)}>
            Neuer Workflow
          </Button>
        </WorkflowsActions>
      </WorkflowsHeader>

      {error && (
        <Alert variant="error" style={{ marginBottom: '20px' }}>
          {error}
        </Alert>
      )}

      <Card>
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Beschreibung</th>
              <th>Status</th>
              <th>Typ</th>
              <th>Letzte Ausführung</th>
              <th>Nächste Ausführung</th>
              <th>Ausführungen</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {workflows.map((workflow) => (
              <tr key={workflow.id}>
                <td>{workflow.name}</td>
                <td>{workflow.description}</td>
                <td>
                  <StatusBadge $status={workflow.status}>
                    {workflow.status === 'active' ? 'Aktiv' : 
                     workflow.status === 'inactive' ? 'Inaktiv' : 'Fehler'}
                  </StatusBadge>
                </td>
                <td>{workflow.type}</td>
                <td>{workflow.lastRun ? new Date(workflow.lastRun).toLocaleString() : '-'}</td>
                <td>{workflow.nextRun ? new Date(workflow.nextRun).toLocaleString() : '-'}</td>
                <td>{workflow.executionCount}</td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <Button 
                      variant="primary" 
                      onClick={() => handleRunWorkflow(workflow.id)}
                      style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                    >
                      Ausführen
                    </Button>
                    
                    {workflow.status === 'inactive' && (
                      <Button 
                        variant="success" 
                        onClick={() => handleActivateWorkflow(workflow.id)}
                        style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                      >
                        Aktivieren
                      </Button>
                    )}
                    
                    {workflow.status === 'active' && (
                      <Button 
                        variant="warning" 
                        onClick={() => handleDeactivateWorkflow(workflow.id)}
                        style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                      >
                        Deaktivieren
                      </Button>
                    )}
                    
                    <Button 
                      variant="error" 
                      onClick={() => handleDeleteWorkflow(workflow.id)}
                      style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                    >
                      Löschen
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>

      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Neuen Workflow hinzufügen"
      >
        <div style={{ padding: '20px' }}>
          <Input
            label="Name"
            value={newWorkflow.name}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, name: e.target.value })}
            fullWidth
            style={{ marginBottom: '15px' }}
          />
          
          <Input
            label="Beschreibung"
            value={newWorkflow.description}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
            fullWidth
            style={{ marginBottom: '15px' }}
          />
          
          <Select
            label="Typ"
            value={newWorkflow.type}
            onChange={(e) => setNewWorkflow({ ...newWorkflow, type: e.target.value })}
            fullWidth
            style={{ marginBottom: '20px' }}
          >
            <option value="n8n">n8n</option>
            <option value="docker">Docker</option>
          </Select>
          
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Abbrechen
            </Button>
            <Button 
              variant="primary" 
              onClick={handleAddWorkflow}
              disabled={!newWorkflow.name}
            >
              Hinzufügen
            </Button>
          </div>
        </div>
      </Modal>
    </WorkflowsContainer>
  );
};

export default Workflows;