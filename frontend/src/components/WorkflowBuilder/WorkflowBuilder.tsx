import React, { useState, useCallback, useRef } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { v4 as uuidv4 } from 'uuid';
import styled from 'styled-components';
import { tokens } from '../../design-system/tokens';

// Types
export interface NodeData {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: Record<string, any>;
  inputs: string[];
  outputs: string[];
}

export interface EdgeData {
  id: string;
  source: string;
  sourceHandle: string;
  target: string;
  targetHandle: string;
}

export interface WorkflowData {
  nodes: NodeData[];
  edges: EdgeData[];
}

interface NodeProps {
  node: NodeData;
  onNodeMove: (id: string, position: { x: number; y: number }) => void;
  onNodeSelect: (id: string) => void;
  isSelected: boolean;
  onConnect: (params: { source: string; sourceHandle: string; target: string; targetHandle: string }) => void;
}

interface HandleProps {
  id: string;
  type: 'source' | 'target';
  position: 'top' | 'right' | 'bottom' | 'left';
  nodeId: string;
  onConnect: (params: { source: string; sourceHandle: string; target: string; targetHandle: string }) => void;
}

interface EdgeProps {
  edge: EdgeData;
  sourcePosition: { x: number; y: number };
  targetPosition: { x: number; y: number };
  onEdgeClick: (id: string) => void;
}

interface CanvasProps {
  workflow: WorkflowData;
  onNodeMove: (id: string, position: { x: number; y: number }) => void;
  onNodeSelect: (id: string) => void;
  selectedNodeId: string | null;
  onConnect: (params: { source: string; sourceHandle: string; target: string; targetHandle: string }) => void;
  onEdgeSelect: (id: string) => void;
}

interface NodePaletteProps {
  onAddNode: (type: string, position: { x: number; y: number }) => void;
}

interface NodePaletteItemProps {
  type: string;
  label: string;
  onAddNode: (type: string, position: { x: number; y: number }) => void;
}

// Styled Components
const WorkflowBuilderContainer = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 600px;
  background-color: ${tokens.colors.background.default};
  border: 1px solid ${tokens.colors.divider};
  border-radius: ${tokens.borderRadius.md};
  overflow: hidden;
`;

const Sidebar = styled.div`
  width: 250px;
  background-color: ${tokens.colors.background.paper};
  border-right: 1px solid ${tokens.colors.divider};
  padding: ${tokens.spacing.md};
  overflow-y: auto;
`;

const CanvasContainer = styled.div`
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: ${tokens.colors.background.paper};
  background-image: radial-gradient(${tokens.colors.divider} 1px, transparent 1px);
  background-size: 20px 20px;
`;

const CanvasInner = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transform-origin: 0 0;
`;

const NodeContainer = styled.div<{ isSelected: boolean }>`
  position: absolute;
  background-color: ${props => props.isSelected ? tokens.colors.primary[50] : tokens.colors.background.paper};
  border: 2px solid ${props => props.isSelected ? tokens.colors.primary[500] : tokens.colors.divider};
  border-radius: ${tokens.borderRadius.md};
  padding: ${tokens.spacing.md};
  min-width: 150px;
  box-shadow: ${tokens.shadows.md};
  cursor: move;
  user-select: none;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: ${tokens.shadows.lg};
  }
`;

const NodeHeader = styled.div`
  font-weight: ${tokens.typography.fontWeight.medium};
  margin-bottom: ${tokens.spacing.sm};
  color: ${tokens.colors.text.primary};
`;

const HandleContainer = styled.div<{ position: string }>`
  position: absolute;
  ${props => props.position === 'top' && `
    top: -6px;
    left: 50%;
    transform: translateX(-50%);
  `}
  ${props => props.position === 'right' && `
    right: -6px;
    top: 50%;
    transform: translateY(-50%);
  `}
  ${props => props.position === 'bottom' && `
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
  `}
  ${props => props.position === 'left' && `
    left: -6px;
    top: 50%;
    transform: translateY(-50%);
  `}
`;

