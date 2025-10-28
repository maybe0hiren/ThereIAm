import React from 'react';
import { supabase } from './../supabaseClient';
import './LoginPage.css';
import googleIcon from './../assets/google.svg'

function LoginPage() {
  async function signInWithGoogle() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
    });
    if (error) alert('Error logging in: ' + error.message);
  }

  return (
    <div className="login-background">
      <div className="login-container">
        <h2>Welcome Back</h2>
        <p>Sign in to continue to your dashboard</p>
        <button className="google-btn" onClick={signInWithGoogle}>
          <img src={googleIcon} alt="Google" className="google-icon" />
          Sign in with Google
        </button>
        <p className="footer-text">© {new Date().getFullYear()} ThereIAm</p>
      </div>
    </div>
  );
}

export default LoginPage;
