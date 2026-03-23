import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import Card from "../components/Card";
import Button from "../components/Button";
import "./RegisterPage.css";

export default function Register() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [form, setForm] = useState({ role: "member" });
  const [images, setImages] = useState([]);
  const [capturing, setCapturing] = useState(false);
  const [step, setStep] = useState(0);
  const [countdown, setCountdown] = useState(null);
  const [stream, setStream] = useState(null);

  const steps = ["Look straight", "Turn slightly left", "Turn slightly right"];
  const isFormValid = form.name && form.email && form.password;

  useEffect(() => {
    if (capturing) {
      const initCamera = async () => {
        try {
          const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });

          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream;
          }

          setStream(mediaStream);
        } catch (err) {
          alert(err.name);
        }
      };

      initCamera();
    }

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [capturing]);

  const captureImage = () => {
    let count = 3;
    setCountdown(count);

    const interval = setInterval(() => {
      count--;

      if (count >= 1) setCountdown(count);
      else setCountdown(null);

      if (count < 0) {
        clearInterval(interval);

        const canvas = canvasRef.current;
        const video = videoRef.current;

        if (!video) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0);

        canvas.toBlob((blob) => {
          setImages((prev) => [...prev, blob]);
          setStep((prev) => prev + 1);
        }, "image/jpeg");
      }
    }, 1000);
  };

  const handleRegister = async () => {
    if (images.length < 3) {
      alert("Capture all images");
      return;
    }

    const data = new FormData();
    data.append("name", form.name);
    data.append("email", form.email);
    data.append("password", form.password);
    data.append("role", form.role);

    images.forEach((img) => data.append("photos", img));

    try {
      await API.post("/register", data);
      alert("Registered");

      if (stream) stream.getTracks().forEach(track => track.stop());

      navigate("/");
    } catch (err) {
      alert(err.response?.data?.error || "Error");
    }
  };

  return (
    <Card>
      <h2>Register</h2>

      {!capturing && (
        <>
          <input placeholder="Name" onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input placeholder="Email" onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input type="password" placeholder="Password" onChange={(e) => setForm({ ...form, password: e.target.value })} />

          <select onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>

          <Button disabled={!isFormValid} onClick={() => setCapturing(true)}>
            Start Face Capture
          </Button>

          <Button onClick={() => navigate("/")}>Existing User?</Button>
        </>
      )}

      {capturing && (
        <>
          <p className="step-text">{steps[step]}</p>

          <div className="camera-container">
            <video ref={videoRef} autoPlay playsInline />
            {countdown !== null && <div className="countdown">{countdown}</div>}
          </div>

          <canvas ref={canvasRef} style={{ display: "none" }} />

          <div className="preview-container">
            {images.map((img, i) => (
              <img key={i} src={URL.createObjectURL(img)} alt="preview" />
            ))}
          </div>

          {step < 3 ? (
            <Button onClick={captureImage}>Capture</Button>
          ) : (
            <Button onClick={handleRegister}>Finish Registration</Button>
          )}
        </>
      )}
    </Card>
  );
}