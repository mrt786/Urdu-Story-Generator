import React, { useState, useEffect, useRef } from 'react';

// Dummy comment to trigger Vercel redeploy

function uuid() {
  return Math.random().toString(36).slice(2, 9);
}

const STORAGE_KEY = 'urdu_chats_v1';

function loadChats() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveChats(chats) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
}

function App() {
  const [chats, setChats] = useState(loadChats());
  const [activeChatId, setActiveChatId] = useState(chats[0]?.id || null);
  const [input, setInput] = useState('');
  const [maxLength, setMaxLength] = useState(500);
  const [temperature, setTemperature] = useState(0.8);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState('');
  const [theme, setTheme] = useState(localStorage.getItem('urdu_theme') || 'dark');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesRef = useRef(null);

  // Persist theme preference
  useEffect(() => {
    localStorage.setItem('urdu_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    setActiveChatId((prev) => prev || chats[0]?.id || null);
    saveChats(chats);
  }, [chats]);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [chats, activeChatId]);

  function toggleTheme() {
    setTheme(theme === 'dark' ? 'light' : 'dark');
    setSidebarOpen(false);
  }

  function createNewChat() {
    const id = uuid();
    const newChat = { id, title: 'New Chat', messages: [], created_at: Date.now() };
    setChats([newChat, ...chats]);
    setActiveChatId(id);
  }

  function addMessage(chatId, role, text) {
    setChats((prev) => {
      return prev.map((c) => (c.id === chatId ? { ...c, messages: [...c.messages, { role, text, ts: Date.now() }] } : c));
    });
  }

  const activeChat = chats.find((c) => c.id === activeChatId) || null;

  async function generateStory(e) {
    e && e.preventDefault();
    setError('');
    if (!activeChatId) {
      createNewChat();
    }
    const chatId = activeChatId || chats[0]?.id;
    addMessage(chatId, 'user', input || '');
    setIsStreaming(true);

    try {
      const API_BASE = 'https://urdu-story-generator.onrender.com'; // Temporary hardcoded for testing
      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prefix: input || '',
          max_length: Number(maxLength),
          temperature: Number(temperature),
        }),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }
      const data = await res.json();
      console.log(data)
      if (data.success) {
        addMessage(chatId, 'bot', data.story);
      } else {
        addMessage(chatId, 'bot', 'Error: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      setError('Error: ' + err.message);
      addMessage(chatId, 'bot', 'Error during generation.');
    } finally {
      setIsStreaming(false);
      setInput('');
    }
  }

  function selectChat(id) {
    setActiveChatId(id);
  }

  function renameChat(id, title) {
    setChats((prev) => prev.map((c) => (c.id === id ? { ...c, title } : c)));
  }

  function deleteChat(id) {
    setChats((prev) => prev.filter((c) => c.id !== id));
    if (activeChatId === id) setActiveChatId(null);
  }

  return (
    <div className={`app ${theme}`}>
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Chats</h2>
          <button onClick={createNewChat} className="small-btn">New</button>
        </div>
        <div className="chat-list">
          {chats.map((c) => (
            <div key={c.id} className={`chat-item ${c.id === activeChatId ? 'active' : ''}`} onClick={() => selectChat(c.id)}>
              <div className="chat-title">{c.title || 'Untitled'}</div>
              <div className="chat-meta">{new Date(c.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </aside>

      <main className="chat-main">
        <header className="chat-top">
          <button className="menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
          <h1>{activeChat?.title || 'کہانی جنریٹر'}</h1>
          <div className="header-actions">
            <button className="theme-btn" onClick={toggleTheme} title="Toggle theme">
              {theme === 'dark' ? '🌙' : '☀️'}
            </button>
            {activeChat && (
              <div className="chat-actions">
                <button onClick={() => renameChat(activeChat.id, prompt('نیا عنوان:', activeChat.title) || activeChat.title)} className="small-btn">نام بدلیں</button>
                <button onClick={() => deleteChat(activeChat.id)} className="small-btn danger">حذف</button>
              </div>
            )}
          </div>
        </header>

        <section className="messages" ref={messagesRef}>
          {activeChat ? (
            activeChat.messages.map((m, i) => (
              <div key={i} className={`message ${m.role}`}>
                <div className="message-text" dir={m.role === 'user' ? 'rtl' : 'auto'}>{m.text}</div>
              </div>
            ))
          ) : (
            <div className="empty">Create or select a chat to begin.</div>
          )}
        </section>

        <form className="composer" onSubmit={generateStory}>
          <textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="اردو میں لکھیں یا خالی چھوڑیں..." dir="rtl"></textarea>
          <div className="controls">
            <div className="controls-left">
              <label>زیادہ سے زیادہ: <input type="number" value={maxLength} onChange={(e)=>setMaxLength(e.target.value)} min="1" max="2000"/></label>
              <label>درجہ حرارت: <input type="number" value={temperature} onChange={(e)=>setTemperature(e.target.value)} step="0.1" min="0.1" max="2"/></label>
            </div>
            <div className="controls-right">
              <button type="submit" className="primary" disabled={isStreaming}>{isStreaming ? 'تیار ہو رہے ہیں...' : 'کہانی بنائیں'}</button>
            </div>
          </div>
        </form>

        {error && <div className="error">{error}</div>}
      </main>
    </div>
  );
}

export default App;