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
  const [images, setImages] = useState([])

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

  const handleSearch = async () => {
    if (!classCode) {
      alert("Enter class code first");
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");

      const res = await API.post(
        "/search",
        { classCode },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setImages(res.data.images || []);
    } catch (err) {
      alert(err.response?.data?.error || "Search failed");
    }

    setLoading(false);
  };


  const handleDeleteImage = async (imageID) => {
    try {
      const token = localStorage.getItem("token");

      await API.post(
        "/admin/deleteImage",
        { imageID },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setImages((prev) => prev.filter((img) => img.id !== imageID));

    } catch (err) {
      alert(err.response?.data?.error || "Delete failed");
    }
  };


  const downloadImage = async (imgPath, index) => {
    try {
      const url = `http://localhost:5000/images/${imgPath}`;

      const response = await fetch(url);
      const blob = await response.blob();

      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `image_${index}.jpg`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert("Download failed");
    }
  };


  const getAllImages = async () => {
    if (!classCode) {
      alert("Enter class code first");
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");

      const res = await API.post(
        "/admin/getAllImages",
        { classCode },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      console.log("API images:", res.data.images);
      setImages(res.data.images || []);
    } catch (err) {
      alert(err.response?.data?.error || "Search failed");
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
      <Card>
        <Button onClick={getAllImages}>Show All Images</Button>
        <Button onClick={handleSearch}>Show My Images</Button>
        <br />
        <br />
        <div className="grid">
          {images.map((img, i) => (
            <div key={i}>
              <img src={`http://localhost:5000/images/${img.path}`} />
              <Button onClick={() => handleDeleteImage(img.id)}>
                Delete
              </Button>
              <Button onClick={() => downloadImage(img.path, i)}>
                Download
              </Button>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}