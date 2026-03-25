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

      setMembers(res.data.members || []);
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

      setImages(res.data.images || []);
    } catch (err) {
      alert(err.response?.data?.error || "Search failed");
    }

    setLoading(false);
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
          {members.map((member) => (
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
        <div className="grid">
          {images.map((img, i) => (
            <div key={i} className="image-card">
              <img
                src={`http://localhost:5000/images/${img.path}`}
                alt="result"
              />

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