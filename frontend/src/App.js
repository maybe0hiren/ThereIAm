import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/LoginPage";
import Register from "./pages/RegisterPage";
import Dashboard from "./pages/DashboardPage";
import AdminDashboard from "./pages/AdminDashboardPage";
import AdminClassPage from "./pages/AdminClassPage";
import MemberClassPage from "./pages/MemberClassPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";

const getToken = () => localStorage.getItem("token");
const getRole = () => localStorage.getItem("role");

const ProtectedRoute = ({ children, roleRequired }) => {
  const token = getToken();
  const role = getRole();

  if (!token) {
    return <Navigate to="/" />;
  }

  if (roleRequired && role !== roleRequired) {
    return <Navigate to="/" />;
  }

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-email/:token" element={<VerifyEmailPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute roleRequired="member">
              <Dashboard />
            </ProtectedRoute>
          }
        />

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

        <Route
          path="/class/:classCode"
          element={
            <ProtectedRoute roleRequired="member">
              <MemberClassPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;