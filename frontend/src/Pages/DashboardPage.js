import React, { useState, useEffect } from "react";

function DashboardPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [markedImage, setMarkedImage] = useState(null);
  const [status, setStatus] = useState("Checking backend...");
  const [backendAvailable, setBackendAvailable] = useState(false);

  const BACKEND_URL = "http://127.0.0.1:5000";

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/`);
        if (res.ok) {
          setStatus("✅ Backend is online");
          setBackendAvailable(true);
        } else {
          setStatus("⚠️ Backend not responding...");
        }
      } catch (err) {
        setStatus("❌ Cannot reach backend. Retrying...");
        setBackendAvailable(false);
        setTimeout(checkBackend, 5000);
      }
    };
    checkBackend();
  }, []);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setMarkedImage(null);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select an image first.");
      return;
    }
    if (!backendAvailable) {
      alert("Backend not available. Please wait...");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      setStatus("⏳ Uploading and detecting faces...");
      const response = await fetch(`${BACKEND_URL}/detect`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Detection failed");

      const data = await response.json();
      setMarkedImage(`data:image/jpeg;base64,${data.marked_image}`);
      setStatus("✅ Detection complete!");
    } catch (error) {
      setStatus("❌ Error connecting to backend or detecting faces");
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Face Detection Dashboard</h1>
      <p>{status}</p>

      <div style={{ margin: "2rem 0" }}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={!backendAvailable}
        />
        <button
          onClick={handleUpload}
          style={{
            marginLeft: "1rem",
            padding: "0.5rem 1rem",
            fontSize: "1rem",
            cursor: "pointer",
          }}
          disabled={!backendAvailable}
        >
          Upload & Detect
        </button>
      </div>

      <div style={{ display: "flex", justifyContent: "center", gap: "2rem", flexWrap: "wrap" }}>
        {preview && (
          <div>
            <h3>Original Image:</h3>
            <img
              src={preview}
              alt="Original preview"
              style={{
                width: "300px",
                borderRadius: "10px",
                boxShadow: "0 0 10px rgba(0,0,0,0.2)",
              }}
            />
          </div>
        )}

        {markedImage && (
          <div>
            <h3>Detected Faces:</h3>
            <img
              src={markedImage}
              alt="Detected faces"
              style={{
                width: "300px",
                borderRadius: "10px",
                boxShadow: "0 0 10px rgba(0,0,0,0.2)",
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;
