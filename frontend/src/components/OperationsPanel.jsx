import React from 'react';
import { Box, TextField, Button, Typography, Paper } from '@mui/material';
import { Search, AddCircleOutline, DeleteOutline } from '@mui/icons-material'; // Using MUI icons

const OperationsPanel = ({
    opPathInput,
    onOpPathInputChange,
    opDataInput,
    onOpDataInputChange,
    onGetData,
    onAddData,
    onInvalidate,
    loading,
    lastOperationResult
}) => {

    return (
        <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom component="h3">
                Operations
            </Typography>
            <Box component="form" noValidate autoComplete="off" sx={{ '& .MuiTextField-root': { mb: 2 } }}>
                <TextField
                    label="Path (e.g. level1/level2)"
                    variant="outlined"
                    size="small"
                    fullWidth
                    value={opPathInput}
                    onChange={onOpPathInputChange}
                    placeholder="users/profile/data"
                    disabled={loading}
                />
                <TextField
                    label="Data (String or JSON)"
                    variant="outlined"
                    size="small"
                    fullWidth
                    multiline
                    rows={3}
                    value={opDataInput}
                    onChange={onOpDataInputChange}
                    placeholder='"some value" or {"key": "value"}'
                    disabled={loading}
                    InputProps={{ sx: { fontFamily: 'monospace' } }}
                />
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                    <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        startIcon={<Search />}
                        onClick={onGetData}
                        disabled={loading || !opPathInput}
                    >
                        Get
                    </Button>
                    <Button
                        variant="contained"
                        color="success"
                        size="small"
                        startIcon={<AddCircleOutline />}
                        onClick={onAddData}
                        disabled={loading || !opPathInput}
                    >
                        Add/Update
                    </Button>
                    <Button
                        variant="contained"
                        color="error"
                        size="small"
                        startIcon={<DeleteOutline />}
                        onClick={onInvalidate}
                        disabled={loading || !opPathInput}
                    >
                        Invalidate
                    </Button>
                </Box>
            </Box>

            {/* Last Operation Result Display */}
            {lastOperationResult && (
                <Box
                    sx={{
                        mt: 2,
                        p: 1,
                        borderRadius: 1,
                        border: 1,
                        fontSize: '0.75rem',
                        borderColor: lastOperationResult.success ? 'success.light' : 'error.light',
                        bgcolor: lastOperationResult.success ? 'success.lighter' : 'error.lighter', // Assuming custom theme colors or adjust
                        color: lastOperationResult.success ? 'success.dark' : 'error.dark',
                    }}
                >
                    <Typography variant="body2" component="p" sx={{ fontWeight: 'medium' }}>
                        Last Op: {lastOperationResult.type} ({lastOperationResult.success ? 'Success' : 'Failed'})
                    </Typography>
                    {lastOperationResult.path && <Typography variant="body2" component="p">Path: <code style={{ wordBreak: 'break-all' }}>{lastOperationResult.path}</code></Typography>}
                    {lastOperationResult.error && <Typography variant="body2" component="p">Error: {lastOperationResult.error}</Typography>}
                    {/* Simple display for GET response */}
                    {lastOperationResult.type === 'GET_DATA' && lastOperationResult.success && (
                         <Typography variant="body2" component="p" sx={{ mt: 0.5 }}>
                            Response: Node {lastOperationResult.response?.node_exists ? `exists (Data: ${lastOperationResult.response?.data !== undefined ? 'Yes' : 'No'})` : 'does not exist.'}
                         </Typography>
                    )}
                </Box>
            )}
        </Paper>
    );
};

export default OperationsPanel;