import { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../api";

export default function VerifyEmailPage() {
  const { token } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const verify = async () => {
      try {
        await API.get(`/verifyEmail/${token}`);
        alert("Email verified successfully!");
        navigate("/");
      } catch {
        alert("Verification failed");
        navigate("/");
      }
    };

    verify();
  }, []);

  return <div>Verifying email...</div>;
}