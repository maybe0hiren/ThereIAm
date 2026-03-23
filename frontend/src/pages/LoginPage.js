import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import Card from "../components/Card";
import Button from "../components/Button";
import "./LoginPage.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await API.post("/login", { email, password });

      localStorage.setItem("token", res.data.token);
      localStorage.setItem("role", res.data.role);

      if (res.data.role === "admin") {
        navigate("/admin");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      alert(err.response?.data?.error || "Login failed");
    }
  };

  return (
    <Card>
      <h2>Login</h2>

      <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />

      <Button onClick={handleLogin}>Login</Button>

      <Button className="secondary-btn" onClick={() => navigate("/register")}>
        New User?
      </Button>
    </Card>
  );
}