const HandleElement = styled.div<{ type: string }>`
  width: 12px;
  height: 12px;
  background-color: ${props => props.type === 'source' ? tokens.colors.primary[500] : tokens.colors.secondary[500]};
  border-radius: 50%;
  cursor: crosshair;
  
  &:hover {
    transform: scale(1.2);
  }
`;

const EdgeSvg = styled.svg`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
`;

const EdgePath = styled.path`
  fill: none;
  stroke: ${tokens.colors.primary[500]};
  stroke-width: 2;
  pointer-events: all;
  cursor: pointer;
  
  &:hover {
    stroke-width: 3;
    stroke: ${tokens.colors.primary[700]};
  }
`;

const NodePaletteList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${tokens.spacing.sm};
`;

const NodePaletteItemContainer = styled.div`
  padding: ${tokens.spacing.sm};
  background-color: ${tokens.colors.background.paper};
  border: 1px solid ${tokens.colors.divider};
  border-radius: ${tokens.borderRadius.sm};
  cursor: grab;
  user-select: none;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${tokens.colors.primary[50]};
    border-color: ${tokens.colors.primary[300]};
  }
`;

const PropertiesPanelContainer = styled.div`
  margin-top: ${tokens.spacing.lg};
  padding-top: ${tokens.spacing.md};
  border-top: 1px solid ${tokens.colors.divider};
`;

const PropertyGroup = styled.div`
  margin-bottom: ${tokens.spacing.md};
`;

const PropertyLabel = styled.div`
  font-size: ${tokens.typography.fontSize.sm};
  color: ${tokens.colors.text.secondary};
  margin-bottom: ${tokens.spacing.xs};
`;

const PropertyInput = styled.input`
  width: 100%;
  padding: ${tokens.spacing.xs} ${tokens.spacing.sm};
  border: 1px solid ${tokens.colors.divider};
  border-radius: ${tokens.borderRadius.sm};
  font-size: ${tokens.typography.fontSize.sm};
  
  &:focus {
    border-color: ${tokens.colors.primary[500]};
    outline: none;
  }
`;

const ToolbarContainer = styled.div`
  display: flex;
  padding: ${tokens.spacing.sm};
  background-color: ${tokens.colors.background.paper};
  border-bottom: 1px solid ${tokens.colors.divider};
`;

const ToolbarButton = styled.button`
  padding: ${tokens.spacing.xs} ${tokens.spacing.sm};
  background-color: ${tokens.colors.background.paper};
  border: 1px solid ${tokens.colors.divider};
  border-radius: ${tokens.borderRadius.sm};
  margin-right: ${tokens.spacing.sm};
  cursor: pointer;
  
  &:hover {
    background-color: ${tokens.colors.primary[50]};
  }
  
  &:active {
    background-color: ${tokens.colors.primary[100]};
  }
