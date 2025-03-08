import { motion } from "framer-motion";
import { FaExclamationTriangle, FaCheckCircle } from "react-icons/fa";
import "../ResultBox.css";

export default function ResultBox({ isSpam }) {
  return (
    <motion.div
      className={`result-box ${isSpam ? "spam" : "not-spam"}`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {isSpam ? (
        <>
          <FaExclamationTriangle className="icon danger" />
          <h2 className="alert-text">⚠️ Suspicious Email Detected!</h2>
          <p className="message">This email **may be a spam or phishing attempt.** Be cautious before clicking any links or providing personal details.</p>
        </>
      ) : (
        <>
          <FaCheckCircle className="icon safe" />
          <h2 className="alert-text">✅ Looks Safe!</h2>
          <p className="message">This email **does not appear to be spam.** However, always verify sender details before taking action.</p>
        </>
      )}
    </motion.div>
  );
}
