import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/LoginPage";
import Register from "./pages/RegisterPage";
import Dashboard from "./pages/DashboardPage";
import AdminDashboard from "./pages/AdminDashboardPage";
import AdminClassPage from "./pages/AdminClassPage";

// 🔐 Helpers
const getToken = () => localStorage.getItem("token");
const getRole = () => localStorage.getItem("role");

// 🔐 Protected Route Component
const ProtectedRoute = ({ children, roleRequired }) => {
  const token = getToken();
  const role = getRole();

  // Not logged in
  if (!token) {
    return <Navigate to="/" />;
  }

  // Role mismatch
  if (roleRequired && role !== roleRequired) {
    return <Navigate to="/" />;
  }

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public */}
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Member */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute roleRequired="member">
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Admin */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute roleRequired="admin">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/class/:classCode"
          element={
            <ProtectedRoute roleRequired="admin">
              <AdminClassPage />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;