import { useState } from "react";
import axios from "axios";
import ResultBox from "./ResultBox";
import "../SpamChecker.css";

export default function SpamChecker() {
  const [emailText, setEmailText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(false);

  const checkSpam = async () => {
    if (!emailText.trim()) return;
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/api/check-spam", { text: emailText });
      setResult(response.data.is_spam);
      setShowPopup(true); // Show popup when result is available
    } catch (error) {
      console.error("Error checking spam:", error);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1 className="title">📧 AI-Powered Email Threat Detector</h1>
      <p className="subtitle">Using Machine Learning to Detect Malicious Emails</p>
      
      <div className="card">
        <p className="description">Enter an email text below to check if it's spam.</p>
        <textarea 
          className="email-input"
          rows={6}
          placeholder="Paste email content here..."
          value={emailText}
          onChange={(e) => setEmailText(e.target.value)}
        />
        <button className="check-button" onClick={checkSpam} disabled={loading}>
          {loading ? "Analyzing..." : "Check for Spam"}
        </button>
      </div>

      {/* Pop-up result box */}
      {showPopup && (
        <div className="popup-container" onClick={() => setShowPopup(false)}>
          <div className="popup-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setShowPopup(false)}>✖</button>
            <ResultBox isSpam={result} />
          </div>
        </div>
      )}
    </div>
  );
}
