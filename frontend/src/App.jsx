import { useState } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [auth, setAuth] = useState(() => {
    const token = localStorage.getItem("rag_token");
    const role  = localStorage.getItem("rag_role");
    const user  = localStorage.getItem("rag_user");
    return token ? { token, role, username: user } : null;
  });

  const handleLogin = (data) => {
    localStorage.setItem("rag_token", data.access_token);
    localStorage.setItem("rag_role",  data.role);
    localStorage.setItem("rag_user",  data.username);
    setAuth({ token: data.access_token, role: data.role, username: data.username });
  };

  const handleLogout = () => {
    localStorage.clear();
    setAuth(null);
  };

  return auth
    ? <Dashboard auth={auth} onLogout={handleLogout} />
    : <Login onLogin={handleLogin} />;
}
