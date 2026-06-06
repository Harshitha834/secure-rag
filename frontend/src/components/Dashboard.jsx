import { useState } from "react";
import Chat from "./Chat";
import Upload from "./Upload";
import Documents from "./Documents";

const ROLE_COLOR = { admin: "#f59e0b", hr: "#3b82f6", employee: "#22c55e" };
const TABS = ["Chat", "Documents", "Upload"];

export default function Dashboard({ auth, onLogout }) {
  const [tab, setTab] = useState("Chat");
  const roleColor = ROLE_COLOR[auth.role] || "#94a3b8";

  return (
    <div style={styles.layout}>
      {/* Sidebar */}
      <aside style={styles.sidebar}>
        <div style={styles.sideTop}>
          <div style={styles.logo}>🛡️ SecureRAG</div>
          <div style={styles.userCard}>
            <div style={{ ...styles.avatar, background: roleColor }}>
              {auth.username[0].toUpperCase()}
            </div>
            <div>
              <div style={styles.userName}>{auth.username}</div>
              <span style={{ ...styles.roleBadge, background: roleColor + "30", color: roleColor }}>
                {auth.role.toUpperCase()}
              </span>
            </div>
          </div>

          <nav style={styles.nav}>
            {TABS.map((t) => {
              // Hide Upload tab for employees
              if (t === "Upload" && auth.role === "employee") return null;
              return (
                <button
                  key={t}
                  style={{ ...styles.navBtn, ...(tab === t ? styles.navBtnActive : {}) }}
                  onClick={() => setTab(t)}
                >
                  {t === "Chat" && "💬 "}
                  {t === "Documents" && "📄 "}
                  {t === "Upload" && "📤 "}
                  {t}
                </button>
              );
            })}
          </nav>
        </div>

        <button style={styles.logoutBtn} onClick={onLogout}>
          🚪 Sign Out
        </button>
      </aside>

      {/* Main */}
      <main style={styles.main}>
        {tab === "Chat"      && <Chat auth={auth} />}
        {tab === "Documents" && <Documents auth={auth} />}
        {tab === "Upload"    && <Upload auth={auth} />}
      </main>
    </div>
  );
}

const styles = {
  layout: {
    display: "flex",
    height: "100vh",
    background: "#0f172a",
    fontFamily: "'Segoe UI', sans-serif",
    color: "#f1f5f9",
  },
  sidebar: {
    width: "240px",
    minWidth: "240px",
    background: "#1e293b",
    borderRight: "1px solid #334155",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "1.5rem 1rem",
  },
  sideTop: { display: "flex", flexDirection: "column", gap: "1.5rem" },
  logo: { fontSize: "1.1rem", fontWeight: 800, color: "#f1f5f9", letterSpacing: "0.02em" },
  userCard: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    background: "#0f172a",
    borderRadius: "10px",
    padding: "0.75rem",
  },
  avatar: {
    width: "36px", height: "36px",
    borderRadius: "50%",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "1rem", fontWeight: 700, color: "#0f172a",
    flexShrink: 0,
  },
  userName: { fontWeight: 600, fontSize: "0.9rem" },
  roleBadge: {
    fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.08em",
    padding: "0.15rem 0.5rem", borderRadius: "4px",
  },
  nav: { display: "flex", flexDirection: "column", gap: "0.4rem" },
  navBtn: {
    background: "transparent",
    border: "none",
    color: "#94a3b8",
    textAlign: "left",
    padding: "0.7rem 0.9rem",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: 500,
    transition: "all 0.15s",
  },
  navBtnActive: { background: "#334155", color: "#f1f5f9", fontWeight: 700 },
  logoutBtn: {
    background: "transparent",
    border: "1px solid #334155",
    color: "#94a3b8",
    borderRadius: "8px",
    padding: "0.65rem 0.9rem",
    cursor: "pointer",
    fontSize: "0.85rem",
    textAlign: "left",
    fontWeight: 500,
  },
  main: { flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" },
};
