import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import "./AdminDashboardPage.css";

export default function AdminDashboardPage() {
  const navigate = useNavigate();

  const [className, setClassName] = useState("");
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

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

  const handleEnterClass = (classCode) => {
    navigate(`/admin/class/${classCode}`);
  };

  const deleteClass = async (classCode) => {
    if (!classCode) {
      alert("Select a Class");
      return;
    }

    setLoading(true);

    try {
      await API.post(
        "/admin/deleteClass",
        { classCode },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setClasses((prev) => prev.filter((c) => c.code !== classCode));
      alert("Class deleted!");
    } catch (err) {
      alert(err.response?.data?.error || "Error Deleting class");
    }

    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    navigate("/");
  };

  return (
    <div className="dashboard">
      <Header title="Admin Dashboard">
        <Button className="secondary-btn" onClick={handleLogout}>
          Logout
        </Button>
      </Header>

      {classes.length === 0 && (
        <Card>
          <h3>Create Your First Class</h3>

          <input
            placeholder="Enter Class Name"
            value={className}
            onChange={(e) => setClassName(e.target.value)}
          />

          <Button onClick={handleCreateClass}>
            {loading ? "Creating..." : "Create Class"}
          </Button>
        </Card>
      )}

      {classes.length > 0 && (
        <>
          <Card>
            <h3>Create New Class</h3>

            <input
              placeholder="Enter Class Name"
              value={className}
              onChange={(e) => setClassName(e.target.value)}
            />

            <Button onClick={handleCreateClass}>
              {loading ? "Creating..." : "Create Class"}
            </Button>
          </Card>

          <Card>
            <h3>Your Classes</h3>

            <div className="class-list">
              {classes.map((cls, i) => (
                <div key={i} className="class-item">
                  <div>
                    <b>{cls.name}</b>
                    <p>Code: {cls.code}</p>
                  </div>

                  <div className="actions">
                    <Button onClick={() => handleEnterClass(cls.code)}>
                      Enter
                    </Button>

                    <Button onClick={() => deleteClass(cls.code)}>
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}