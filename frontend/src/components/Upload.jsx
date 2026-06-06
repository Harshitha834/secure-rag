import { useState, useRef } from "react";
import { api } from "../api";

const ROLE_OPTIONS = ["employee", "hr", "admin"];
const ROLE_COLOR = { admin: "#f59e0b", hr: "#3b82f6", employee: "#22c55e" };

export default function Upload({ auth }) {
  const [file, setFile]       = useState(null);
  const [docRole, setDocRole] = useState("employee");
  const [status, setStatus]   = useState(null); // {type:'success'|'error', msg}
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  const handleFile = (f) => {
    if (f && f.type === "text/plain") setFile(f);
    else setStatus({ type: "error", msg: "Only .txt files are supported." });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const upload = async () => {
    if (!file) { setStatus({ type: "error", msg: "Please select a file first." }); return; }
    setLoading(true); setStatus(null);
    try {
      const res = await api.uploadDoc(file, docRole, auth.token);
      setStatus({ type: "success", msg: `✓ ${res.message} (${res.chunks} chunks indexed)` });
      setFile(null);
    } catch (e) {
      setStatus({ type: "error", msg: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.h2}>Upload Document</h2>
        <p style={styles.sub}>Index a .txt file into the secure knowledge base</p>
      </div>

      <div style={styles.body}>
        <div style={styles.card}>
          {/* Drop zone */}
          <div
            style={{
              ...styles.dropzone,
              borderColor: file ? "#22c55e" : "#334155",
              background: file ? "#052e16" : "#0f172a",
            }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => inputRef.current.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".txt"
              style={{ display: "none" }}
              onChange={(e) => handleFile(e.target.files[0])}
            />
            {file ? (
              <>
                <p style={{ fontSize: "2rem" }}>✅</p>
                <p style={{ color: "#22c55e", fontWeight: 600 }}>{file.name}</p>
                <p style={{ color: "#64748b", fontSize: "0.8rem" }}>
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </>
            ) : (
              <>
                <p style={{ fontSize: "2.5rem" }}>📁</p>
                <p style={{ color: "#94a3b8", fontWeight: 600 }}>Drop a .txt file here</p>
                <p style={{ color: "#64748b", fontSize: "0.8rem" }}>or click to browse</p>
              </>
            )}
          </div>

          {/* Role selector */}
          <div style={styles.field}>
            <label style={styles.label}>Document Access Role</label>
            <p style={styles.labelHint}>
              Only users with this role (or above) will be able to retrieve this document.
            </p>
            <div style={styles.roleRow}>
              {ROLE_OPTIONS.map((r) => (
                <button
                  key={r}
                  style={{
                    ...styles.roleBtn,
                    ...(docRole === r
                      ? { background: ROLE_COLOR[r] + "25", borderColor: ROLE_COLOR[r], color: ROLE_COLOR[r] }
                      : {}),
                  }}
                  onClick={() => setDocRole(r)}
                >
                  {r.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Status */}
          {status && (
            <div style={{ ...styles.statusBox, ...(status.type === "success" ? styles.success : styles.error) }}>
              {status.msg}
            </div>
          )}

          {/* Submit */}
          <button
            style={{ ...styles.btn, opacity: loading ? 0.7 : 1 }}
            onClick={upload}
            disabled={loading}
          >
            {loading ? "Uploading…" : "📤 Upload & Index Document"}
          </button>
        </div>

        {/* Info */}
        <div style={styles.infoBox}>
          <h3 style={styles.infoTitle}>How document indexing works</h3>
          <ol style={styles.ol}>
            <li>Document text is split into overlapping chunks of ~400 characters</li>
            <li>Each chunk is converted to a 384-dim vector using <code>all-MiniLM-L6-v2</code></li>
            <li>Vectors are stored in a FAISS index with role metadata</li>
            <li>At query time, only chunks matching the user's role are retrieved</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" },
  header: { padding: "1.25rem 1.5rem", borderBottom: "1px solid #334155", background: "#1e293b" },
  h2: { margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "#f1f5f9" },
  sub: { margin: "0.25rem 0 0", fontSize: "0.82rem", color: "#64748b" },
  body: { flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1.5rem" },
  card: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "12px",
    padding: "1.5rem",
    display: "flex",
    flexDirection: "column",
    gap: "1.25rem",
  },
  dropzone: {
    border: "2px dashed",
    borderRadius: "10px",
    padding: "2.5rem 1rem",
    textAlign: "center",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  field: { display: "flex", flexDirection: "column", gap: "0.4rem" },
  label: { color: "#94a3b8", fontSize: "0.85rem", fontWeight: 700, letterSpacing: "0.04em" },
  labelHint: { color: "#64748b", fontSize: "0.78rem", margin: 0 },
  roleRow: { display: "flex", gap: "0.6rem" },
  roleBtn: {
    flex: 1,
    background: "#0f172a",
    border: "1px solid #334155",
    color: "#64748b",
    borderRadius: "8px",
    padding: "0.6rem",
    cursor: "pointer",
    fontSize: "0.8rem",
    fontWeight: 700,
    transition: "all 0.15s",
  },
  statusBox: { borderRadius: "8px", padding: "0.75rem 1rem", fontSize: "0.88rem", fontWeight: 500 },
  success: { background: "#052e16", color: "#22c55e", border: "1px solid #16a34a" },
  error:   { background: "#450a0a", color: "#f87171", border: "1px solid #dc2626" },
  btn: {
    background: "linear-gradient(135deg, #3b82f6, #6366f1)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "0.85rem",
    fontSize: "0.95rem",
    fontWeight: 700,
    cursor: "pointer",
  },
  infoBox: {
    background: "#1e293b",
    border: "1px solid #334155",
    borderRadius: "12px",
    padding: "1.25rem",
  },
  infoTitle: { margin: "0 0 0.75rem", color: "#f1f5f9", fontSize: "0.95rem", fontWeight: 700 },
  ol: { margin: 0, paddingLeft: "1.2rem", color: "#94a3b8", fontSize: "0.85rem", lineHeight: 2 },
};
