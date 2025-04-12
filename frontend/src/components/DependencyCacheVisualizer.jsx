import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Grid, AppBar, Toolbar, Typography, Select, MenuItem, Button, IconButton, CircularProgress, Alert, Paper, Tooltip as MuiTooltip } from '@mui/material';
import { Refresh, PlayArrow, Pause, ErrorOutline } from '@mui/icons-material'; // Using MUI icons
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'; // Import toastify CSS

import * as api from '../services/api';
import TreeView from './TreeView';
import StatsPanel from './StatsPanel';
import NodeDetailsPanel from './NodeDetailsPanel';
import OperationsPanel from './OperationsPanel'; // Import the new panel

// Helper to parse path string
const parsePath = (pathStr) => {
    return pathStr.split('/').filter(p => p && p.trim() !== '');
};

// Helper to format path array to string
const formatPath = (pathArray) => {
    const displayPath = pathArray && pathArray[0] === 'root' ? pathArray.slice(1) : pathArray;
    return displayPath ? displayPath.join('/') : '';
};

const DependencyCacheVisualizer = () => {
    const [tree, setTree] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState({ tree: false, stats: false, operation: false });
    const [error, setError] = useState(null);
    const [expandedNodes, setExpandedNodes] = useState({});
    const [selectedNode, setSelectedNode] = useState(null);
    const [selectedPath, setSelectedPath] = useState([]);

    // Operation Inputs state now managed here, passed down
    const [opPathInput, setOpPathInput] = useState('');
    const [opDataInput, setOpDataInput] = useState('');
    const [lastOperationResult, setLastOperationResult] = useState(null); // Keep track of last op for display

    // Auto-refresh state
    const [autoRefreshInterval, setAutoRefreshInterval] = useState(0);
    const refreshIntervalId = useRef(null);

    // --- Data Fetching ---
    const fetchData = useCallback(async (isInitial = false) => {
        if (isInitial) setLoading({ tree: true, stats: true, operation: false });
        else setLoading(prev => ({ ...prev, tree: true, stats: true }));
        setError(null); // Clear previous errors on fetch attempt
        try {
            const [treeData, statsData] = await Promise.all([api.getTree(), api.getStats()]);
            setTree(treeData);
            setStats(statsData);
        } catch (err) {
            console.error('Error fetching data:', err);
            const errorMsg = `Failed to fetch data: ${err.message}`;
            setError(errorMsg);
            toast.error(errorMsg); // Show toast on fetch error
            if (refreshIntervalId.current) {
                clearInterval(refreshIntervalId.current);
                refreshIntervalId.current = null;
                setAutoRefreshInterval(0);
            }
        } finally {
            setLoading(prev => ({ ...prev, tree: false, stats: false })); // Only reset tree/stats loading
        }
    }, []);

    // --- Initial Data Load ---
    useEffect(() => {
        fetchData(true);
    }, [fetchData]);

    // --- Auto Refresh Logic ---
    useEffect(() => {
        if (refreshIntervalId.current) clearInterval(refreshIntervalId.current);
        if (autoRefreshInterval > 0) {
            refreshIntervalId.current = setInterval(() => {
                if (!loading.tree && !loading.stats && !loading.operation) fetchData();
            }, autoRefreshInterval);
        }
        return () => { if (refreshIntervalId.current) clearInterval(refreshIntervalId.current); };
    }, [autoRefreshInterval, fetchData, loading]);

    const handleAutoRefreshChange = (event) => {
        setAutoRefreshInterval(Number(event.target.value));
    };

    // --- Tree Interaction ---
    const handleToggleNode = useCallback((nodeId) => {
        setExpandedNodes(prev => ({ ...prev, [nodeId]: !prev[nodeId] }));
    }, []);

    const handleNodeClick = useCallback((node, path) => {
        console.log("Node Clicked:", node); // Log the full node object received
        console.log("Path Clicked:", path);
        setSelectedNode(node);
        setSelectedPath(path);
        setOpPathInput(formatPath(path)); // Update operation path input
    }, []);

    // --- Cache Operations ---
    const executeOperation = async (operationFn, successMessage, opType, requiresPath = true, clearDataInput = false) => {
        setLoading(prev => ({ ...prev, operation: true }));
        setError(null);
        setLastOperationResult(null); // Clear previous result
        let resultData = null;
        const currentPathStr = opPathInput; // Capture path at start of operation

        try {
            const path = parsePath(opPathInput);
            if (requiresPath && path.length === 0) {
                throw new Error("Path cannot be empty for this operation.");
            }

            let response;
            if (operationFn === api.addData) {
                let dataValue;
                try { dataValue = JSON.parse(opDataInput); }
                catch { dataValue = opDataInput; }
                response = await operationFn(path, dataValue);
            } else if (requiresPath) {
                response = await operationFn(path);
            } else {
                 response = await operationFn(); // For operations like resetStats
            }

            resultData = response;
            toast.success(successMessage);
            setLastOperationResult({ type: opType, success: true, path: currentPathStr, response });
            if (clearDataInput) setOpDataInput('');
            await fetchData(); // Refresh data after successful operation
        } catch (err) {
            console.error(`Operation failed: ${opType}`, err);
            const errorMsg = `Operation failed: ${err.message}`;
            setError(errorMsg); // Show error in dedicated area
            toast.error(errorMsg); // Show toast notification
            setLastOperationResult({ type: opType, success: false, path: currentPathStr, error: err.message });
        } finally {
            setLoading(prev => ({ ...prev, operation: false }));
        }
        return resultData; // Return result if needed
    };

    const handleGetData = async () => {
       const result = await executeOperation(api.getData, 'Data retrieved', 'GET_DATA', true);
       // Update last op result specifically for GET to show existence/data status
       if (result) {
            setLastOperationResult({
                type: 'GET_DATA',
                success: true,
                path: opPathInput,
                response: result // Contains data, hash, timestamp etc.
            });
       }
    };
    const handleAddData = () => executeOperation(api.addData, 'Data added/updated', 'ADD_DATA', true, true);
    const handleInvalidate = () => executeOperation(api.invalidatePath, 'Path invalidated', 'INVALIDATE', true);
    const handleResetStats = () => executeOperation(api.resetStats, 'Stats reset', 'RESET_STATS', false);

    const isOverallLoading = loading.tree || loading.stats; // Don't block UI for op loading

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            {/* Header */}
            <AppBar position="static" elevation={1}>
                <Toolbar variant="dense">
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Dependency Cache Visualizer
                    </Typography>
                    {/* Refresh Controls */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                         <MuiTooltip title="Manual Refresh">
                            <span> {/* Tooltip needs a DOM element when button is disabled */}
                                <IconButton
                                    color="inherit"
                                    onClick={() => fetchData()}
                                    disabled={isOverallLoading}
                                >
                                    <Refresh className={isOverallLoading ? 'animate-spin' : ''} />
                                </IconButton>
                            </span>
                         </MuiTooltip>
                        <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: 'rgba(255,255,255,0.1)', borderRadius: 1, p: 0.5 }}>
                            <MuiTooltip title={autoRefreshInterval > 0 ? `Auto-refreshing every ${autoRefreshInterval/1000}s` : 'Auto-refresh Off'}>
                                {autoRefreshInterval > 0 ? <PlayArrow fontSize="small" /> : <Pause fontSize="small" />}
                             </MuiTooltip>
                            <Select
                                variant="standard"
                                value={autoRefreshInterval}
                                onChange={handleAutoRefreshChange}
                                disabled={isOverallLoading}
                                disableUnderline
                                sx={{
                                    color: 'inherit',
                                    ml: 0.5,
                                    fontSize: '0.8rem',
                                    '& .MuiSelect-icon': { color: 'inherit' },
                                    '& .MuiSelect-select': { py: 0, px: 1 }
                                }}
                            >
                                <MenuItem value={0}>Manual</MenuItem>
                                <MenuItem value={5000}>5s</MenuItem>
                                <MenuItem value={10000}>10s</MenuItem>
                                <MenuItem value={30000}>30s</MenuItem>
                            </Select>
                        </Box>
                    </Box>
                </Toolbar>
            </AppBar>

            {/* Main Content Area */}
            <Box sx={{ flexGrow: 1, p: 2 }}> 
                <Grid container spacing={2} sx={{ height: '100%' }}>
                    {/* First Row: Tree View */}
                    <Grid item xs={12} md={5} lg={4}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                        <Typography variant="h6" component="h2" gutterBottom>Cache Tree</Typography>
                        <Box sx={{ flexGrow: 1, overflow: 'auto', minHeight: 0 }}> 
                           {loading.tree && !tree ? ( 
                                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                                    <CircularProgress />
                                </Box>
                            ) : (
                                <TreeView
                                    tree={tree}
                                    expandedNodes={expandedNodes}
                                    selectedNodePath={selectedPath}
                                    onToggleNode={handleToggleNode}
                                    onNodeClick={handleNodeClick}
                                />
                            )}
                            </Box>
                        </Box>
                    </Grid>

                    {/* Second Row: Operations, Stats, Details */}
                    <Grid item xs={12} md={7} lg={8}> {/* Make this column scrollable */}
                    <Box sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            height: '100%',
                            overflow: 'auto', // Make this inner box scrollable
                            gap: 2 // Apply gap here for spacing between panels
                        }}>
                        {error && (
                            <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
                                {error}
                            </Alert>
                        )}
                            <OperationsPanel
                                sx={{ flexShrink: 0 }}
                                opPathInput={opPathInput}
                                onOpPathInputChange={(e) => setOpPathInput(e.target.value)}
                                opDataInput={opDataInput}
                                onOpDataInputChange={(e) => setOpDataInput(e.target.value)}
                                onGetData={handleGetData}
                                onAddData={handleAddData}
                                onInvalidate={handleInvalidate}
                                loading={loading.operation}
                                lastOperationResult={lastOperationResult}
                            />
                           {loading.stats && !stats ? ( // Show loading indicator only on initial load
                                <Paper elevation={2} sx={{ p: 2 }}><CircularProgress size={24} /></Paper>
                            ) : (
                                <StatsPanel  sx={{ flexShrink: 0 }} stats={stats} onResetStats={handleResetStats} loading={loading.operation} />
                            )}
                            <NodeDetailsPanel  sx={{ flexShrink: 0 }} node={selectedNode} path={selectedPath} />
                        </Box>
                    </Grid>
                </Grid>
            </Box>

            {/* Toast Notifications Container */}
            <ToastContainer
                position="bottom-right"
                autoClose={4000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="light" // or "dark" or "colored"
            />
        </Box>
    );
}

export default DependencyCacheVisualizer;