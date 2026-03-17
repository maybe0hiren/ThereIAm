import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";

export default function Register() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [form, setForm] = useState({});
  const [images, setImages] = useState([]);
  const [capturing, setCapturing] = useState(false);
  const [step, setStep] = useState(0);
  const [countdown, setCountdown] = useState(null);

  const steps = [
    "Look straight",
    "Turn slightly left",
    "Turn slightly right"
  ];

  const isFormValid = form.name && form.email && form.password;
  
  useEffect(() => {
    if (capturing) {
      const initCamera = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } catch (err) {
          console.error(err);
          alert(err.name);
        }
      };

      initCamera();
    }
  }, [capturing]);

  const startCamera = () => {
    setCapturing(true);
  };

  const captureImage = () => {
    let count = 3;
    setCountdown(count);

    const interval = setInterval(() => {
      count--;
      setCountdown(count >= 0 ? count : null);

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
    if (!form.name || !form.email || !form.password) {
      alert("Fill all fields");
      return;
    }

    if (images.length < 3) {
      alert("Capture all required images");
      return;
    }

    const data = new FormData();
    data.append("name", form.name);
    data.append("email", form.email);
    data.append("password", form.password);

    images.forEach((img) => data.append("photos", img));

    try {
      await API.post("/register", data);
      alert("Registered successfully");
      navigate("/");
    } catch (err) {
      console.log(err.response?.data);
      alert(err.response?.data?.error || "Error");
    }
  };

  return (
    <div className="card">
      <h2>Register</h2>

      {!capturing && (
        <>
          <input
            placeholder="Name"
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />

          <input
            placeholder="Email"
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />

          <input
            type="password"
            placeholder="Password"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />

            <button 
                onClick={startCamera} 
                disabled={!isFormValid}
                style={{
                    opacity: isFormValid ? 1 : 0.5,
                    cursor: isFormValid ? "pointer" : "not-allowed"
                }}
            >Start Face Capture</button>

          <button className="secondary-btn" onClick={() => navigate("/")}>
            Existing User?
          </button>
        </>
      )}

      {capturing && (
        <>
          <p className="step-text">
            {steps[step] || "Done capturing!"}
          </p>

          <div className="camera-container">
            <video ref={videoRef} autoPlay playsInline />
            {countdown !== null && (
              <div className="countdown">{countdown}</div>
            )}
          </div>

          <canvas ref={canvasRef} style={{ display: "none" }} />

          <div className="preview-container">
            {images.map((img, i) => (
              <img key={i} src={URL.createObjectURL(img)} alt="preview" />
            ))}
          </div>

          {step < 3 ? (
            <button onClick={captureImage}>Capture</button>
          ) : (
            <button onClick={handleRegister}>Finish Registration</button>
          )}
        </>
      )}
    </div>
  );
}