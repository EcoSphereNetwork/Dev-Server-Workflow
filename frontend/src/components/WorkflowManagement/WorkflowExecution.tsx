/**
 * WorkflowExecution Component
 * 
 * A component for monitoring workflow executions
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Button, Card, Spinner, Badge, Tabs, Tab } from '../../design-system';
import { Workflow } from './WorkflowList';

// Types for workflow executions
interface WorkflowExecution {
  id: string;
  workflowId: string;
  workflowName: string;
  status: 'running' | 'completed' | 'error' | 'waiting';
  startTime: Date;
  endTime?: Date;
  duration?: number;
  nodes: {
    id: string;
    name: string;
    type: string;
    status: 'pending' | 'running' | 'completed' | 'error';
    startTime?: Date;
    endTime?: Date;
    input?: any;
    output?: any;
    error?: string;
  }[];
  error?: string;
}

// Props for WorkflowExecution
interface WorkflowExecutionProps {
  workflow: Workflow;
  onClose: () => void;
}

// Styled components
const ExecutionContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const ExecutionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ExecutionTitle = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ExecutionActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
`;

const ExecutionSummary = styled(Card)`
  padding: ${props => props.theme.spacing.md};
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const SummaryLabel = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.text.secondary};
`;

const SummaryValue = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const StatusBadge = styled(Badge)<{ $status: string }>`
  text-transform: capitalize;
`;

const ExecutionProgress = styled.div`
  height: 8px;
  background-color: ${props => props.theme.colors.background.default};
  border-radius: ${props => props.theme.borderRadius.full};
  overflow: hidden;
  margin-top: ${props => props.theme.spacing.sm};
`;

const ProgressBar = styled.div<{ $progress: number; $status: string }>`
  height: 100%;
  width: ${props => `${props.$progress}%`};
  background-color: ${props => {
    switch (props.$status) {
      case 'completed':
        return props.theme.colors.success.main;
      case 'error':
        return props.theme.colors.error;
      case 'running':
        return props.theme.colors.primary;
      default:
        return props.theme.colors.warning.main;
    }
  }};
  transition: width 0.3s ease;
`;

const TabContent = styled.div`
  padding: ${props => props.theme.spacing.md} 0;
`;

const NodesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const NodeCard = styled(Card)<{ $status: string }>`
  padding: ${props => props.theme.spacing.md};
  border-left: 4px solid ${props => {
    switch (props.$status) {
      case 'completed':
        return props.theme.colors.success.main;
      case 'error':
        return props.theme.colors.error;
      case 'running':
        return props.theme.colors.primary;
      default:
        return props.theme.colors.divider;
    }
  }};
`;

const NodeHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const NodeTitle = styled.h4`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const NodeType = styled.span`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  font-weight: ${props => props.theme.typography.fontWeight.regular};
`;

const NodeDetails = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

const NodeTiming = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.xs};
`;

const NodeError = styled.div`
  margin-top: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.error + '10'};
  border-left: 2px solid ${props => props.theme.colors.error};
  color: ${props => props.theme.colors.error};
  font-size: ${props => props.theme.typography.fontSize.sm};
  white-space: pre-wrap;
`;

const DataViewer = styled.pre`
  background-color: ${props => props.theme.colors.background.default};
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  overflow: auto;
  font-size: ${props => props.theme.typography.fontSize.xs};
  margin: ${props => props.theme.spacing.sm} 0;
  max-height: 200px;
`;

const LogsContainer = styled.div`
  background-color: ${props => props.theme.colors.background.default};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-family: monospace;
  font-size: ${props => props.theme.typography.fontSize.sm};
  white-space: pre-wrap;
  overflow: auto;
  max-height: 400px;
`;

const LogEntry = styled.div<{ $level: string }>`
  margin-bottom: ${props => props.theme.spacing.xs};
  color: ${props => {
    switch (props.$level) {
      case 'error':
        return props.theme.colors.error;
      case 'warning':
        return props.theme.colors.warning.main;
      case 'info':
        return props.theme.colors.info;
      default:
        return props.theme.colors.text.primary;
    }
  }};
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xl};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.text.secondary};
`;

// Mock API function to fetch workflow executions
const fetchWorkflowExecutions = async (workflowId: string): Promise<WorkflowExecution[]> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock data
  const mockExecutions: WorkflowExecution[] = [
    {
      id: 'exec-1',
      workflowId: workflowId,
      workflowName: 'GitHub to OpenProject',
      status: 'completed',
      startTime: new Date(Date.now() - 3600000),
      endTime: new Date(Date.now() - 3590000),
      duration: 10000,
      nodes: [
        {
          id: 'node-1',
          name: 'GitHub Trigger',
          type: 'Trigger',
          status: 'completed',
          startTime: new Date(Date.now() - 3600000),
          endTime: new Date(Date.now() - 3598000),
          input: { event: 'issue.created' },
          output: { issue: { id: 123, title: 'New Issue' } }
        },
        {
          id: 'node-2',
          name: 'Filter Issues',
          type: 'Logic',
          status: 'completed',
          startTime: new Date(Date.now() - 3598000),
          endTime: new Date(Date.now() - 3595000),
          input: { issue: { id: 123, title: 'New Issue' } },
          output: { issue: { id: 123, title: 'New Issue' } }
        },
        {
          id: 'node-3',
          name: 'OpenProject Create',
          type: 'Action',
          status: 'completed',
          startTime: new Date(Date.now() - 3595000),
          endTime: new Date(Date.now() - 3590000),
          input: { issue: { id: 123, title: 'New Issue' } },
          output: { workPackage: { id: 456, title: 'New Issue' } }
        }
      ]
    },
    {
      id: 'exec-2',
      workflowId: workflowId,
      workflowName: 'GitHub to OpenProject',
      status: 'error',
      startTime: new Date(Date.now() - 7200000),
      endTime: new Date(Date.now() - 7195000),
      duration: 5000,
      nodes: [
        {
          id: 'node-1',
          name: 'GitHub Trigger',
          type: 'Trigger',
          status: 'completed',
          startTime: new Date(Date.now() - 7200000),
          endTime: new Date(Date.now() - 7198000),
          input: { event: 'issue.created' },
          output: { issue: { id: 124, title: 'Another Issue' } }
        },
        {
          id: 'node-2',
          name: 'Filter Issues',
          type: 'Logic',
          status: 'completed',
          startTime: new Date(Date.now() - 7198000),
          endTime: new Date(Date.now() - 7196000),
          input: { issue: { id: 124, title: 'Another Issue' } },
          output: { issue: { id: 124, title: 'Another Issue' } }
        },
        {
          id: 'node-3',
          name: 'OpenProject Create',
          type: 'Action',
          status: 'error',
          startTime: new Date(Date.now() - 7196000),
          endTime: new Date(Date.now() - 7195000),
          input: { issue: { id: 124, title: 'Another Issue' } },
          error: 'API Error: OpenProject API returned 401 Unauthorized'
        }
      ],
      error: 'Execution failed at node "OpenProject Create": API Error: OpenProject API returned 401 Unauthorized'
    },
    {
      id: 'exec-3',
      workflowId: workflowId,
      workflowName: 'GitHub to OpenProject',
      status: 'running',
      startTime: new Date(Date.now() - 60000),
      nodes: [
        {
          id: 'node-1',
          name: 'GitHub Trigger',
          type: 'Trigger',
          status: 'completed',
          startTime: new Date(Date.now() - 60000),
          endTime: new Date(Date.now() - 58000),
          input: { event: 'issue.created' },
          output: { issue: { id: 125, title: 'New Running Issue' } }
        },
        {
          id: 'node-2',
          name: 'Filter Issues',
          type: 'Logic',
          status: 'completed',
          startTime: new Date(Date.now() - 58000),
          endTime: new Date(Date.now() - 55000),
          input: { issue: { id: 125, title: 'New Running Issue' } },
          output: { issue: { id: 125, title: 'New Running Issue' } }
        },
        {
          id: 'node-3',
          name: 'OpenProject Create',
          type: 'Action',
          status: 'running',
          startTime: new Date(Date.now() - 55000),
          input: { issue: { id: 125, title: 'New Running Issue' } }
        }
      ]
    }
  ];
  
  return mockExecutions;
};

// Mock API function to fetch execution logs
const fetchExecutionLogs = async (executionId: string): Promise<{ timestamp: Date; level: string; message: string }[]> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Mock data
  const mockLogs = [
    { timestamp: new Date(Date.now() - 3600000), level: 'info', message: 'Workflow execution started' },
    { timestamp: new Date(Date.now() - 3599000), level: 'info', message: 'Node "GitHub Trigger" started' },
    { timestamp: new Date(Date.now() - 3598500), level: 'debug', message: 'Received webhook event: issue.created' },
    { timestamp: new Date(Date.now() - 3598000), level: 'info', message: 'Node "GitHub Trigger" completed' },
    { timestamp: new Date(Date.now() - 3597500), level: 'info', message: 'Node "Filter Issues" started' },
    { timestamp: new Date(Date.now() - 3596000), level: 'debug', message: 'Applying filter: label == "bug"' },
    { timestamp: new Date(Date.now() - 3595500), level: 'debug', message: 'Filter result: true' },
    { timestamp: new Date(Date.now() - 3595000), level: 'info', message: 'Node "Filter Issues" completed' },
    { timestamp: new Date(Date.now() - 3594500), level: 'info', message: 'Node "OpenProject Create" started' },
    { timestamp: new Date(Date.now() - 3593000), level: 'debug', message: 'Creating work package in OpenProject' },
    { timestamp: new Date(Date.now() - 3592000), level: 'debug', message: 'Work package created with ID: 456' },
    { timestamp: new Date(Date.now() - 3591000), level: 'info', message: 'Node "OpenProject Create" completed' },
    { timestamp: new Date(Date.now() - 3590000), level: 'info', message: 'Workflow execution completed successfully' }
  ];
  
  if (executionId === 'exec-2') {
    mockLogs.push(
      { timestamp: new Date(Date.now() - 7195500), level: 'error', message: 'API Error: OpenProject API returned 401 Unauthorized' },
      { timestamp: new Date(Date.now() - 7195000), level: 'error', message: 'Workflow execution failed' }
    );
  }
  
  return mockLogs;
};

// Format date to time string
const formatTime = (date: Date): string => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

// Format duration in milliseconds to human-readable string
const formatDuration = (ms: number): string => {
  if (ms < 1000) {
    return `${ms}ms`;
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(1)}s`;
  } else {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return `${minutes}m ${seconds}s`;
  }
};

// Calculate progress percentage
const calculateProgress = (execution: WorkflowExecution): number => {
  if (execution.status === 'completed') return 100;
  if (execution.status === 'error') return 100;
  
  const totalNodes = execution.nodes.length;
  const completedNodes = execution.nodes.filter(node => 
    node.status === 'completed' || node.status === 'error'
  ).length;
  
  return Math.round((completedNodes / totalNodes) * 100);
};

// WorkflowExecution component
export const WorkflowExecution: React.FC<WorkflowExecutionProps> = ({ workflow, onClose }) => {
  // State
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [logs, setLogs] = useState<{ timestamp: Date; level: string; message: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Load executions
  useEffect(() => {
    const loadExecutions = async () => {
      setLoading(true);
      try {
        const data = await fetchWorkflowExecutions(workflow.id);
        setExecutions(data);
        
        // Select the most recent execution by default
        if (data.length > 0) {
          setSelectedExecution(data[0]);
        }
      } catch (error) {
        console.error('Error loading executions:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadExecutions();
  }, [workflow.id]);
  
  // Load logs when selected execution changes
  useEffect(() => {
    if (!selectedExecution) return;
    
    const loadLogs = async () => {
      setLoadingLogs(true);
      try {
        const data = await fetchExecutionLogs(selectedExecution.id);
        setLogs(data);
      } catch (error) {
        console.error('Error loading logs:', error);
      } finally {
        setLoadingLogs(false);
      }
    };
    
    loadLogs();
  }, [selectedExecution]);
  
  // Handle execution selection
  const handleSelectExecution = (execution: WorkflowExecution) => {
    setSelectedExecution(execution);
  };
  
  // Get status color
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      case 'running':
        return 'primary';
      default:
        return 'warning';
    }
  };
  
  return (
    <ExecutionContainer>
      <ExecutionHeader>
        <ExecutionTitle>Workflow Executions: {workflow.name}</ExecutionTitle>
        <ExecutionActions>
          <Button
            variant="outlined"
            onClick={onClose}
          >
            Back
          </Button>
          <Button
            variant="primary"
            disabled={!workflow.active}
          >
            Run Now
          </Button>
        </ExecutionActions>
      </ExecutionHeader>
      
      {loading ? (
        <LoadingContainer>
          <Spinner size="lg" />
        </LoadingContainer>
      ) : executions.length === 0 ? (
        <EmptyState>
          <h3>No executions found</h3>
          <p>This workflow hasn't been executed yet.</p>
          {workflow.active && (
            <Button
              variant="primary"
            >
              Run Now
            </Button>
          )}
        </EmptyState>
      ) : (
        <>
          {selectedExecution && (
            <ExecutionSummary>
              <SummaryRow>
                <SummaryLabel>Execution ID</SummaryLabel>
                <SummaryValue>{selectedExecution.id}</SummaryValue>
              </SummaryRow>
              
              <SummaryRow>
                <SummaryLabel>Status</SummaryLabel>
                <StatusBadge 
                  color={getStatusColor(selectedExecution.status)}
                  $status={selectedExecution.status}
                >
                  {selectedExecution.status}
                  {selectedExecution.status === 'running' && <Spinner size="xs" style={{ marginLeft: '8px' }} />}
                </StatusBadge>
              </SummaryRow>
              
              <SummaryRow>
                <SummaryLabel>Start Time</SummaryLabel>
                <SummaryValue>{formatTime(selectedExecution.startTime)}</SummaryValue>
              </SummaryRow>
              
              {selectedExecution.endTime && (
                <SummaryRow>
                  <SummaryLabel>End Time</SummaryLabel>
                  <SummaryValue>{formatTime(selectedExecution.endTime)}</SummaryValue>
                </SummaryRow>
              )}
              
              {selectedExecution.duration && (
                <SummaryRow>
                  <SummaryLabel>Duration</SummaryLabel>
                  <SummaryValue>{formatDuration(selectedExecution.duration)}</SummaryValue>
                </SummaryRow>
              )}
              
              <SummaryRow>
                <SummaryLabel>Progress</SummaryLabel>
                <SummaryValue>{calculateProgress(selectedExecution)}%</SummaryValue>
              </SummaryRow>
              
              <ExecutionProgress>
                <ProgressBar 
                  $progress={calculateProgress(selectedExecution)}
                  $status={selectedExecution.status}
                />
              </ExecutionProgress>
              
              {selectedExecution.error && (
                <NodeError>{selectedExecution.error}</NodeError>
              )}
            </ExecutionSummary>
          )}
          
          <Tabs activeTab={activeTab} onChange={setActiveTab}>
            <Tab id="overview" label="Overview" />
            <Tab id="nodes" label="Nodes" />
            <Tab id="logs" label="Logs" />
            <Tab id="history" label="History" />
          </Tabs>
          
          <TabContent>
            {activeTab === 'overview' && selectedExecution && (
              <div>
                <h3>Execution Summary</h3>
                <p>This workflow has {selectedExecution.nodes.length} nodes and was triggered at {formatTime(selectedExecution.startTime)}.</p>
                
                {selectedExecution.status === 'completed' && (
                  <p>The workflow completed successfully in {formatDuration(selectedExecution.duration || 0)}.</p>
                )}
                
                {selectedExecution.status === 'error' && (
                  <p>The workflow failed with an error: {selectedExecution.error}</p>
                )}
                
                {selectedExecution.status === 'running' && (
                  <p>The workflow is currently running. {calculateProgress(selectedExecution)}% complete.</p>
                )}
              </div>
            )}
            
            {activeTab === 'nodes' && selectedExecution && (
              <NodesList>
                {selectedExecution.nodes.map(node => (
                  <NodeCard key={node.id} $status={node.status}>
                    <NodeHeader>
                      <NodeTitle>
                        {node.name}
                        <NodeType>({node.type})</NodeType>
                      </NodeTitle>
                      <StatusBadge 
                        color={getStatusColor(node.status)}
                        $status={node.status}
                      >
                        {node.status}
                        {node.status === 'running' && <Spinner size="xs" style={{ marginLeft: '8px' }} />}
                      </StatusBadge>
                    </NodeHeader>
                    
                    <NodeTiming>
                      {node.startTime && (
                        <div>Started: {formatTime(node.startTime)}</div>
                      )}
                      {node.endTime && (
                        <div>Ended: {formatTime(node.endTime)}</div>
                      )}
                      {node.startTime && node.endTime && (
                        <div>Duration: {formatDuration(node.endTime.getTime() - node.startTime.getTime())}</div>
                      )}
                    </NodeTiming>
                    
                    <NodeDetails>
                      {node.input && (
                        <>
                          <div>Input:</div>
                          <DataViewer>{JSON.stringify(node.input, null, 2)}</DataViewer>
                        </>
                      )}
                      
                      {node.output && (
                        <>
                          <div>Output:</div>
                          <DataViewer>{JSON.stringify(node.output, null, 2)}</DataViewer>
                        </>
                      )}
                      
                      {node.error && (
                        <NodeError>{node.error}</NodeError>
                      )}
                    </NodeDetails>
                  </NodeCard>
                ))}
              </NodesList>
            )}
            
            {activeTab === 'logs' && (
              <>
                {loadingLogs ? (
                  <LoadingContainer>
                    <Spinner size="md" />
                  </LoadingContainer>
                ) : (
                  <LogsContainer>
                    {logs.map((log, index) => (
                      <LogEntry key={index} $level={log.level}>
                        [{formatTime(log.timestamp)}] [{log.level.toUpperCase()}] {log.message}
                      </LogEntry>
                    ))}
                  </LogsContainer>
                )}
              </>
            )}
            
            {activeTab === 'history' && (
              <NodesList>
                {executions.map(execution => (
                  <NodeCard 
                    key={execution.id} 
                    $status={execution.status}
                    onClick={() => handleSelectExecution(execution)}
                    style={{ cursor: 'pointer' }}
                  >
                    <NodeHeader>
                      <NodeTitle>
                        Execution {execution.id}
                      </NodeTitle>
                      <StatusBadge 
                        color={getStatusColor(execution.status)}
                        $status={execution.status}
                      >
                        {execution.status}
                        {execution.status === 'running' && <Spinner size="xs" style={{ marginLeft: '8px' }} />}
                      </StatusBadge>
                    </NodeHeader>
                    
                    <NodeTiming>
                      <div>Started: {formatTime(execution.startTime)}</div>
                      {execution.endTime && (
                        <div>Ended: {formatTime(execution.endTime)}</div>
                      )}
                      {execution.duration && (
                        <div>Duration: {formatDuration(execution.duration)}</div>
                      )}
                    </NodeTiming>
                    
                    {execution.error && (
                      <NodeError>{execution.error}</NodeError>
                    )}
                  </NodeCard>
                ))}
              </NodesList>
            )}
          </TabContent>
        </>
      )}
    </ExecutionContainer>
  );
};

export default WorkflowExecution;