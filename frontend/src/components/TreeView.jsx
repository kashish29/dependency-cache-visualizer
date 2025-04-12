import React, { useState, memo, useCallback } from 'react';
import { Box, Typography, IconButton, Collapse,Paper } from '@mui/material';
import { ChevronRight, ExpandMore, Folder, FolderOpen, DataObject } from '@mui/icons-material'; // Using MUI icons

// Memoize TreeNode to prevent unnecessary re-renders
const TreeNode = memo(({
    node,
    level = 0,
    path = [],
    expandedNodes,
    selectedNodePathStr, // Pass selected path as string for comparison
    onToggleNode,
    onNodeClick
}) => {
    if (!node || !node.identifier) return null;

    const currentPath = [...path, node.identifier];
    const currentPathStr = currentPath.join('/');
    const isExpanded = expandedNodes[currentPathStr] || false;
    const hasChildren = node.children && Object.keys(node.children).length > 0;
    const isSelected = selectedNodePathStr === currentPathStr;

    const handleToggle = useCallback((e) => {
        e.stopPropagation();
        if (hasChildren) onToggleNode(currentPathStr);
    }, [hasChildren, onToggleNode, currentPathStr]);

    const handleClick = useCallback(() => {
        onNodeClick(node, currentPath);
    }, [onNodeClick, node, currentPath]);

    const Icon = hasChildren ? (isExpanded ? FolderOpen : Folder) : DataObject;

    return (
        <Box sx={{ pl: level * 2, userSelect: 'none' }}> {/* Indentation using padding */}
            <Box
                onClick={handleClick}
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    cursor: 'pointer',
                    py: 0.5,
                    px: 1,
                    borderRadius: 1,
                    backgroundColor: isSelected ? 'action.selected' : 'transparent',
                    '&:hover': {
                        backgroundColor: isSelected ? 'action.selected' : 'action.hover',
                    },
                }}
            >
                <IconButton size="small" onClick={handleToggle} sx={{ visibility: hasChildren ? 'visible' : 'hidden', mr: 0.5 }}>
                    {isExpanded ? <ExpandMore fontSize="inherit" /> : <ChevronRight fontSize="inherit" />}
                </IconButton>
                <Icon fontSize="small" sx={{ mr: 1, color: node.has_data ? 'primary.main' : 'text.secondary' }} />
                <Typography
                    variant="body2"
                    component="span"
                    sx={{
                        fontWeight: node.has_data ? 500 : 400,
                        color: node.has_data ? 'text.primary' : 'text.secondary',
                        flexGrow: 1,
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                    }}
                    title={currentPathStr} // Show full path on hover
                >
                    {node.identifier}
                </Typography>
                {/* Add indicators here if needed */}
            </Box>

            {/* Children - Use Collapse for animation */}
            {hasChildren && (
                 <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                     <Box sx={{ borderLeft: '1px dashed', borderColor: 'grey.300', ml: '12px' /* Align with icon center */ }}>
                        {Object.values(node.children)
                            .sort((a, b) => a.identifier.localeCompare(b.identifier))
                            .map(childNode => (
                                <TreeNode
                                    key={childNode.identifier}
                                    node={childNode}
                                    level={level + 1}
                                    path={currentPath}
                                    expandedNodes={expandedNodes}
                                    selectedNodePathStr={selectedNodePathStr}
                                    onToggleNode={onToggleNode}
                                    onNodeClick={onNodeClick}
                                />
                            ))
                        }
                    </Box>
                 </Collapse>
            )}
        </Box>
    );
});

// Main Tree View Component
const TreeView = ({ tree, expandedNodes, selectedNodePath, onToggleNode, onNodeClick }) => {
    if (!tree || !tree.children) {
        return <Paper elevation={2} sx={{ p: 2 }}><Typography color="text.secondary">Loading tree or cache empty...</Typography></Paper>;
    }

    const rootChildren = Object.values(tree.children)
        .sort((a, b) => a.identifier.localeCompare(b.identifier));

    // Convert selected path array to string for efficient comparison in children
    const selectedNodePathStr = selectedNodePath ? selectedNodePath.join('/') : null;

    return (
        <Paper elevation={2} sx={{ p: 1, maxHeight: 'calc(100vh - 200px)', overflow: 'auto' }}> {/* Adjust maxHeight as needed */}
             {rootChildren.length === 0 ? (
                 <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                    Cache is empty.
                 </Typography>
            ) : (
                rootChildren.map(node => (
                    <TreeNode
                        key={node.identifier}
                        node={node}
                        level={0}
                        path={['root']} // Base path
                        expandedNodes={expandedNodes}
                        selectedNodePathStr={selectedNodePathStr}
                        onToggleNode={onToggleNode}
                        onNodeClick={onNodeClick}
                    />
                ))
            )}
        </Paper>
    );
};

export default TreeView;