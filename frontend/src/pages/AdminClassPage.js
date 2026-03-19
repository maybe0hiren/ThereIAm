import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import API from "../api";

export default function AdminClassPage() {
  const navigate = useNavigate();
  const { classCode } = useParams();

  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  // 🔹 Upload Photos
  const handleUpload = async () => {
    if (!files || files.length === 0) {
      alert("Select images first");
      return;
    }

    setLoading(true);

    const data = new FormData();
    data.append("classCode", classCode);

    for (let file of files) {
      data.append("photos", file);
    }

    try {
      const res = await API.post("/admin/uploadPhotos", data, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      alert(`Uploaded ${res.data.count} images`);
      setFiles([]);

    } catch (err) {
      alert(err.response?.data?.error || "Upload failed");
    }

    setLoading(false);
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
        <h2>Class: {classCode}</h2>

        <div>
          <button
            className="secondary-btn"
            onClick={() => navigate("/admin")}
          >
            Back
          </button>

          <button
            className="secondary-btn"
            onClick={handleLogout}
            style={{ marginLeft: "10px" }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* Class Info */}
      <div className="card">
        <h3>Class Code</h3>
        <p style={{ fontSize: "20px", fontWeight: "bold" }}>
          {classCode}
        </p>
      </div>

      {/* Upload Section */}
      <div className="card">
        <h3>Upload Photos</h3>

        <input
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
        />

        <button onClick={handleUpload}>
          {loading ? "Uploading..." : "Upload Photos"}
        </button>
      </div>

    </div>
  );
}