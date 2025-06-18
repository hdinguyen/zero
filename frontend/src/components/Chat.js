import React, { useState, useRef, useEffect, useCallback } from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import { apiService } from '../config/api';
import { useMode } from '../contexts/ModeContext';

const Chat = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [showPreview, setShowPreview] = useState(false);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [currentThreadId, setCurrentThreadId] = useState(null); // Start with no thread
  const { mode, toggleMode, isFreeMode, isPaidMode } = useMode();
  const textareaRef = useRef(null);
  const chatContainerRef = useRef(null);
  const previewRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [chats, setChats] = useState([]);
  const [chatsLoading, setChatsLoading] = useState(false);
  const [chatsError, setChatsError] = useState(null);
  const [socketMessages, setSocketMessages] = useState([]);

  // Fetch thread IDs on mount
  useEffect(() => {
    const fetchChats = async () => {
      setChatsLoading(true);
      setChatsError(null);
      try {
        const data = await apiService.fetchThreadIds();
        setChats(data);
      } catch (err) {
        setChatsError('Failed to load chat threads');
      } finally {
        setChatsLoading(false);
      }
    };
    fetchChats();
  }, []);

  // Function to start a new chat
  const handleNewChat = () => {
    setMessages([]);
    setCurrentThreadId(null);
    setError(null);
    setMessage('');
    setShowPreview(false);
  };

  const handleSendMessage = async () => {
    if (message.trim()) {
      // Clear any previous errors
      setError(null);
      
      // Add user message to conversation
      const userMessage = {
        id: Date.now(),
        text: message.trim(),
        sender: 'user',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prevMessages => [...prevMessages, userMessage]);
      const questionText = message.trim();
      setMessage('');
      
      // Show typing animation
      setIsTyping(true);
      
      try {
        // Make API call to backend
        const response = await apiService.sendMessage(questionText, currentThreadId);
        
        // Update thread ID if this was a new thread or if it changed
        if (response.thread_id && response.thread_id !== currentThreadId) {
          setCurrentThreadId(response.thread_id);
        }
        
        // Create AI response message
        const aiResponse = {
          id: Date.now() + 1,
          text: response.result || 'I received your message but got an unexpected response format.',
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        setMessages(prevMessages => [...prevMessages, aiResponse]);
        
      } catch (error) {
        console.error('Failed to send message:', error);
        setError('Failed to get response from AI. Please try again.');
        
        // Add error message to chat
        const errorMessage = {
          id: Date.now() + 1,
          text: 'Sorry, I\'m having trouble connecting to the server. Please try again later.',
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isError: true
        };
        
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      } finally {
        // Hide typing animation
        setIsTyping(false);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Auto-resize textarea based on content
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    const chatContainer = chatContainerRef.current;
    
    if (textarea && chatContainer) {
      // Reset height to calculate scrollHeight
      textarea.style.height = 'auto';
      
      // Calculate max height (1/3 of chat window)
      const chatHeight = chatContainer.clientHeight;
      const maxHeight = Math.floor(chatHeight / 3);
      
      // Set height based on content, up to maxHeight
      const newHeight = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = `${newHeight}px`;
      
      // Enable scrolling if content exceeds max height
      textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
    }
  };

  // Adjust height when message changes
  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      adjustTextareaHeight();
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle cursor position changes
  const handleCursorChange = (e) => {
    setCursorPosition(e.target.selectionStart);
  };

  // Check if message contains markdown syntax
  const hasMarkdownSyntax = () => {
    return /[*_`#[\]!-]/.test(message) && message.trim().length > 0;
  };

  // Calculate which line the cursor is on
  const getCurrentLine = useCallback(() => {
    if (!message || cursorPosition === 0) return 0;
    
    const textUpToCursor = message.substring(0, cursorPosition);
    const lineNumber = textUpToCursor.split('\n').length - 1;
    return lineNumber;
  }, [message, cursorPosition]);

  // Auto-scroll preview to cursor line
  const scrollPreviewToCursor = useCallback(() => {
    if (!showPreview || !previewRef.current) return;
    
    const currentLine = getCurrentLine();
    const previewContainer = previewRef.current;
    
    // Find all line elements in the preview
    const lineElements = previewContainer.querySelectorAll('.preview-line');
    
    if (lineElements[currentLine]) {
      lineElements[currentLine].scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  }, [showPreview, getCurrentLine]);

  // Scroll preview when cursor position changes
  useEffect(() => {
    if (showPreview) {
      scrollPreviewToCursor();
    }
  }, [cursorPosition, showPreview, scrollPreviewToCursor]);

  // Auto-scroll to bottom when messages change or typing starts
  useEffect(() => {
    if (messages.length > 0 && !isTyping) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
    }
  }, [messages, isTyping]);

  // Parse message into blocks (text/code)
  const parseBlocks = (text) => {
    const lines = text.split('\n');
    const blocks = [];
    let inCodeBlock = false;
    let codeBlockLang = '';
    let codeLines = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const codeBlockStart = line.match(/^```(\w*)/);

      if (!inCodeBlock && codeBlockStart) {
        inCodeBlock = true;
        codeBlockLang = codeBlockStart[1] || '';
        codeLines = [];
      } else if (inCodeBlock && line.trim() === '```') {
        inCodeBlock = false;
        blocks.push({
          type: 'code',
          lang: codeBlockLang,
          content: codeLines.join('\n'),
        });
        codeBlockLang = '';
        codeLines = [];
      } else if (inCodeBlock) {
        codeLines.push(line);
      } else {
        blocks.push({
          type: 'text',
          content: line,
        });
      }
    }
    // If file ends while still in code block
    if (inCodeBlock && codeLines.length > 0) {
      blocks.push({
        type: 'code',
        lang: codeBlockLang,
        content: codeLines.join('\n'),
      });
    }
    return blocks;
  };

  // Render message with Slack-like styling for input display
  const renderStyledMessage = (text) => {
    const blocks = parseBlocks(text);
    return blocks.map((block, idx) => {
      if (block.type === 'code') {
        return (
          <div key={idx} className="my-2 p-2 bg-[#f1f5f9] border border-[#cbd5e1] rounded text-xs font-mono">
            <div className="text-[#64748b] text-xs mb-1">Code block:</div>
            <pre className="whitespace-pre-wrap">{block.content}</pre>
          </div>
        );
      } else {
        // Inline code styling
        const inlineParts = block.content.split(/(`[^`]+`)/);
        return (
          <div key={idx} className="preview-line">
            {inlineParts.map((inlinePart, inlineIdx) => {
              if (inlinePart.startsWith('`') && inlinePart.endsWith('`')) {
                const code = inlinePart.slice(1, -1);
                return (
                  <span
                    key={inlineIdx}
                    className="bg-[#f1f5f9] border border-[#cbd5e1] rounded px-1 py-0.5 text-sm font-mono text-[#dc2626] mx-0.5"
                  >
                    {code}
                  </span>
                );
              } else {
                return <span key={inlineIdx}>{inlinePart}</span>;
              }
            })}
          </div>
        );
      }
    });
  };

  // Socket connection logic
  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');

    socket.onopen = () => {
      console.log('WebSocket connection opened');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setSocketMessages(prevMessages => [...prevMessages, data.message]);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="relative flex size-full min-h-screen flex-col bg-slate-50 group/design-root overflow-x-hidden font-inter">
      <div className="flex flex-1 h-full min-h-0">
        {/* Sidebar */}
        <aside className="w-80 flex flex-col bg-slate-50 flex-shrink-0 h-full border-r border-[#e7edf4]">
          <div className="flex flex-col flex-1 h-full p-4">
            <h1 className="text-[#0d151c] text-base font-medium leading-normal mb-2">My AI Assistant</h1>
            <div className="flex flex-col flex-1 min-h-0">
              {/* Chat List (scrollable, max 10 threads) */}
              <div
                className="overflow-y-auto"
                style={{ maxHeight: `${10 * 48}px` }} // 48px per thread item
              >
                {chatsLoading ? (
                  <div className="text-xs text-gray-400 px-3 py-2">Loading chats...</div>
                ) : chatsError ? (
                  <div className="text-xs text-red-500 px-3 py-2">{chatsError}</div>
                ) : (
                  chats.map((chat) => (
                    <div 
                      key={chat.thread_id} 
                      className="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-[#e7edf4] rounded-lg transition-colors"
                      style={{ minHeight: '48px', height: '48px' }}
                      onClick={async () => {
                        setError(null);
                        setIsTyping(false);
                        setCurrentThreadId(chat.thread_id);
                        setMessages([]);
                        try {
                          const conversation = await apiService.fetchConversation(chat.thread_id);
                          // Map the conversation to the messages format used in state
                          const mappedMessages = conversation.map((item, idx) => [
                            {
                              id: `${chat.thread_id}-user-${idx}`,
                              text: item.user_message,
                              sender: 'user',
                              timestamp: item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''
                            },
                            {
                              id: `${chat.thread_id}-ai-${idx}`,
                              text: item.assistant_response,
                              sender: 'ai',
                              timestamp: item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''
                            }
                          ]).flat();
                          setMessages(mappedMessages);
                        } catch (err) {
                          setError('Failed to load conversation');
                          setMessages([]);
                        }
                      }}
                    >
                      <div className="text-[#0d151c]" data-icon="ChatCircleDots" data-size="24px" data-weight="regular">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                          <path d="M140,128a12,12,0,1,1-12-12A12,12,0,0,1,140,128ZM84,116a12,12,0,1,0,12,12A12,12,0,0,0,84,116Zm88,0a12,12,0,1,0,12,12A12,12,0,0,0,172,116Zm60,12A104,104,0,0,1,79.12,219.82L45.07,231.17a16,16,0,0,1-20.24-20.24l11.35-34.05A104,104,0,1,1,232,128Zm-16,0A88,88,0,1,0,51.81,172.06a8,8,0,0,1,.66,6.54L40,216,77.4,203.53a7.85,7.85,0,0,1,2.53-.42,8,8,0,0,1,4,1.08A88,88,0,0,0,216,128Z"></path>
                        </svg>
                      </div>
                      <p className="text-[#0d151c] text-sm font-medium leading-normal truncate max-w-[120px]">{chat.thread_id}</p>
                    </div>
                  ))
                )}
              </div>
              {/* Socket Messages Area (fills remaining space) */}
              <div className="flex-1 min-h-0 mt-2 flex flex-col">
                <label className="block text-xs font-medium text-[#49749c] mb-1">Server Socket Messages</label>
                <textarea
                  value={socketMessages.join('\n')}
                  readOnly
                  className="w-full flex-1 bg-[#f8fafc] border border-[#e7edf4] rounded p-2 text-xs text-[#0d151c] resize-none min-h-0 max-h-full overflow-y-auto"
                  style={{ fontFamily: 'monospace', height: '100%' }}
                  aria-label="Socket messages from server"
                />
              </div>
            </div>
          </div>
        </aside>
        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col min-h-0" ref={chatContainerRef}>
          {/* Thread Status Header */}
          <div className="border-b border-[#e7edf4] bg-white px-4 py-3 flex-shrink-0">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-[#0d151c]">
                {currentThreadId ? `Thread: ${currentThreadId}` : 'New Conversation'}
              </h2>
              <div className="flex items-center gap-4 text-sm text-[#49749c]">
                {/* Mode Indicator */}
                <div className="flex items-center gap-1">
                  <div className={`w-2 h-2 rounded-full ${
                    isPaidMode ? 'bg-yellow-500' : 'bg-gray-400'
                  }`}></div>
                  <span className={isPaidMode ? 'text-yellow-600 font-medium' : 'text-gray-500'}>
                    {isPaidMode ? 'Paid' : 'Free'}
                  </span>
                </div>
                
                {/* Thread Status */}
                {currentThreadId ? (
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span>Connected to thread</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span>Ready to start new thread</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Error Banner */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 mx-4 mt-4 rounded-lg">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium">{error}</p>
                </div>
                <div className="ml-auto pl-3">
                  <button
                    onClick={() => setError(null)}
                    className="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none"
                  >
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Chat Content */}
          <div className="flex-1 min-h-0 flex flex-col">
            <section className="flex-1 flex flex-col overflow-y-auto min-h-0 px-4 py-5">
              {messages.length === 0 ? (
                // Welcome screen when no messages
                <div className="flex-1 flex flex-col justify-center items-center">
                  <div className="max-w-[960px] w-full text-center">
                    <h2 className="text-[#0d151c] tracking-light text-[28px] font-bold leading-tight pb-3">
                      Start a new conversation
                    </h2>
                    <p className="text-[#0d151c] text-base font-normal leading-normal pb-3">
                      Engage with our advanced AI model to explore ideas, draft content, and receive assistance on various topics.
                    </p>
                    <div className="text-xs text-[#49749c] bg-[#f1f5f9] rounded-lg p-3 mx-auto max-w-md">
                      💡 <strong>Tip:</strong> Use Shift+Enter for new lines, `code` for inline code, ```code``` for blocks, and more markdown!
                    </div>
                  </div>
                </div>
              ) : (
                // Chat messages
                <div className="flex flex-col gap-4 max-w-[960px] w-full mx-auto">
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`rounded-lg px-4 py-2 ${
                        msg.sender === 'user' 
                          ? 'max-w-[70%] bg-[#0b80ee] text-white' 
                          : msg.isError
                          ? 'w-full bg-red-50 border border-red-200 text-red-700'
                          : 'w-full bg-[#e7edf4] text-[#0d151c]'
                      }`}>
                        {msg.isError && (
                          <div className="flex items-center mb-2">
                            <svg className="h-4 w-4 text-red-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                            <span className="text-xs font-medium">Connection Error</span>
                          </div>
                        )}
                        <MarkdownRenderer content={msg.text} isUser={msg.sender === 'user'} />
                        <p className={`text-xs mt-1 ${
                          msg.sender === 'user' ? 'text-blue-100' : 
                          msg.isError ? 'text-red-500' : 'text-[#49749c]'
                        }`}>
                          {msg.timestamp}
                        </p>
                      </div>
                    </div>
                  ))}
                  {/* Typing Animation */}
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="w-full bg-[#e7edf4] text-[#0d151c] rounded-lg px-4 py-2">
                        <div className="flex items-center gap-2">
                          <div className="flex items-center space-x-1">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 bg-[#49749c] rounded-full animate-bounce"></div>
                              <div className="w-2 h-2 bg-[#49749c] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                              <div className="w-2 h-2 bg-[#49749c] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                          </div>
                          <span className="text-sm text-[#49749c] italic">AI is typing...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  {/* Invisible scroll anchor */}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </section>
          </div>
          
          {/* Enhanced Message Input Area */}
          <div className="border-t border-[#e7edf4] bg-white">
            {/* Markdown Preview */}
            {showPreview && message.trim() && (
              <div className="border-b border-[#e7edf4] px-4 py-3 bg-[#f8fafc]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-[#49749c]">
                    Preview (Slack-style) • Line {getCurrentLine() + 1}
                  </span>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="text-xs text-[#49749c] hover:text-[#0d151c] transition-colors"
                  >
                    ✕
                  </button>
                </div>
                <div 
                  ref={previewRef}
                  className="bg-white rounded-lg border border-[#e7edf4] p-3 max-h-32 overflow-y-auto"
                >
                  <div className="slack-style-preview">
                    {renderStyledMessage(message)}
                  </div>
                </div>
              </div>
            )}
            
            {/* Input Controls */}
            <div className="px-4 py-3">
              <div className="flex items-end gap-3">
                <div className="flex-1">
                  <div className="flex w-full items-end rounded-xl min-h-[48px] bg-[#e7edf4]">
                    <textarea
                      ref={textareaRef}
                      placeholder="Type your message here... (Shift+Enter for new line)"
                      className="flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d151c] focus:outline-0 focus:ring-0 border-none bg-transparent focus:border-none placeholder:text-[#49749c] px-4 py-3 text-base font-normal leading-normal min-h-[48px]"
                      style={{ height: '48px' }}
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      onKeyUp={handleCursorChange}
                      onMouseUp={handleCursorChange}
                      onSelect={handleCursorChange}
                      onFocus={handleCursorChange}
                      rows={1}
                    />
                    <div className="flex flex-col items-center justify-end p-2 gap-2">
                      {/* Markdown Toggle */}
                      {hasMarkdownSyntax() && (
                        <button
                          onClick={() => setShowPreview(!showPreview)}
                          className={`text-sm px-2 py-1 rounded transition-colors ${
                            showPreview 
                              ? 'bg-[#0b80ee] text-white' 
                              : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                          }`}
                          title={showPreview ? "Hide preview" : "Show preview"}
                        >
                          {showPreview ? '🫣' : '🧐'}
                        </button>
                      )}
                      
                      {/* Send Button */}
                      <button
                        onClick={handleSendMessage}
                        className="min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-[#0b80ee] text-slate-50 text-sm font-medium leading-normal hover:bg-[#0a70d6] transition-colors flex disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!message.trim() || isTyping}
                      >
                        {isTyping ? (
                          <div className="flex items-center">
                            <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                            <span className="truncate">Sending...</span>
                          </div>
                        ) : (
                          <span className="truncate">Send</span>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Helper Text */}
              <div className="flex items-center justify-between mt-2 text-xs text-[#49749c]">
                <div className="flex items-center gap-2">
                  <span>Shift+Enter for new line • `code` for inline • ```code``` for blocks</span>
                  {!currentThreadId && (
                    <span className="text-blue-500 font-medium">• Next message will create new thread</span>
                  )}
                  {error && (
                    <span className="text-red-500 font-medium">• Connection failed</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span>{message.length} characters</span>
                  {isTyping && (
                    <span className="text-blue-500 font-medium">• Sending...</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Chat; 