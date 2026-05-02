import { Heart } from "lucide-react";
import "../styles/navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <div className="navbar-icon-wrapper">
            <Heart className="navbar-icon" size={22} fill="currentColor" />
          </div>
          <div className="navbar-title">
            <h1>NabzAI</h1>
            <p>Smart Health Diagnosis</p>
          </div>
        </div>

        <div className="navbar-pulse">
          <div className="pulse-dot" />
          <span className="pulse-text">AI Active</span>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;