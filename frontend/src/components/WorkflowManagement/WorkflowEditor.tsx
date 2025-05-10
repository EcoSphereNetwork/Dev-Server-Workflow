/**
 * WorkflowEditor Component
 * 
 * A component for editing workflow details and configuration
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Button, Input, Textarea, Switch, Card, Spinner, Badge, Tabs, Tab } from '../../design-system';
import { Workflow } from './WorkflowList';

// Props for WorkflowEditor
interface WorkflowEditorProps {
  workflow?: Workflow;
  isNew?: boolean;
  onSave: (workflow: Workflow) => void;
  onCancel: () => void;
}

// Styled components
const EditorContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const EditorHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const EditorTitle = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const EditorActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
`;

const FormSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const FormRow = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
  flex: 1;
`;

const FormLabel = styled.label`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.text.primary};
`;

const FormHelp = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
`;

const TagsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.xs};
  margin-top: ${props => props.theme.spacing.xs};
`;

const TagInput = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
`;

const TabContent = styled.div`
  padding: ${props => props.theme.spacing.md} 0;
`;

const NodeContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.md};
`;

const NodeCard = styled(Card)`
  width: 200px;
  padding: ${props => props.theme.spacing.md};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const NodeIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.primary + '20'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const NodeTitle = styled.h4`
  margin: 0 0 ${props => props.theme.spacing.xs} 0;
  font-size: ${props => props.theme.typography.fontSize.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const NodeDescription = styled.p`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const ConnectionsContainer = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  border: 1px dashed ${props => props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.md};
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.text.secondary};
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xl};
`;

// Mock node types
const nodeTypes = [
  {
    id: 'github',
    name: 'GitHub',
    description: 'Connect to GitHub API',
    category: 'Trigger',
    icon: '🔄'
  },
  {
    id: 'gitlab',
    name: 'GitLab',
    description: 'Connect to GitLab API',
    category: 'Trigger',
    icon: '🔄'
  },
  {
    id: 'openproject',
    name: 'OpenProject',
    description: 'Connect to OpenProject API',
    category: 'Action',
    icon: '📋'
  },
  {
    id: 'discord',
    name: 'Discord',
    description: 'Send messages to Discord',
    category: 'Action',
    icon: '💬'
  },
  {
    id: 'filter',
    name: 'Filter',
    description: 'Filter data based on conditions',
    category: 'Logic',
    icon: '🔍'
  },
  {
    id: 'transform',
    name: 'Transform',
    description: 'Transform data structure',
    category: 'Logic',
    icon: '🔄'
  },
  {
    id: 'openhands',
    name: 'OpenHands',
    description: 'AI-assisted issue resolution',
    category: 'Action',
    icon: '🤖'
  },
  {
    id: 'http',
    name: 'HTTP Request',
    description: 'Make HTTP requests',
    category: 'Action',
    icon: '🌐'
  }
];

// WorkflowEditor component
export const WorkflowEditor: React.FC<WorkflowEditorProps> = ({ 
  workflow, 
  isNew = false, 
  onSave, 
  onCancel 
}) => {
  // Default empty workflow
  const emptyWorkflow: Workflow = {
    id: '',
    name: '',
    description: '',
    active: false,
    tags: [],
    createdAt: new Date(),
    updatedAt: new Date()
  };
  
  // State
  const [formData, setFormData] = useState<Workflow>(workflow || emptyWorkflow);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('details');
  const [newTag, setNewTag] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // Load workflow data
  useEffect(() => {
    if (workflow && !isNew) {
      setFormData(workflow);
    }
  }, [workflow, isNew]);
  
  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };
  
  // Handle switch change
  const handleSwitchChange = (checked: boolean) => {
    setFormData(prev => ({ ...prev, active: checked }));
  };
  
  // Handle add tag
  const handleAddTag = () => {
    if (!newTag.trim()) return;
    
    // Check if tag already exists
    if (formData.tags.includes(newTag.trim())) {
      setNewTag('');
      return;
    }
    
    setFormData(prev => ({
      ...prev,
      tags: [...prev.tags, newTag.trim()]
    }));
    setNewTag('');
  };
  
  // Handle remove tag
  const handleRemoveTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };
  
  // Handle tag input keydown
  const handleTagKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };
  
  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle save
  const handleSave = async () => {
    if (!validateForm()) return;
    
    setSaving(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Generate ID for new workflows
      const savedWorkflow: Workflow = {
        ...formData,
        id: isNew ? `new-${Date.now()}` : formData.id,
        updatedAt: new Date()
      };
      
      onSave(savedWorkflow);
    } catch (error) {
      console.error('Error saving workflow:', error);
    } finally {
      setSaving(false);
    }
  };
  
  return (
    <EditorContainer>
      <EditorHeader>
        <EditorTitle>{isNew ? 'Create New Workflow' : `Edit Workflow: ${formData.name}`}</EditorTitle>
        <EditorActions>
          <Button
            variant="outlined"
            onClick={onCancel}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? <Spinner size="sm" /> : isNew ? 'Create' : 'Save'}
          </Button>
        </EditorActions>
      </EditorHeader>
      
      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <Tab id="details" label="Details" />
        <Tab id="nodes" label="Nodes" />
        <Tab id="connections" label="Connections" />
        <Tab id="settings" label="Settings" />
      </Tabs>
      
      {loading ? (
        <LoadingContainer>
          <Spinner size="lg" />
        </LoadingContainer>
      ) : (
        <TabContent>
          {activeTab === 'details' && (
            <FormSection>
              <FormGroup>
                <FormLabel htmlFor="name">Workflow Name</FormLabel>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Enter workflow name"
                  error={errors.name}
                />
                {errors.name && <FormHelp>{errors.name}</FormHelp>}
              </FormGroup>
              
              <FormGroup>
                <FormLabel htmlFor="description">Description</FormLabel>
                <Textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Enter workflow description"
                  rows={3}
                  error={errors.description}
                />
                {errors.description && <FormHelp>{errors.description}</FormHelp>}
              </FormGroup>
              
              <FormRow>
                <FormGroup>
                  <FormLabel>Status</FormLabel>
                  <Switch
                    checked={formData.active}
                    onChange={handleSwitchChange}
                    label={formData.active ? 'Active' : 'Inactive'}
                  />
                  <FormHelp>Active workflows will run automatically when triggered</FormHelp>
                </FormGroup>
              </FormRow>
              
              <FormGroup>
                <FormLabel>Tags</FormLabel>
                <TagInput>
                  <Input
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyDown={handleTagKeyDown}
                    placeholder="Add tag and press Enter"
                  />
                  <Button
                    variant="outlined"
                    onClick={handleAddTag}
                    disabled={!newTag.trim()}
                  >
                    Add
                  </Button>
                </TagInput>
                <TagsContainer>
                  {formData.tags.map(tag => (
                    <Badge
                      key={tag}
                      color="secondary"
                      onRemove={() => handleRemoveTag(tag)}
                    >
                      {tag}
                    </Badge>
                  ))}
                  {formData.tags.length === 0 && (
                    <FormHelp>No tags added yet</FormHelp>
                  )}
                </TagsContainer>
              </FormGroup>
            </FormSection>
          )}
          
          {activeTab === 'nodes' && (
            <FormSection>
              <FormGroup>
                <FormLabel>Available Nodes</FormLabel>
                <FormHelp>Select nodes to add to your workflow</FormHelp>
                
                <NodeContainer>
                  {nodeTypes.map(node => (
                    <NodeCard key={node.id}>
                      <NodeIcon>{node.icon}</NodeIcon>
                      <NodeTitle>{node.name}</NodeTitle>
                      <NodeDescription>{node.description}</NodeDescription>
                      <Badge color="primary" style={{ marginTop: '8px' }}>{node.category}</Badge>
                    </NodeCard>
                  ))}
                </NodeContainer>
              </FormGroup>
            </FormSection>
          )}
          
          {activeTab === 'connections' && (
            <FormSection>
              <FormGroup>
                <FormLabel>Workflow Connections</FormLabel>
                <FormHelp>Connect nodes to create your workflow</FormHelp>
                
                <ConnectionsContainer>
                  <p>Add nodes from the Nodes tab to start building your workflow</p>
                </ConnectionsContainer>
              </FormGroup>
            </FormSection>
          )}
          
          {activeTab === 'settings' && (
            <FormSection>
              <FormGroup>
                <FormLabel htmlFor="execution-mode">Execution Mode</FormLabel>
                <select id="execution-mode" className="form-select">
                  <option value="sequential">Sequential</option>
                  <option value="parallel">Parallel</option>
                </select>
                <FormHelp>How the workflow nodes should be executed</FormHelp>
              </FormGroup>
              
              <FormGroup>
                <FormLabel htmlFor="timeout">Timeout (seconds)</FormLabel>
                <Input
                  id="timeout"
                  type="number"
                  min="0"
                  placeholder="300"
                />
                <FormHelp>Maximum execution time before the workflow is terminated</FormHelp>
              </FormGroup>
              
              <FormGroup>
                <FormLabel htmlFor="retry-attempts">Retry Attempts</FormLabel>
                <Input
                  id="retry-attempts"
                  type="number"
                  min="0"
                  placeholder="3"
                />
                <FormHelp>Number of retry attempts on failure</FormHelp>
              </FormGroup>
              
              <FormGroup>
                <FormLabel>Error Handling</FormLabel>
                <Switch
                  checked={true}
                  onChange={() => {}}
                  label="Continue on Error"
                />
                <FormHelp>If enabled, the workflow will continue execution even if a node fails</FormHelp>
              </FormGroup>
            </FormSection>
          )}
        </TabContent>
      )}
    </EditorContainer>
  );
};

export default WorkflowEditor;