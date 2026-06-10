import React, { useState, useEffect } from 'react';
import AuthPage from './components/AuthPage';
import LegalAIAssistant from './components/LegalAIAssistant';

function App() {
  const [user, setUser]   = useState(null);
  const [token, setToken] = useState(null);

  // Clear localStorage on mount to ensure we never auto-login from old sessions
  useEffect(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }, []);

  const handleAuth = (userData, accessToken) => {
    setUser(userData);
    setToken(accessToken);
  };

  const handleLogout = () => {
    setUser(null);
    setToken(null);
  };

  if (!user || !token) {
    return <AuthPage onAuth={handleAuth} />;
  }

  return (
    <div className="min-h-screen">
      <LegalAIAssistant user={user} token={token} onLogout={handleLogout} />
    </div>
  );
}

export default App;
