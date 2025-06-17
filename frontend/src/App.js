import React from 'react';
import Chat from './components/Chat';
import { ModeProvider } from './contexts/ModeContext';
import './App.css';

function App() {
  return (
    <ModeProvider>
      <div className="App">
        <Chat />
      </div>
    </ModeProvider>
  );
}

export default App;
