import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import Header from "../components/Header";
import Button from "../components/Button";
import "./DashboardPage.css";

export default function Dashboard() {
  const navigate = useNavigate();

  const [classCode, setClassCode] = useState("");
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);

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

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
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

  return (
    <div className="dashboard">
      <Header title="ThereIAm">
        <Button className="secondary-btn" onClick={handleLogout}>
          Logout
        </Button>
      </Header>

      <div className="search-section">
        <input
          placeholder="Enter Class Code"
          value={classCode}
          onChange={(e) => setClassCode(e.target.value.toUpperCase())}
        />

        <Button onClick={handleSearch} disabled={!classCode}>
          {loading ? "Searching..." : "Find My Photos"}
        </Button>
      </div>

      <div className="grid">
        {images.map((img, i) => (
          <div key={i}>
            <img src={`http://localhost:5000/images/${img}`} alt="result" />
            <Button onClick={() => downloadImage(img, i)}>Download</Button>
          </div>
        ))}
      </div>
    </div>
  );
}