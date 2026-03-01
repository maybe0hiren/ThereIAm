import React, { useState } from "react";

function HomePage() {
  const [files, setFiles] = useState(null);
  const [status, setStatus] = useState("");

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      setStatus("No files selected");
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("photos", files[i]);
    }

    try {
      const res = await fetch("http://localhost:5000/admin/uploadPhotos", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setStatus(`Uploaded ${data.uploaded || data.count} images`);
    } catch (err) {
      setStatus("Upload failed");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Photos</h2>

      <input
        type="file"
        multiple
        accept="image/*"
        onChange={(e) => setFiles(e.target.files)}
      />

      <br /><br />

      <button onClick={handleUpload}>
        Upload
      </button>

      <p>{status}</p>
    </div>
  );
}

export default HomePage;