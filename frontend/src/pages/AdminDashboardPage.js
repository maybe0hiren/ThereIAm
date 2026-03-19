import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";

export default function AdminDashboard() {
  const navigate = useNavigate();

  const [className, setClassName] = useState("");
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  // 🔹 Fetch classes on load
  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      const res = await API.get("/admin/classes", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setClasses(res.data.classes || []);
    } catch (err) {
      console.log(err);
    }
  };

  // 🔹 Create Class
  const handleCreateClass = async () => {
    if (!className) {
      alert("Enter class name");
      return;
    }

    setLoading(true);

    try {
      await API.post(
        "/admin/createClass",
        { className },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setClassName("");
      await fetchClasses();

      alert("Class created!");
    } catch (err) {
      alert(err.response?.data?.error || "Error creating class");
    }

    setLoading(false);
  };

  // 🔹 Navigate to class page
  const handleEnterClass = (classCode) => {
    navigate(`/admin/class/${classCode}`);
  };

  // 🔹 Logout
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    navigate("/");
  };

  return (
    <div className="dashboard">

      {/* Header */}
      <div className="header">
        <h2>Admin Dashboard</h2>
        <button className="secondary-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>

      {/* If NO classes → show create */}
      {classes.length === 0 && (
        <div className="card">
          <h3>Create Your First Class</h3>

          <input
            placeholder="Enter Class Name"
            value={className}
            onChange={(e) => setClassName(e.target.value)}
          />

          <button onClick={handleCreateClass}>
            {loading ? "Creating..." : "Create Class"}
          </button>
        </div>
      )}

      {/* If classes exist */}
      {classes.length > 0 && (
        <>
          {/* Create new class */}
          <div className="card">
            <h3>Create New Class</h3>

            <input
              placeholder="Enter Class Name"
              value={className}
              onChange={(e) => setClassName(e.target.value)}
            />

            <button onClick={handleCreateClass}>
              {loading ? "Creating..." : "Create Class"}
            </button>
          </div>

          {/* Class List */}
          <div className="card">
            <h3>Your Classes</h3>

            <div className="class-list">
              {classes.map((cls, i) => (
                <div key={i} className="class-item">
                  <div>
                    <b>{cls.name}</b>
                    <p>Code: {cls.code}</p>
                  </div>

                  <button onClick={() => handleEnterClass(cls.code)}>
                    Enter
                  </button>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}