`;

// Components
const Handle: React.FC<HandleProps> = ({ id, type, position, nodeId, onConnect }) => {
  const [{ isOver }, drop] = useDrop({
    accept: 'handle',
    drop: (item: { id: string; nodeId: string; type: string }) => {
      if (item.type === 'source' && type === 'target') {
        onConnect({
          source: item.nodeId,
          sourceHandle: item.id,
          target: nodeId,
          targetHandle: id,
        });
      } else if (item.type === 'target' && type === 'source') {
        onConnect({
          source: nodeId,
          sourceHandle: id,
          target: item.nodeId,
          targetHandle: item.id,
        });
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  });

  const [{ isDragging }, drag] = useDrag({
    type: 'handle',
    item: { id, nodeId, type },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  return (
    <HandleContainer position={position}>
      <HandleElement
        ref={(node) => {
          drag(drop(node));
        }}
        type={type}
        style={{
          backgroundColor: isOver ? tokens.colors.primary[300] : type === 'source' ? tokens.colors.primary[500] : tokens.colors.secondary[500],
        }}
      />
    </HandleContainer>
  );
};

const Node: React.FC<NodeProps> = ({ node, onNodeMove, onNodeSelect, isSelected, onConnect }) => {
  const ref = useRef<HTMLDivElement>(null);

  const [{ isDragging }, drag] = useDrag({
    type: 'node',
    item: { id: node.id, type: node.type },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onNodeSelect(node.id);
  };

  drag(ref);

  return (
    <NodeContainer
      ref={ref}
      style={{
        left: node.position.x,
        top: node.position.y,
        opacity: isDragging ? 0.5 : 1,
      }}
      isSelected={isSelected}
      onClick={handleClick}
      data-node-id={node.id}
    >
      <NodeHeader>{node.type}</NodeHeader>
      <div>{node.data.label || 'Unnamed Node'}</div>
      
      {node.inputs.map((input) => (
        <Handle
          key={input}
          id={input}
          type="target"
          position="left"
          nodeId={node.id}
          onConnect={onConnect}
        />
      ))}
      
      {node.outputs.map((output) => (
        <Handle
          key={output}
          id={output}
          type="source"
          position="right"
          nodeId={node.id}
          onConnect={onConnect}
        />
      ))}
    </NodeContainer>
  );
};

const EdgeComponent: React.FC<EdgeProps> = ({ edge, sourcePosition, targetPosition, onEdgeClick }) => {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdgeClick(edge.id);
  };

  // Calculate the path for the edge
  const path = `M ${sourcePosition.x} ${sourcePosition.y} C ${sourcePosition.x + 50} ${sourcePosition.y}, ${targetPosition.x - 50} ${targetPosition.y}, ${targetPosition.x} ${targetPosition.y}`;

  return (
    <EdgePath
      d={path}
      onClick={handleClick}
    />
  );
};

const Canvas: React.FC<CanvasProps> = ({
  workflow,
  onNodeMove,
  onNodeSelect,
  selectedNodeId,
  onConnect,
  onEdgeSelect,
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleCanvasClick = () => {
    onNodeSelect('');
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    const newScale = Math.min(Math.max(0.1, scale + delta), 2);
    setScale(newScale);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      const dx = e.clientX - dragStart.x;
      const dy = e.clientY - dragStart.y;
      setPosition({
        x: position.x + dx,
        y: position.y + dy,
      });
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Calculate handle positions for edges
  const getHandlePosition = (nodeId: string, handleId: string, type: 'source' | 'target'): { x: number; y: number } => {
    const node = workflow.nodes.find((n) => n.id === nodeId);
    if (!node) return { x: 0, y: 0 };

    const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
    if (!nodeElement) return { x: 0, y: 0 };

    const nodeRect = nodeElement.getBoundingClientRect();
    const canvasRect = canvasRef.current?.getBoundingClientRect() || { left: 0, top: 0 };

    if (type === 'source') {
      return {
        x: (node.position.x + nodeRect.width) * scale + position.x,
        y: (node.position.y + nodeRect.height / 2) * scale + position.y,
      };
    } else {
      return {
        x: node.position.x * scale + position.x,
        y: (node.position.y + nodeRect.height / 2) * scale + position.y,
      };
    }
  };

  return (
    <CanvasContainer
      ref={canvasRef}
      onClick={handleCanvasClick}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <CanvasInner
        style={{
          transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
        }}
      >
        <EdgeSvg>
          {workflow.edges.map((edge) => (
            <EdgeComponent
              key={edge.id}
              edge={edge}
              sourcePosition={getHandlePosition(edge.source, edge.sourceHandle, 'source')}
              targetPosition={getHandlePosition(edge.target, edge.targetHandle, 'target')}
              onEdgeClick={onEdgeSelect}
            />
          ))}
        </EdgeSvg>
        
        {workflow.nodes.map((node) => (
          <Node
            key={node.id}
            node={node}
            onNodeMove={onNodeMove}
            onNodeSelect={onNodeSelect}
            isSelected={node.id === selectedNodeId}
            onConnect={onConnect}
          />
        ))}
      </CanvasInner>
    </CanvasContainer>
  );
};

const NodePaletteItem: React.FC<NodePaletteItemProps> = ({ type, label, onAddNode }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'new-node',
    item: { type },
    end: (item, monitor) => {
      const dropResult = monitor.getDropResult();
      if (item && dropResult) {
        const offset = monitor.getClientOffset();
        if (offset) {
          onAddNode(type, { x: offset.x, y: offset.y });
        }
      }
    },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  return (
    <NodePaletteItemContainer ref={drag} style={{ opacity: isDragging ? 0.5 : 1 }}>
      {label}
    </NodePaletteItemContainer>
  );
};

const NodePalette: React.FC<NodePaletteProps> = ({ onAddNode }) => {
  const nodeTypes = [
    { type: 'input', label: 'Input' },
    { type: 'process', label: 'Process' },
    { type: 'output', label: 'Output' },
    { type: 'condition', label: 'Condition' },
    { type: 'api', label: 'API Call' },
    { type: 'transform', label: 'Transform' },
    { type: 'delay', label: 'Delay' },
  ];

  return (
    <NodePaletteList>
      <h3>Node Types</h3>
      {nodeTypes.map((nodeType) => (
        <NodePaletteItem
          key={nodeType.type}
          type={nodeType.type}
          label={nodeType.label}
          onAddNode={onAddNode}
        />
      ))}
    </NodePaletteList>
  );
};

const PropertiesPanelComponent: React.FC<{ selectedNode: NodeData | null; onUpdateNodeData: (id: string, data: Record<string, any>) => void }> = ({
  selectedNode,
  onUpdateNodeData,
}) => {
  if (!selectedNode) {
    return (
      <PropertiesPanelContainer>
        <h3>Properties</h3>
        <p>Select a node to edit its properties</p>
      </PropertiesPanelContainer>
    );
  }

  const handleChange = (key: string, value: any) => {
    onUpdateNodeData(selectedNode.id, {
      ...selectedNode.data,
      [key]: value,
    });
  };

  return (
    <PropertiesPanelContainer>
      <h3>Properties: {selectedNode.type}</h3>
      
      <PropertyGroup>
        <PropertyLabel>Label</PropertyLabel>
        <PropertyInput
          type="text"
          value={selectedNode.data.label || ''}
          onChange={(e) => handleChange('label', e.target.value)}
        />
      </PropertyGroup>
      
      {selectedNode.type === 'api' && (
        <>
          <PropertyGroup>
            <PropertyLabel>URL</PropertyLabel>
            <PropertyInput
              type="text"
              value={selectedNode.data.url || ''}
              onChange={(e) => handleChange('url', e.target.value)}
            />
          </PropertyGroup>
          <PropertyGroup>
            <PropertyLabel>Method</PropertyLabel>
            <PropertyInput
              type="text"
              value={selectedNode.data.method || 'GET'}
              onChange={(e) => handleChange('method', e.target.value)}
            />
          </PropertyGroup>
        </>
      )}
      
      {selectedNode.type === 'transform' && (
        <PropertyGroup>
          <PropertyLabel>Transform Function</PropertyLabel>
          <PropertyInput
            type="text"
            value={selectedNode.data.function || ''}
            onChange={(e) => handleChange('function', e.target.value)}
          />
        </PropertyGroup>
      )}
      
      {selectedNode.type === 'delay' && (
        <PropertyGroup>
          <PropertyLabel>Delay (ms)</PropertyLabel>
          <PropertyInput
            type="number"
            value={selectedNode.data.delay || 1000}
            onChange={(e) => handleChange('delay', parseInt(e.target.value))}
          />
        </PropertyGroup>
      )}
    </PropertiesPanelContainer>
  );
};

const Toolbar: React.FC<{
  onSave: () => void;
  onLoad: () => void;
  onClear: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onRun: () => void;
}> = ({ onSave, onLoad, onClear, onZoomIn, onZoomOut, onRun }) => {
  return (
    <ToolbarContainer>
      <ToolbarButton onClick={onSave}>Save</ToolbarButton>
      <ToolbarButton onClick={onLoad}>Load</ToolbarButton>
      <ToolbarButton onClick={onClear}>Clear</ToolbarButton>
      <ToolbarButton onClick={onZoomIn}>Zoom In</ToolbarButton>
      <ToolbarButton onClick={onZoomOut}>Zoom Out</ToolbarButton>
      <ToolbarButton onClick={onRun}>Run Workflow</ToolbarButton>
    </ToolbarContainer>
  );
};

// Main Component
const WorkflowBuilder: React.FC = () => {
  const [workflow, setWorkflow] = useState<WorkflowData>({
    nodes: [],
    edges: [],
  });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [scale, setScale] = useState(1);

  const handleAddNode = (type: string, position: { x: number; y: number }) => {
    const newNode: NodeData = {
      id: uuidv4(),
      type,
      position,
      data: { label: `${type} Node` },
      inputs: ['input-1'],
      outputs: ['output-1'],
    };

    setWorkflow((prev) => ({
      ...prev,
      nodes: [...prev.nodes, newNode],
    }));
  };

  const handleNodeMove = (id: string, position: { x: number; y: number }) => {
    setWorkflow((prev) => ({
      ...prev,
      nodes: prev.nodes.map((node) =>
        node.id === id ? { ...node, position } : node
      ),
    }));
  };

  const handleNodeSelect = (id: string) => {
    setSelectedNodeId(id || null);
    setSelectedEdgeId(null);
  };

  const handleEdgeSelect = (id: string) => {
    setSelectedEdgeId(id);
    setSelectedNodeId(null);
  };

  const handleConnect = (params: { source: string; sourceHandle: string; target: string; targetHandle: string }) => {
    const newEdge: EdgeData = {
      id: uuidv4(),
      ...params,
    };

    setWorkflow((prev) => ({
      ...prev,
      edges: [...prev.edges, newEdge],
    }));
  };

  const handleUpdateNodeData = (id: string, data: Record<string, any>) => {
    setWorkflow((prev) => ({
      ...prev,
      nodes: prev.nodes.map((node) =>
        node.id === id ? { ...node, data } : node
      ),
    }));
  };

  const handleSave = () => {
    const json = JSON.stringify(workflow);
    localStorage.setItem('workflow', json);
    alert('Workflow saved!');
  };

  const handleLoad = () => {
    const json = localStorage.getItem('workflow');
    if (json) {
      try {
        const loadedWorkflow = JSON.parse(json);
        setWorkflow(loadedWorkflow);
        alert('Workflow loaded!');
      } catch (error) {
        alert('Failed to load workflow!');
      }
    } else {
      alert('No saved workflow found!');
    }
  };

  const handleClear = () => {
    if (window.confirm('Are you sure you want to clear the workflow?')) {
      setWorkflow({ nodes: [], edges: [] });
      setSelectedNodeId(null);
      setSelectedEdgeId(null);
    }
  };

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.1, 2));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.1, 0.1));
  };

  const handleRun = () => {
    alert('Running workflow...');
    // Implement workflow execution logic here
  };

  const selectedNode = workflow.nodes.find((node) => node.id === selectedNodeId) || null;

  return (
    <DndProvider backend={HTML5Backend}>
      <WorkflowBuilderContainer>
        <Sidebar>
          <NodePalette onAddNode={handleAddNode} />
          <PropertiesPanelComponent
            selectedNode={selectedNode}
            onUpdateNodeData={handleUpdateNodeData}
          />
        </Sidebar>
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
          <Toolbar
            onSave={handleSave}
            onLoad={handleLoad}
            onClear={handleClear}
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onRun={handleRun}
          />
          <Canvas
            workflow={workflow}
            onNodeMove={handleNodeMove}
            onNodeSelect={handleNodeSelect}
            selectedNodeId={selectedNodeId}
            onConnect={handleConnect}
            onEdgeSelect={handleEdgeSelect}
          />
        </div>
      </WorkflowBuilderContainer>
    </DndProvider>
  );
};

export default WorkflowBuilder;