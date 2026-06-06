const BASE = "http://localhost:8000";

async function request(method, path, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  login: (username, password) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    }).then(async (r) => {
      if (!r.ok) throw new Error((await r.json()).detail || "Login failed");
      return r.json();
    });
  },

  query: (text, token) =>
    request("POST", "/query", { query: text }, token),

  listDocs: (token) =>
    request("GET", "/documents/list", null, token),

  uploadDoc: (file, docRole, token) => {
    const form = new FormData();
    form.append("file", file);
    form.append("doc_role", docRole);
    return fetch(`${BASE}/documents/upload`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    }).then(async (r) => {
      if (!r.ok) throw new Error((await r.json()).detail || "Upload failed");
      return r.json();
    });
  },
};
