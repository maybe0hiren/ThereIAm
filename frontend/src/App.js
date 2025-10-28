import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { supabase } from "./supabaseClient";
import LoginPage from "./Pages/LoginPage";
import FaceCapPage from "./Pages/FaceCapPage";
import DashboardPage from "./Pages/DashboardPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthRedirect />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/face_capture" element={<FaceCapPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </Router>
  );
}

function AuthRedirect() {
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        navigate("/login");
        setChecking(false);
        return;
      }

      // ✅ Check if user already uploaded face video
      const { data: files, error } = await supabase.storage
        .from("user_faces")
        .list(user.id, { limit: 1 });

      if (error) {
        console.error("Storage check error:", error);
        navigate("/face_capture");
      } else if (!files || files.length === 0) {
        navigate("/face_capture");
      } else {
        navigate("/dashboard");
      }

      setChecking(false);
    }

    checkAuth();
  }, [navigate]);

  if (checking) {
    return (
      <div
        style={{
          height: "100vh",
          background: "#1a1a1a",
          color: "#ffdd57",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontFamily: "Poppins, sans-serif",
          fontSize: "1.2rem",
        }}
      >
        Checking authentication...
      </div>
    );
  }

  return null;
}

export default App;
