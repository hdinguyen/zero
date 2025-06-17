import React, { createContext, useContext, useState, useEffect } from 'react';

// Create the context
const ModeContext = createContext();

// Custom hook to use the mode context
export const useMode = () => {
  const context = useContext(ModeContext);
  if (!context) {
    throw new Error('useMode must be used within a ModeProvider');
  }
  return context;
};

// Mode provider component
export const ModeProvider = ({ children }) => {
  // Initialize state from localStorage or default to 'free'
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('chatMode');
    return savedMode || 'free';
  });

  // Update localStorage whenever mode changes
  useEffect(() => {
    localStorage.setItem('chatMode', mode);
  }, [mode]);

  // Toggle between free and paid mode
  const toggleMode = () => {
    setMode(prevMode => prevMode === 'free' ? 'paid' : 'free');
  };

  // Check if current mode is free
  const isFreeMode = mode === 'free';

  // Check if current mode is paid
  const isPaidMode = mode === 'paid';

  const value = {
    mode,
    setMode,
    toggleMode,
    isFreeMode,
    isPaidMode
  };

  return (
    <ModeContext.Provider value={value}>
      {children}
    </ModeContext.Provider>
  );
};

export default ModeContext; 