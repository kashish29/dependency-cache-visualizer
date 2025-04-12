import React from 'react';
// Import the main visualizer component
import DependencyCacheVisualizer from './components/DependencyCacheVisualizer'; // Corrected path
import './index.css'; // Ensure global styles are imported

function App() {
  return (
    // Render only the main visualizer component
    <DependencyCacheVisualizer />
  );
}

export default App;