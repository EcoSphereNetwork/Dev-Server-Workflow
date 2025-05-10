/**
 * WorkflowList Component
 * 
 * A component for listing and filtering workflows
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Button, Input, Card, Spinner, Badge } from '../../design-system';
import { useNavigate } from 'react-router-dom';

// Types for workflows
export interface Workflow {
  id: string;
  name: string;
  description: string;
  active: boolean;
  lastExecuted?: Date;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

// Props for WorkflowList
interface WorkflowListProps {
  onSelectWorkflow: (workflow: Workflow) => void;
}

// Styled components
const ListContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const SearchContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const SearchInput = styled(Input)`
  flex: 1;
`;

const FilterContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.md};
  flex-wrap: wrap;
`;

const FilterButton = styled(Button)<{ $active: boolean }>`
  opacity: ${props => props.$active ? 1 : 0.7};
`;

const WorkflowCard = styled(Card)<{ $active: boolean }>`
  padding: ${props => props.theme.spacing.md};
  cursor: pointer;
  border-left: 4px solid ${props => props.$active ? props.theme.colors.success.main : props.theme.colors.warning.main};
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const WorkflowHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const WorkflowTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const WorkflowStatus = styled.div<{ $active: boolean }>`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.$active ? props.theme.colors.success.main : props.theme.colors.warning.main};
`;

const WorkflowDescription = styled.p`
  margin: 0 0 ${props => props.theme.spacing.md} 0;
  color: ${props => props.theme.colors.text.secondary};
`;

const WorkflowMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const WorkflowTags = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
  flex-wrap: wrap;
`;

const WorkflowDate = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.text.secondary};
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xl};
`;

const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: ${props => props.theme.spacing.sm};
  margin-top: ${props => props.theme.spacing.lg};
`;

// Mock API function to fetch workflows
const fetchWorkflows = async (
  search: string = '',
  filter: string = 'all',
  page: number = 1,
  pageSize: number = 10
): Promise<{ workflows: Workflow[], total: number }> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Mock data
  const mockWorkflows: Workflow[] = [
    {
      id: '1',
      name: 'GitHub to OpenProject',
      description: 'Synchronizes issues and pull requests between GitHub/GitLab and OpenProject',
      active: true,
      lastExecuted: new Date(Date.now() - 3600000),
      tags: ['github', 'openproject', 'sync'],
      createdAt: new Date(Date.now() - 7 * 24 * 3600000),
      updatedAt: new Date(Date.now() - 24 * 3600000)
    },
    {
      id: '2',
      name: 'Document Synchronization',
      description: 'Synchronizes documents between AFFiNE/AppFlowy, GitHub and OpenProject',
      active: true,
      lastExecuted: new Date(Date.now() - 7200000),
      tags: ['document', 'sync', 'github'],
      createdAt: new Date(Date.now() - 14 * 24 * 3600000),
      updatedAt: new Date(Date.now() - 2 * 24 * 3600000)
    },
    {
      id: '3',
      name: 'OpenHands Integration',
      description: 'Integrates OpenHands for AI-assisted issue resolution',
      active: false,
      tags: ['openhands', 'ai', 'github'],
      createdAt: new Date(Date.now() - 21 * 24 * 3600000),
      updatedAt: new Date(Date.now() - 5 * 24 * 3600000)
    },
    {
      id: '4',
      name: 'Discord Notifications',
      description: 'Sends notifications about GitHub/GitLab events to Discord',
      active: true,
      lastExecuted: new Date(Date.now() - 1800000),
      tags: ['discord', 'notifications', 'github'],
      createdAt: new Date(Date.now() - 30 * 24 * 3600000),
      updatedAt: new Date(Date.now() - 3 * 24 * 3600000)
    },
    {
      id: '5',
      name: 'Time Tracking',
      description: 'Extracts time tracking information from commit messages and transfers it to OpenProject',
      active: false,
      tags: ['time-tracking', 'github', 'openproject'],
      createdAt: new Date(Date.now() - 45 * 24 * 3600000),
      updatedAt: new Date(Date.now() - 10 * 24 * 3600000)
    }
  ];
  
  // Filter by search term
  let filtered = mockWorkflows;
  if (search) {
    const searchLower = search.toLowerCase();
    filtered = filtered.filter(workflow => 
      workflow.name.toLowerCase().includes(searchLower) || 
      workflow.description.toLowerCase().includes(searchLower) ||
      workflow.tags.some(tag => tag.toLowerCase().includes(searchLower))
    );
  }
  
  // Filter by status
  if (filter === 'active') {
    filtered = filtered.filter(workflow => workflow.active);
  } else if (filter === 'inactive') {
    filtered = filtered.filter(workflow => !workflow.active);
  }
  
  // Calculate pagination
  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const paginatedWorkflows = filtered.slice(start, end);
  
  return { workflows: paginatedWorkflows, total };
};

// Format date to relative time
const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  
  if (diffDay > 0) {
    return `${diffDay} ${diffDay === 1 ? 'day' : 'days'} ago`;
  } else if (diffHour > 0) {
    return `${diffHour} ${diffHour === 1 ? 'hour' : 'hours'} ago`;
  } else if (diffMin > 0) {
    return `${diffMin} ${diffMin === 1 ? 'minute' : 'minutes'} ago`;
  } else {
    return 'just now';
  }
};

// WorkflowList component
export const WorkflowList: React.FC<WorkflowListProps> = ({ onSelectWorkflow }) => {
  // State
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [totalWorkflows, setTotalWorkflows] = useState(0);
  const pageSize = 10;
  
  const navigate = useNavigate();
  
  // Load workflows
  useEffect(() => {
    const loadWorkflows = async () => {
      setLoading(true);
      try {
        const { workflows, total } = await fetchWorkflows(search, filter, page, pageSize);
        setWorkflows(workflows);
        setTotalWorkflows(total);
      } catch (error) {
        console.error('Error loading workflows:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadWorkflows();
  }, [search, filter, page]);
  
  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    setPage(1); // Reset to first page when searching
  };
  
  // Handle filter change
  const handleFilterChange = (newFilter: string) => {
    setFilter(newFilter);
    setPage(1); // Reset to first page when filtering
  };
  
  // Handle workflow selection
  const handleSelectWorkflow = (workflow: Workflow) => {
    onSelectWorkflow(workflow);
  };
  
  // Handle create new workflow
  const handleCreateWorkflow = () => {
    navigate('/workflows/new');
  };
  
  // Calculate total pages
  const totalPages = Math.ceil(totalWorkflows / pageSize);
  
  return (
    <ListContainer>
      <SearchContainer>
        <SearchInput
          placeholder="Search workflows..."
          value={search}
          onChange={handleSearch}
          icon="search"
        />
        <Button
          variant="primary"
          onClick={handleCreateWorkflow}
        >
          New Workflow
        </Button>
      </SearchContainer>
      
      <FilterContainer>
        <FilterButton
          variant="text"
          size="sm"
          $active={filter === 'all'}
          onClick={() => handleFilterChange('all')}
        >
          All
        </FilterButton>
        <FilterButton
          variant="text"
          size="sm"
          $active={filter === 'active'}
          onClick={() => handleFilterChange('active')}
        >
          Active
        </FilterButton>
        <FilterButton
          variant="text"
          size="sm"
          $active={filter === 'inactive'}
          onClick={() => handleFilterChange('inactive')}
        >
          Inactive
        </FilterButton>
      </FilterContainer>
      
      {loading ? (
        <LoadingContainer>
          <Spinner size="lg" />
        </LoadingContainer>
      ) : workflows.length === 0 ? (
        <EmptyState>
          <h3>No workflows found</h3>
          <p>Try adjusting your search or filter criteria, or create a new workflow.</p>
          <Button
            variant="primary"
            onClick={handleCreateWorkflow}
          >
            Create Workflow
          </Button>
        </EmptyState>
      ) : (
        <>
          {workflows.map(workflow => (
            <WorkflowCard
              key={workflow.id}
              $active={workflow.active}
              onClick={() => handleSelectWorkflow(workflow)}
            >
              <WorkflowHeader>
                <WorkflowTitle>{workflow.name}</WorkflowTitle>
                <WorkflowStatus $active={workflow.active}>
                  {workflow.active ? 'Active' : 'Inactive'}
                </WorkflowStatus>
              </WorkflowHeader>
              
              <WorkflowDescription>{workflow.description}</WorkflowDescription>
              
              <WorkflowMeta>
                <WorkflowTags>
                  {workflow.tags.map(tag => (
                    <Badge key={tag} color="secondary">{tag}</Badge>
                  ))}
                </WorkflowTags>
                
                <WorkflowDate>
                  {workflow.lastExecuted ? (
                    <>Last run: {formatRelativeTime(workflow.lastExecuted)}</>
                  ) : (
                    <>Updated: {formatRelativeTime(workflow.updatedAt)}</>
                  )}
                </WorkflowDate>
              </WorkflowMeta>
            </WorkflowCard>
          ))}
          
          {totalPages > 1 && (
            <PaginationContainer>
              <Button
                variant="outlined"
                size="sm"
                onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              
              <span>
                Page {page} of {totalPages}
              </span>
              
              <Button
                variant="outlined"
                size="sm"
                onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages}
              >
                Next
              </Button>
            </PaginationContainer>
          )}
        </>
      )}
    </ListContainer>
  );
};

export default WorkflowList;