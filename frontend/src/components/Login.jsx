import { useState } from "react";
import { api } from "../api";

const DEMO_ACCOUNTS = [
  { user: "alice", pass: "alice123", role: "employee", color: "#22c55e" },
  { user: "bob",   pass: "bob123",   role: "hr",       color: "#3b82f6" },
  { user: "carol", pass: "carol123", role: "admin",    color: "#f59e0b" },
];

export default function Login({ onLogin, onToggle }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (u = username, p = password) => {
    setError(""); setLoading(true);
    try {
      const data = await api.login(u, p);
      onLogin(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (acc) => {
    setUsername(acc.user);
    setPassword(acc.pass);
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.shield}>🛡️</div>
          <h1 style={styles.title}>SecureRAG</h1>
          <p style={styles.subtitle}>Enterprise AI Assistant</p>
        </div>

        {/* Form */}
        <div style={styles.form}>
          <label style={styles.label}>Username</label>
          <input
            style={styles.input}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter username"
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />

          <label style={styles.label}>Password</label>
          <input
            style={styles.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />

          {error && <p style={styles.error}>{error}</p>}

          <button
            style={{ ...styles.btn, opacity: loading ? 0.7 : 1 }}
            onClick={() => submit()}
            disabled={loading}
          >
            {loading ? "Signing in…" : "Sign In"}
          </button>
          <p>
            Don't have an account?{" "}
            <span
              style={{ color: "blue", cursor: "pointer" }}
              onClick={onToggle}
            >
              Register
            </span>
          </p>
        </div>

        {/* Demo accounts */}
        <div style={styles.demoSection}>
          <p style={styles.demoTitle}>Demo Accounts</p>
          <div style={styles.demoGrid}>
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.user}
                style={{ ...styles.demoBtn, borderColor: acc.color, color: acc.color }}
                onClick={() => fillDemo(acc)}
              >
                <span style={styles.demoBadge}>{acc.role.toUpperCase()}</span>
                <span>{acc.user}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "'Segoe UI', sans-serif",
    padding: "1rem",
  },
  card: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "16px",
    padding: "2.5rem",
    width: "100%",
    maxWidth: "420px",
    boxShadow: "0 25px 60px rgba(0,0,0,0.5)",
  },
  header: { textAlign: "center", marginBottom: "2rem" },
  shield: { fontSize: "3rem", marginBottom: "0.5rem" },
  title: { margin: 0, color: "#f1f5f9", fontSize: "1.8rem", fontWeight: 700 },
  subtitle: { margin: "0.25rem 0 0", color: "#94a3b8", fontSize: "0.9rem" },
  form: { display: "flex", flexDirection: "column", gap: "0.6rem" },
  label: { color: "#94a3b8", fontSize: "0.85rem", fontWeight: 600, letterSpacing: "0.05em" },
  input: {
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "8px",
    padding: "0.75rem 1rem",
    color: "#f1f5f9",
    fontSize: "0.95rem",
    outline: "none",
    marginBottom: "0.4rem",
  },
  error: { color: "#f87171", fontSize: "0.85rem", margin: "0.25rem 0" },
  btn: {
    background: "linear-gradient(135deg, #3b82f6, #6366f1)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "0.85rem",
    fontSize: "1rem",
    fontWeight: 700,
    cursor: "pointer",
    marginTop: "0.5rem",
    letterSpacing: "0.03em",
  },
  demoSection: { marginTop: "2rem", borderTop: "1px solid #334155", paddingTop: "1.5rem" },
  demoTitle: { color: "#64748b", fontSize: "0.78rem", textAlign: "center", marginBottom: "0.75rem", letterSpacing: "0.08em" },
  demoGrid: { display: "flex", gap: "0.6rem" },
  demoBtn: {
    flex: 1,
    background: "transparent",
    border: "1px solid",
    borderRadius: "8px",
    padding: "0.5rem 0.25rem",
    cursor: "pointer",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0.2rem",
    fontSize: "0.8rem",
    fontWeight: 600,
    transition: "background 0.2s",
  },
  demoBadge: { fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.06em" },
};
