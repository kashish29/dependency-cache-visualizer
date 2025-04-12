import React, { useState, useMemo } from 'react';
import { Paper, Typography, Grid, Box, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TableSortLabel, Tooltip as MuiTooltip } from '@mui/material';
import { Refresh } from '@mui/icons-material'; // Using MUI icons
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Helper to format numbers or show 'N/A'
const formatStat = (value) => {
    return typeof value === 'number' ? value.toLocaleString() : 'N/A';
};

// Colors for Pie Chart
const COLORS = ['#4caf50', '#f44336']; // Green for Hits, Red for Misses

// Table Sorting Helpers
function descendingComparator(a, b, orderBy) {
    if (b[orderBy] < a[orderBy]) return -1;
    if (b[orderBy] > a[orderBy]) return 1;
    return 0;
}

function getComparator(order, orderBy) {
    return order === 'desc'
        ? (a, b) => descendingComparator(a, b, orderBy)
        : (a, b) => -descendingComparator(a, b, orderBy);
}

const StatsPanel = ({ stats, onResetStats, loading }) => {
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('checked'); // Default sort column

    const handleRequestSort = (property) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const {
        gets = 0, hits = 0, misses = 0, adds = 0, invalidations = 0,
        paths_checked = {}, paths_hit = {}, paths_missed = {},
        paths_added = {}, paths_invalidated = {}
    } = stats || {}; // Default to empty object if stats is null/undefined

    const hitRatio = gets > 0 ? (hits / gets) * 100 : 0;
    const missRatio = gets > 0 ? (misses / gets) * 100 : 0;

    const pieData = [
        { name: 'Hits', value: hits },
        { name: 'Misses', value: misses },
    ];

    // Prepare data for the table
    const pathTableData = useMemo(() => {
        const allPaths = new Set([
            ...Object.keys(paths_checked),
            ...Object.keys(paths_hit),
            ...Object.keys(paths_missed),
            ...Object.keys(paths_added),
            ...Object.keys(paths_invalidated),
        ]);

        return Array.from(allPaths).map(pathKey => ({
            path: pathKey,
            checked: paths_checked[pathKey] || 0,
            hit: paths_hit[pathKey] || 0,
            missed: paths_missed[pathKey] || 0,
            added: paths_added[pathKey] || 0,
            invalidated: paths_invalidated[pathKey] || 0,
        }));
    }, [paths_checked, paths_hit, paths_missed, paths_added, paths_invalidated]);

    const sortedTableData = useMemo(() => {
        return [...pathTableData].sort(getComparator(order, orderBy));
    }, [pathTableData, order, orderBy]);

    const tableColumns = [
        { id: 'path', label: 'Path', numeric: false },
        { id: 'checked', label: 'Checked', numeric: true },
        { id: 'hit', label: 'Hit', numeric: true },
        { id: 'missed', label: 'Missed', numeric: true },
        { id: 'added', label: 'Added', numeric: true },
        { id: 'invalidated', label: 'Invalidated', numeric: true },
    ];

    if (!stats) {
        return <Paper elevation={2} sx={{ p: 2 }}><Typography color="text.secondary">Loading stats...</Typography></Paper>;
    }

    return (
        <Paper elevation={2} sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h3">
                    Cache Statistics
                </Typography>
                <Button
                    variant="outlined"
                    color="secondary"
                    size="small"
                    startIcon={<Refresh />}
                    onClick={onResetStats}
                    disabled={loading}
                >
                    Reset Stats
                </Button>
            </Box>

            <Grid container spacing={2}>
                {/* Overview Stats */}
                <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" gutterBottom>Overview</Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}> <Typography variant="body2">Gets:</Typography> <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{formatStat(gets)}</Typography> </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}> <Typography variant="body2">Hits:</Typography> <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{formatStat(hits)}</Typography> </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}> <Typography variant="body2">Misses:</Typography> <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{formatStat(misses)}</Typography> </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}> <Typography variant="body2">Adds:</Typography> <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{formatStat(adds)}</Typography> </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}> <Typography variant="body2">Invalidations:</Typography> <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{formatStat(invalidations)}</Typography> </Box>
                </Grid>

                {/* Hit/Miss Ratio Pie Chart */}
                <Grid item xs={12} md={6}>
                     <Typography variant="subtitle1" align="center" gutterBottom>Hit / Miss Ratio</Typography>
                     {gets > 0 ? (
                        <ResponsiveContainer width="100%" height={150}>
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    outerRadius={60}
                                    fill="#8884d8"
                                    dataKey="value"
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value, name) => [formatStat(value), name]}/>
                                {/* <Legend /> */}
                            </PieChart>
                        </ResponsiveContainer>
                     ) : (
                        <Typography variant="body2" align="center" color="text.secondary" sx={{height: 150, display:'flex', alignItems:'center', justifyContent:'center'}}>
                            No cache gets yet.
                        </Typography>
                     )}
                </Grid>
            </Grid>

            {/* Detailed Path Stats Table */}
            <Typography variant="subtitle1" sx={{ mt: 3, mb: 1 }}>Detailed Path Counts</Typography>
            <TableContainer component={Paper} elevation={1} sx={{ maxHeight: 300, overflow: 'auto' }}>
                <Table stickyHeader size="small" aria-label="detailed path statistics table">
                    <TableHead>
                        <TableRow>
                            {tableColumns.map((col) => (
                                <TableCell
                                    key={col.id}
                                    align={col.numeric ? 'right' : 'left'}
                                    sortDirection={orderBy === col.id ? order : false}
                                    sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}
                                >
                                    <TableSortLabel
                                        active={orderBy === col.id}
                                        direction={orderBy === col.id ? order : 'asc'}
                                        onClick={() => handleRequestSort(col.id)}
                                    >
                                        {col.label}
                                    </TableSortLabel>
                                </TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {sortedTableData.map((row) => (
                            <TableRow hover key={row.path}>
                                <TableCell component="th" scope="row" sx={{ wordBreak: 'break-all', fontSize: '0.75rem' }}>
                                    {row.path}
                                </TableCell>
                                <TableCell align="right">{formatStat(row.checked)}</TableCell>
                                <TableCell align="right">{formatStat(row.hit)}</TableCell>
                                <TableCell align="right">{formatStat(row.missed)}</TableCell>
                                <TableCell align="right">{formatStat(row.added)}</TableCell>
                                <TableCell align="right">{formatStat(row.invalidated)}</TableCell>
                            </TableRow>
                        ))}
                         {pathTableData.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={tableColumns.length} align="center">
                                    No path data recorded yet.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
};

export default StatsPanel;