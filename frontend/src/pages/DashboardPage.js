import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import Header from "../components/Header";
import Button from "../components/Button";
import "./DashboardPage.css";

export default function Dashboard() {
  const navigate = useNavigate();

  const [classCode, setClassCode] = useState("");
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  // 🔹 Fetch user classes
  const fetchClasses = async () => {
    try {
      const res = await API.get("/myClasses", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      // 🔥 Sort classes alphabetically
      const sorted = (res.data.classes || []).sort((a, b) =>
        a.name.localeCompare(b.name)
      );

      setClasses(sorted);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  // 🔹 Join class via code
  const handleJoinClass = async () => {
    if (!classCode) {
      alert("Enter class code first");
      return;
    }

    const upperCode = classCode.toUpperCase();

    // 🔥 Prevent duplicate join
    if (classes.some((c) => c.code === upperCode)) {
      navigate(`/class/${upperCode}`);
      return;
    }

    setLoading(true);

    try {
      await API.post(
        "/classMembers",
        { classCode: upperCode },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // 🔥 Refresh classes
      await fetchClasses();

      // 🔥 Clear input
      setClassCode("");

      // 🔥 Navigate
      navigate(`/class/${upperCode}`);

    } catch (err) {
      alert(err.response?.data?.error || "Failed to join class");
    }

    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="dashboard">
      <Header title="ThereIAm">
        <Button className="secondary-btn" onClick={handleLogout}>
          Logout
        </Button>
      </Header>

      {/* 🔹 Join Class */}
      <div className="card">
        <h3>Join a Class</h3>

        <input
          placeholder="Enter Class Code"
          value={classCode}
          onChange={(e) => setClassCode(e.target.value.toUpperCase())}
        />

        <Button onClick={handleJoinClass} disabled={!classCode || loading}>
          {loading ? "Joining..." : "Enter Class"}
        </Button>
      </div>

      {/* 🔹 My Classes */}
      <div className="card">
        <h3>My Classes</h3>

        {classes.length === 0 ? (
          <p>No classes joined yet</p>
        ) : (
          <div className="class-list">
            {classes.map((cls, i) => (
              <div key={i} className="class-item">
                <div>
                  <b>{cls.name}</b>
                  <p>Code: {cls.code}</p>
                </div>

                <Button onClick={() => navigate(`/class/${cls.code}`)}>
                  Enter
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}