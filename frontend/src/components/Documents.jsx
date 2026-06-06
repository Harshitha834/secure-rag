import { useState, useEffect } from "react";
import { api } from "../api";

const ROLE_COLOR = { admin: "#f59e0b", hr: "#3b82f6", employee: "#22c55e" };

export default function Documents({ auth }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listDocs(auth.token)
      .then((res) => setDocs(res.documents || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [auth.token]);

  const ROLE_PERMISSIONS = {
    employee: ["employee"],
    hr:       ["employee", "hr"],
    admin:    ["employee", "hr", "admin"],
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.h2}>Accessible Documents</h2>
        <p style={styles.sub}>
          Your <strong style={{ color: ROLE_COLOR[auth.role] }}>{auth.role}</strong> role grants access to:{" "}
          {ROLE_PERMISSIONS[auth.role]?.map((r) => (
            <span key={r} style={{ ...styles.permBadge, background: ROLE_COLOR[r] + "25", color: ROLE_COLOR[r] }}>
              {r}
            </span>
          ))}
        </p>
      </div>

      <div style={styles.body}>
        {loading && <p style={styles.info}>Loading documents…</p>}
        {error   && <p style={styles.error}>Error: {error}</p>}

        {!loading && docs.length === 0 && (
          <div style={styles.empty}>
            <p style={{ fontSize: "2.5rem" }}>📭</p>
            <p style={{ color: "#64748b" }}>No documents indexed yet. Upload some first.</p>
          </div>
        )}

        <div style={styles.grid}>
          {docs.map((doc, i) => (
            <div key={i} style={styles.card}>
              <div style={styles.cardIcon}>📄</div>
              <div style={styles.cardBody}>
                <div style={styles.cardName}>{doc.filename}</div>
                <span
                  style={{
                    ...styles.roleBadge,
                    background: (ROLE_COLOR[doc.role] || "#6b7280") + "25",
                    color: ROLE_COLOR[doc.role] || "#6b7280",
                  }}
                >
                  {doc.role}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* RBAC explanation */}
        <div style={styles.rbacBox}>
          <h3 style={styles.rbacTitle}>🔒 Role-Based Access Control</h3>
          <div style={styles.rbacGrid}>
            {[
              { role: "employee", access: "Employee documents only" },
              { role: "hr",       access: "Employee + HR documents" },
              { role: "admin",    access: "All documents including admin secrets" },
            ].map((row) => (
              <div key={row.role} style={{ ...styles.rbacRow, ...(auth.role === row.role ? styles.rbacRowActive : {}) }}>
                <span style={{ ...styles.roleBadge, background: ROLE_COLOR[row.role] + "25", color: ROLE_COLOR[row.role] }}>
                  {row.role}
                </span>
                <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>{row.access}</span>
                {auth.role === row.role && <span style={styles.youBadge}>YOU</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
  header: { padding: "1.25rem 1.5rem", borderBottom: "1px solid #334155", background: "#1e293b" },
  h2: { margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "#f1f5f9" },
  sub: { margin: "0.25rem 0 0", fontSize: "0.82rem", color: "#64748b", display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" },
  body: { flex: 1, overflowY: "auto", padding: "1.5rem" },
  info:  { color: "#64748b" },
  error: { color: "#f87171" },
  empty: { textAlign: "center", padding: "3rem 0" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "1rem", marginBottom: "2rem" },
  card: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "10px",
    padding: "1rem",
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
  },
  cardIcon: { fontSize: "1.8rem", flexShrink: 0 },
  cardBody: { display: "flex", flexDirection: "column", gap: "0.35rem", minWidth: 0 },
  cardName: { color: "#e2e8f0", fontSize: "0.88rem", fontWeight: 600, wordBreak: "break-all" },
  permBadge: { fontSize: "0.7rem", fontWeight: 700, padding: "0.15rem 0.5rem", borderRadius: "4px" },
  roleBadge: { fontSize: "0.7rem", fontWeight: 700, padding: "0.15rem 0.5rem", borderRadius: "4px", display: "inline-block" },
  rbacBox: { background: "#1e293b", border: "1px solid #334155", borderRadius: "12px", padding: "1.25rem" },
  rbacTitle: { margin: "0 0 1rem", color: "#f1f5f9", fontSize: "0.95rem", fontWeight: 700 },
  rbacGrid: { display: "flex", flexDirection: "column", gap: "0.6rem" },
  rbacRow: {
    display: "flex", alignItems: "center", gap: "0.75rem",
    padding: "0.6rem 0.75rem",
    borderRadius: "8px",
    background: "transparent",
  },
  rbacRowActive: { background: "#0f172a", border: "1px solid #334155" },
  youBadge: {
    marginLeft: "auto",
    background: "#1d4ed8",
    color: "#fff",
    fontSize: "0.65rem",
    fontWeight: 800,
    padding: "0.1rem 0.5rem",
    borderRadius: "4px",
    letterSpacing: "0.08em",
  },
};
