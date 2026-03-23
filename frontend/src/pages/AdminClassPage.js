import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import API from "../api";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import "./AdminClassPage.css";

export default function AdminClassPage() {
  const navigate = useNavigate();
  const { classCode } = useParams();

  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

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

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    navigate("/");
  };

  return (
    <div className="dashboard">
      <Header title={`Class: ${classCode}`}>
        <div className="header-actions">
          <Button onClick={() => navigate("/admin")}>Back</Button>
          <Button onClick={handleLogout}>Logout</Button>
        </div>
      </Header>

      <Card>
        <h3>Class Code</h3>
        <p className="class-code">{classCode}</p>
      </Card>

      <Card>
        <h3>Upload Photos</h3>

        <input
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
        />

        <Button onClick={handleUpload}>
          {loading ? "Uploading..." : "Upload Photos"}
        </Button>
      </Card>
    </div>
  );
}