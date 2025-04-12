import React from 'react';
import { Card, CardContent, Typography, Box, Chip, Divider } from '@mui/material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'; // Choose a style

// Helper to format path array to string for display
const formatPath = (pathArray) => {
    const displayPath = pathArray && pathArray[0] === 'root' ? pathArray.slice(1) : pathArray;
    return displayPath ? displayPath.join('/') : 'N/A';
};

const NodeDetailsPanel = ({ node, path }) => {
    console.log("NodeDetailsPanel received node:", node); // Log the prop received
    console.log("NodeDetailsPanel received path:", path);
    if (!node) {
        return (
            <Card elevation={2}>
                <CardContent>
                    <Typography variant="h6" component="h3" gutterBottom>
                        Node Details
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Click a node in the tree to see details.
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const formattedTimestamp = node.timestamp ? new Date(node.timestamp).toLocaleString() : 'N/A';
    let dataPreview = '(No data)';
    let language = 'text';

    if (node.has_data && node.data !== undefined && node.data !== null) {
        try {
            // Attempt to stringify for JSON preview
            dataPreview = JSON.stringify(node.data, null, 2);
            language = 'json';
        } catch (e) {
             // Fallback for non-JSON serializable data
            try {
                dataPreview = String(node.data);
                // Basic check for complex object types
                if (dataPreview === '[object Object]' && typeof node.data === 'object') {
                     dataPreview = `Object Keys: ${Object.keys(node.data).slice(0, 10).join(', ')}${Object.keys(node.data).length > 10 ? '...' : ''}\n(Preview limited for complex object)`;
                }
            } catch (strErr) {
                 dataPreview = '(Could not display data preview)';
            }
            language = 'text'; // Treat as plain text
        }
    }


    return (
        <Card elevation={2}>
            <CardContent>
                <Typography variant="h6" component="h3" gutterBottom>
                    Node Details
                </Typography>
                <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" color="text.secondary" display="block">Path</Typography>
                    <Typography variant="body2" component="code" sx={{ wordBreak: 'break-all' }}>
                        {formatPath(path)}
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                    <Chip label={`Identifier: ${node.identifier}`} size="small" />
                    <Chip label={`Has Data: ${node.has_data ? 'Yes' : 'No'}`} size="small" color={node.has_data ? 'success' : 'default'} />
                </Box>
                 <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" color="text.secondary" display="block">Timestamp</Typography>
                    <Typography variant="body2">{formattedTimestamp}</Typography>
                </Box>
                 <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block">Data Hash</Typography>
                    <Typography variant="body2" component="code" sx={{ fontSize: '0.75rem', wordBreak: 'break-all' }}>
                        {node.data_hash || 'N/A'}
                    </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle1" component="h4" gutterBottom>
                    Data Preview
                </Typography>
                <Box sx={{ maxHeight: '250px', overflow: 'auto', bgcolor: 'grey.900', borderRadius: 1 }}>
                    <SyntaxHighlighter
                        language={language}
                        style={atomDark} // Use imported style
                        customStyle={{ margin: 0, padding: '8px', fontSize: '0.75rem' }}
                        wrapLongLines={true}
                    >
                        {dataPreview}
                    </SyntaxHighlighter>
                </Box>
            </CardContent>
        </Card>
    );
};

export default NodeDetailsPanel;