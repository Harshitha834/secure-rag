import { useState, useRef, useEffect } from "react";
import { api } from "../api";

export default function Chat({ auth }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: `Hello ${auth.username}! I'm your secure AI assistant. You can ask me questions about documents you have access to based on your **${auth.role}** role.`,
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const res = await api.query(text, auth.token);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: res.answer,
          sources: res.sources || [],
          alert: res.security_alert,
        },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: `Error: ${e.message}`, sources: [], isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const SUGGESTIONS = [
    "What are the company work policies?",
    "How does the leave policy work?",
    "What are the training benefits?",
  ];

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h2 style={styles.h2}>AI Assistant</h2>
          <p style={styles.sub}>Documents filtered by your <strong style={{ color: "#3b82f6" }}>{auth.role}</strong> role</p>
        </div>
      </div>

      {/* Messages */}
      <div style={styles.messages}>
        {messages.map((msg, i) => (
          <div key={i} style={{ ...styles.msgRow, justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
            {msg.role === "assistant" && <div style={styles.botAvatar}>🛡️</div>}
            <div
              style={{
                ...styles.bubble,
                ...(msg.role === "user" ? styles.userBubble : styles.botBubble),
                ...(msg.isError ? styles.errorBubble : {}),
              }}
            >
              {msg.alert && (
                <div style={styles.alertBox}>
                  ⚠️ <strong>Security Alert:</strong> {msg.alert}
                </div>
              )}
              <p style={styles.msgText}>{msg.text}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div style={styles.sources}>
                  <span style={styles.sourcesLabel}>Sources:</span>
                  {msg.sources.map((s, j) => (
                    <span key={j} style={styles.sourceTag}>📄 {s}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ ...styles.msgRow, justifyContent: "flex-start" }}>
            <div style={styles.botAvatar}>🛡️</div>
            <div style={{ ...styles.bubble, ...styles.botBubble }}>
              <div style={styles.dots}>
                <span style={{ ...styles.dot, animationDelay: "0s" }} />
                <span style={{ ...styles.dot, animationDelay: "0.2s" }} />
                <span style={{ ...styles.dot, animationDelay: "0.4s" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div style={styles.suggestions}>
          {SUGGESTIONS.map((s, i) => (
            <button key={i} style={styles.suggBtn} onClick={() => { setInput(s); }}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div style={styles.inputRow}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents…"
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button style={{ ...styles.sendBtn, opacity: loading ? 0.6 : 1 }} onClick={send} disabled={loading}>
          ➤
        </button>
      </div>

      <style>{`
        @keyframes bounce {
          0%,80%,100%{transform:translateY(0)}
          40%{transform:translateY(-6px)}
        }
      `}</style>
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
  header: {
    padding: "1.25rem 1.5rem",
    borderBottom: "1px solid #334155",
    background: "#1e293b",
  },
  h2: { margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "#f1f5f9" },
  sub: { margin: "0.25rem 0 0", fontSize: "0.82rem", color: "#64748b" },
  messages: { flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" },
  msgRow: { display: "flex", alignItems: "flex-start", gap: "0.6rem" },
  botAvatar: { fontSize: "1.4rem", marginTop: "0.1rem", flexShrink: 0 },
  bubble: { maxWidth: "72%", borderRadius: "12px", padding: "0.85rem 1rem" },
  userBubble: { background: "#3b82f6", color: "#fff" },
  botBubble: { background: "#1e293b", border: "1px solid #334155", color: "#e2e8f0" },
  errorBubble: { background: "#7f1d1d", borderColor: "#991b1b" },
  alertBox: {
    background: "#431407",
    border: "1px solid #c2410c",
    borderRadius: "8px",
    padding: "0.5rem 0.75rem",
    marginBottom: "0.5rem",
    fontSize: "0.82rem",
    color: "#fed7aa",
  },
  msgText: { margin: 0, fontSize: "0.9rem", lineHeight: 1.6, whiteSpace: "pre-wrap" },
  sources: { marginTop: "0.6rem", display: "flex", flexWrap: "wrap", gap: "0.35rem", alignItems: "center" },
  sourcesLabel: { fontSize: "0.72rem", color: "#64748b", fontWeight: 600 },
  sourceTag: {
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "6px",
    padding: "0.15rem 0.5rem",
    fontSize: "0.72rem",
    color: "#94a3b8",
  },
  dots: { display: "flex", gap: "4px", padding: "4px 0" },
  dot: {
    width: "8px", height: "8px",
    borderRadius: "50%",
    background: "#64748b",
    display: "inline-block",
    animation: "bounce 1.2s infinite",
  },
  suggestions: {
    padding: "0 1.5rem 1rem",
    display: "flex",
    flexWrap: "wrap",
    gap: "0.5rem",
  },
  suggBtn: {
    background: "#1e293b",
    border: "1px solid #334155",
    color: "#94a3b8",
    borderRadius: "20px",
    padding: "0.4rem 0.9rem",
    fontSize: "0.8rem",
    cursor: "pointer",
    transition: "all 0.15s",
  },
  inputRow: {
    display: "flex",
    gap: "0.5rem",
    padding: "1rem 1.5rem",
    borderTop: "1px solid #334155",
    background: "#1e293b",
  },
  input: {
    flex: 1,
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "8px",
    padding: "0.75rem 1rem",
    color: "#f1f5f9",
    fontSize: "0.9rem",
    outline: "none",
  },
  sendBtn: {
    background: "linear-gradient(135deg,#3b82f6,#6366f1)",
    border: "none",
    color: "#fff",
    borderRadius: "8px",
    padding: "0 1.2rem",
    fontSize: "1.1rem",
    cursor: "pointer",
    fontWeight: 700,
  },
};
