// API Configuration
const API_CONFIG = {
  // Use empty string when using proxy, otherwise use full URL
  BASE_URL: process.env.REACT_APP_USE_PROXY === 'true' ? '' : (process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'),
  ENDPOINTS: {
    QUERY: '/query'
  }
};

// API Service functions
export const apiService = {
  // Send message to the backend
  // If threadId is null/undefined, creates new thread
  // If threadId is provided, continues existing thread
  sendMessage: async (question, threadId = null) => {
    try {
      // Determine the endpoint URL based on whether we have a thread ID
      const endpoint = threadId 
        ? `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.QUERY}/${threadId}`
        : `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.QUERY}`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  },
  fetchThreadIds: async () => {
    const response = await fetch(`${API_CONFIG.BASE_URL}/fetch_thread_ids`);
    if (!response.ok) throw new Error('Failed to fetch thread ids');
    return response.json();
  },
  // Fetch conversation by thread ID
  fetchConversation: async (threadId) => {
    if (!threadId) throw new Error('Thread ID is required');
    const response = await fetch(`${API_CONFIG.BASE_URL}/fetch_conversation/${threadId}`);
    if (!response.ok) throw new Error('Failed to fetch conversation');
    return response.json();
  }
};

export default API_CONFIG; 