import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import { supabase } from "../supabaseClient";
import "./FaceCapPage.css";
import { useNavigate } from "react-router-dom";

function FaceCapPage() {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [videoBlob, setVideoBlob] = useState(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const startRecording = () => {
    const stream = webcamRef.current.stream;
    const mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm" });
    let chunks = [];

    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: "video/webm" });
      setVideoBlob(blob);
    };

    mediaRecorder.start();
    setRecording(true);
    mediaRecorderRef.current = mediaRecorder;

    setTimeout(() => stopRecording(), 7000);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const uploadVideo = async () => {
    setUploading(true);
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user) {
      alert("Please log in first");
      setUploading(false);
      return;
    }

    const fileName = `${user.id}/faceCapture.webm`;
    const { error } = await supabase.storage
      .from("user_faces")
      .upload(fileName, videoBlob, { upsert: true });

    setUploading(false);

    if (error) alert("Upload failed: " + error.message);
    else {
        navigate("/dashboard");
    }
  };

  return (
    <div className="face-container">
      <div className="face-card">
        <h2>Face Registration</h2>
        <p>We’ll record a 7 second video to analyze your face</p>
        <p> Slowly turn your head in every way you can</p>

        <Webcam
          ref={webcamRef}
          audio={false}
          className="webcam-view"
          videoConstraints={{ facingMode: "user" }}
        />

        {!recording && !uploading && (
          <button className="capture-btn" onClick={startRecording}>
            🎥 Start Recording (5s)
          </button>
        )}
        {recording && <p className="recording-text">Recording...</p>}

        {uploading && (
          <div className="uploading-loader">
            <div className="spinner"></div>
            <p>Uploading your video...</p>
          </div>
        )}

        {videoBlob && !uploading && !recording && (
          <button className="upload-btn" onClick={uploadVideo}>
            Upload Video
          </button>
        )}
      </div>
    </div>
  );
}

export default FaceCapPage;
