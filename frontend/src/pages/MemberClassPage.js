import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import API from "../api";
import Header from "../components/Header";
import Card from "../components/Card";
import Button from "../components/Button";
import "./MemberClassPage.css";

export default function MemberClassPage() {
  const navigate = useNavigate();
  const { classCode } = useParams();

  const [members, setMembers] = useState([]);
  const [selectedFriends, setSelectedFriends] = useState([]);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedImages, setSelectedImages] = useState([]);

  const token = localStorage.getItem("token");

  const fetchMembers = async () => {
    try {
      const res = await API.post(
        "/classMembers",
        { classCode },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMembers(res?.data?.members || []);
    } catch (err) {
      alert("Failed to load members");
    }
  };

  useEffect(() => {
    fetchMembers();
  }, []);

  const toggleFriend = (userID) => {
    setSelectedFriends((prev) =>
      prev.includes(userID)
        ? prev.filter((id) => id !== userID)
        : [...prev, userID]
    );
  };

  const handleSearch = async () => {
    setLoading(true);

    try {
      const res = await API.post(
        "/search",
        {
          classCode,
          friendIDs: selectedFriends,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setImages(res?.data?.images || []);
      setSelectedImages([]);
    } catch (err) {
      alert(err.response?.data?.error || "Search failed");
    }

    setLoading(false);
  };

  const toggleImageSelection = (imageID) => {
    setSelectedImages((prev) =>
      prev.includes(imageID)
        ? prev.filter((id) => id !== imageID)
        : [...prev, imageID]
    );
  };

  const handleSelectAll = () => {
    if (selectedImages.length === images.length) {
      setSelectedImages([]);
    } else {
      setSelectedImages(images.map((img) => img.id));
    }
  };

  const downloadSelectedImages = async () => {
    try {
      const selected = images.filter((img) =>
        selectedImages.includes(img.id)
      );

      for (const img of selected) {
        const url = `http://localhost:5000/images/${img.path}`;
        const response = await fetch(url);
        const blob = await response.blob();

        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = img.path.split("/").pop();

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      alert("Download failed");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="dashboard">
      <Header title={`Class: ${classCode}`}>
        <div className="header-actions">
          <Button onClick={() => navigate("/dashboard")}>Back</Button>
          <Button onClick={handleLogout}>Logout</Button>
        </div>
      </Header>

      <Card>
        <h3>Select Friends</h3>

        <div className="members-list">
          {members?.map((member) => (
            <div
              key={member.id}
              className={`member-item ${
                selectedFriends.includes(member.id) ? "selected" : ""
              }`}
              onClick={() => toggleFriend(member.id)}
            >
              {member.name}
            </div>
          ))}
        </div>

        <Button onClick={handleSearch}>
          {loading ? "Searching..." : "Get Images"}
        </Button>
      </Card>

      <Card>
        <h3>Your Images Appear Here...</h3>

        {images.length > 0 && (
          <div className="image-actions">
            <Button onClick={handleSelectAll}>
              {selectedImages.length === images.length
                ? "Unselect All"
                : "Select All"}
            </Button>

            <Button
              onClick={downloadSelectedImages}
              disabled={selectedImages.length === 0}
            >
              Download Selected
            </Button>
          </div>
        )}
        <br />
        <div className="grid">
          {images?.map((img, i) => (
            <div key={i} className="image-card">
              <img
                src={`http://localhost:5000/images/${img.path}`}
                alt="result"
                onClick={() => toggleImageSelection(img.id)}
                className={
                  selectedImages.includes(img.id)
                    ? "selected-image"
                    : ""
                }
              />

              <input
                type="checkbox"
                checked={selectedImages.includes(img.id)}
                onChange={() => toggleImageSelection(img.id)}
              />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}