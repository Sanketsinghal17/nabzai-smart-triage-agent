import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Zap, TrendingUp, Award, Users, Activity, Heart, Shield, Clock, ChevronRight } from "lucide-react";
import Navbar from "../components/Navbar";
import CTABannerUpgraded from "../components/CTABannerUpgraded"; // ← IMPORT UPGRADED CTA
import "../styles/home.css";

/* ── Particle canvas ── */
function ParticleCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let animId;
    const W = () => (canvas.width = window.innerWidth);
    const H = () => (canvas.height = window.innerHeight);
    W(); H();

    const COLS = { teal: "0,212,180", blue: "14,165,233", pink: "244,114,182" };
    const colorKeys = Object.values(COLS);

    const dots = Array.from({ length: 70 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.8 + 0.4,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      color: colorKeys[Math.floor(Math.random() * colorKeys.length)],
      alpha: Math.random() * 0.5 + 0.15,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      dots.forEach((d) => {
        d.x += d.vx;
        d.y += d.vy;
        if (d.x < 0) d.x = canvas.width;
        if (d.x > canvas.width) d.x = 0;
        if (d.y < 0) d.y = canvas.height;
        if (d.y > canvas.height) d.y = 0;

        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${d.color},${d.alpha})`;
        ctx.fill();
      });

      // draw lines between close dots
      for (let i = 0; i < dots.length; i++) {
        for (let j = i + 1; j < dots.length; j++) {
          const dx = dots[i].x - dots[j].x;
          const dy = dots[i].y - dots[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(dots[i].x, dots[i].y);
            ctx.lineTo(dots[j].x, dots[j].y);
            ctx.strokeStyle = `rgba(0,212,180,${0.07 * (1 - dist / 120)})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }
      animId = requestAnimationFrame(draw);
    };

    draw();
    const onResize = () => { W(); H(); };
    window.addEventListener("resize", onResize);
    return () => { cancelAnimationFrame(animId); window.removeEventListener("resize", onResize); };
  }, []);

  return <canvas ref={canvasRef} className="particle-canvas" />;
}

/* ── Typewriter ── */
function Typewriter({ words }) {
  const [idx, setIdx] = useState(0);
  const [charIdx, setCharIdx] = useState(0);
  const [deleting, setDeleting] = useState(false);
  const [display, setDisplay] = useState("");

  useEffect(() => {
    const current = words[idx];
    const timeout = deleting
      ? setTimeout(() => {
          setDisplay(current.slice(0, charIdx - 1));
          setCharIdx((c) => c - 1);
          if (charIdx - 1 === 0) { setDeleting(false); setIdx((i) => (i + 1) % words.length); }
        }, 60)
      : setTimeout(() => {
          setDisplay(current.slice(0, charIdx + 1));
          setCharIdx((c) => c + 1);
          if (charIdx + 1 === current.length) setTimeout(() => setDeleting(true), 1800);
        }, 90);
    return () => clearTimeout(timeout);
  }, [charIdx, deleting, idx, words]);

  return (
    <span className="typewriter-text">
      {display}<span className="typewriter-cursor">|</span>
    </span>
  );
}

/* ── Stat counter ── */
function StatCounter({ target, suffix = "" }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        const duration = 1800;
        const steps = 60;
        const inc = target / steps;
        let cur = 0;
        const timer = setInterval(() => {
          cur += inc;
          if (cur >= target) { setCount(target); clearInterval(timer); }
          else setCount(Math.floor(cur));
        }, duration / steps);
      }
    }, { threshold: 0.5 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [target]);

  return <span ref={ref}>{count.toLocaleString()}{suffix}</span>;
}

export default function Home() {
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [customSymptom, setCustomSymptom] = useState("");
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [severity, setSeverity] = useState("Moderate");
  const [duration, setDuration] = useState("1-3 days");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const predefinedSymptoms = [
    { id: 1, name: "Headache", emoji: "🧠" },
    { id: 2, name: "Chest Pain", emoji: "❤️" },
    { id: 3, name: "Fever", emoji: "🌡️" },
    { id: 4, name: "Cough", emoji: "💨" },
    { id: 5, name: "Fatigue", emoji: "😴" },
    { id: 6, name: "Dizziness", emoji: "🌀" },
    { id: 7, name: "Shortness of Breath", emoji: "🫁" },
    { id: 8, name: "Nausea", emoji: "🤢" },
    { id: 9, name: "Back Pain", emoji: "📍" },
    { id: 10, name: "Sore Throat", emoji: "😣" },
    { id: 11, name: "Chill", emoji: "❄️" },
    { id: 12, name: "Vomiting", emoji: "🤮" },
  ];

  const toggleSymptom = (name) => {
    setSelectedSymptoms((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    );
  };

  const addCustomSymptom = () => {
    if (customSymptom.trim()) {
      setSelectedSymptoms((prev) => [...prev, customSymptom.trim()]);
      setCustomSymptom("");
      setShowCustomInput(false);
    }
  };

  const removeSymptom = (s) => setSelectedSymptoms((prev) => prev.filter((x) => x !== s));

  /* rule-based triage */
  const triage = (symptoms, sev) => {
    const s = symptoms;
    const high = sev === "Severe";
    if (s.includes("Chest Pain") || s.includes("Shortness of Breath"))
      return { urgency: "High", specialist: "Cardiologist", icon: "🫀", reason: "Chest pain or breathing difficulty indicates a possible cardiac event requiring urgent evaluation." };
    if (s.includes("Dizziness") && high)
      return { urgency: "High", specialist: "Neurologist", icon: "🧠", reason: "Severe dizziness warrants neurological assessment to rule out serious conditions." };
    if (s.includes("Headache") && high)
      return { urgency: "Medium", specialist: "Neurologist", icon: "🧠", reason: "Severe headache warrants neurological evaluation." };
    if (s.includes("Back Pain"))
      return { urgency: "Medium", specialist: "Orthopedist", icon: "🦴", reason: "Back pain may indicate musculoskeletal or spinal conditions." };
    if (s.includes("Fever") && (s.includes("Cough") || s.includes("Chill")))
      return { urgency: "Medium", specialist: "General Physician", icon: "🏥", reason: "Combination of fever and respiratory symptoms needs prompt medical review." };
    return { urgency: high ? "Medium" : "Low", specialist: "General Physician", icon: "🏥", reason: "Symptoms suggest a general medical consultation is recommended." };
  };

  const handleAnalyze = () => {
    if (!selectedSymptoms.length) { alert("Please select at least one symptom."); return; }
    setLoading(true);

    const result = triage(selectedSymptoms, severity);
    const doctorDB = {
      Cardiologist: [
        { name: "Dr. Rajesh Sharma", specialization: "Cardiologist", rating: 4.9, exp: "14 yrs", slots: ["9:00 AM", "11:30 AM", "3:00 PM"] },
        { name: "Dr. Priya Mehta", specialization: "Cardiologist", rating: 4.7, exp: "10 yrs", slots: ["10:00 AM", "2:00 PM"] },
      ],
      Neurologist: [
        { name: "Dr. Sunita Rao", specialization: "Neurologist", rating: 4.8, exp: "12 yrs", slots: ["9:00 AM", "2:30 PM"] },
        { name: "Dr. Arjun Mehta", specialization: "Neurologist", rating: 4.6, exp: "8 yrs", slots: ["11:00 AM", "4:00 PM"] },
      ],
      Orthopedist: [
        { name: "Dr. Ajay Verma", specialization: "Orthopedist", rating: 4.7, exp: "11 yrs", slots: ["10:30 AM", "1:00 PM", "4:00 PM"] },
      ],
      "General Physician": [
        { name: "Dr. Ritu Gupta", specialization: "General Physician", rating: 4.8, exp: "9 yrs", slots: ["8:30 AM", "12:00 PM", "4:00 PM"] },
        { name: "Dr. Sameer Khan", specialization: "General Physician", rating: 4.6, exp: "7 yrs", slots: ["9:30 AM", "1:30 PM"] },
      ],
    };

    const data = {
      symptoms: selectedSymptoms,
      severity,
      duration,
      urgency: result.urgency,
      specialist: result.specialist,
      icon: result.icon,
      reason: result.reason,
      steps: [
        `Parsed ${selectedSymptoms.length} symptom(s): ${selectedSymptoms.join(", ")}`,
        `Severity classified as "${severity}" · Duration: ${duration}`,
        `Urgency level set to "${result.urgency}" via decision engine`,
        `Specialist mapped → ${result.specialist}`,
        `Found ${(doctorDB[result.specialist] || []).length} available doctors with open slots`,
      ],
      doctors: doctorDB[result.specialist] || doctorDB["General Physician"],
    };

    setTimeout(() => { setLoading(false); navigate("/result", { state: data }); }, 1600);
  };

  const features = [
    { Icon: Zap, title: "AI-Powered Triage", desc: "Rule-based decision engine classifies urgency in milliseconds — no guesswork." },
    { Icon: TrendingUp, title: "Real-time Matching", desc: "Instantly match with available specialists based on your symptom profile." },
    { Icon: Award, title: "Top Specialists", desc: "Access verified, highly-rated doctors across all major medical disciplines." },
    { Icon: Shield, title: "Private & Secure", desc: "Your health data stays on-device. We never share your information." },
    { Icon: Clock, title: "Instant Availability", desc: "See real-time open slots and book in one tap without waiting on hold." },
    { Icon: Heart, title: "Holistic Care", desc: "From diagnosis to follow-up, we keep your entire health journey connected." },
  ];

  const howItWorks = [
    { step: "01", title: "Describe Symptoms", desc: "Select from common symptoms or type your own. Add severity and duration." },
    { step: "02", title: "AI Analyzes", desc: "Our triage engine classifies urgency and maps to the right specialist." },
    { step: "03", title: "See Reasoning", desc: "Watch each step of the agent's decision-making process in real time." },
    { step: "04", title: "Book Instantly", desc: "Choose a doctor and time slot. Your appointment is confirmed immediately." },
  ];

  // Zigzag scroll observer
  useEffect(() => {
    const items = document.querySelectorAll("[data-howitem]");
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("how-zitem-visible"); });
      },
      { threshold: 0.22 }
    );
    items.forEach((el) => obs.observe(el));
    return () => obs.disconnect();
  }, []);

  const stats = [
    { value: 50000, suffix: "+", label: "Patients Served" },
    { value: 98, suffix: "%", label: "Accuracy Rate" },
    { value: 200, suffix: "+", label: "Verified Doctors" },
    { value: 30, suffix: "s", label: "Avg Triage Time" },
  ];

  return (
    <div className="home-page">
      <ParticleCanvas />
      <Navbar />

      {/* ── HERO ── */}
      <section className="hero-section">
        <div className="hero-glow hero-glow-left" />
        <div className="hero-glow hero-glow-right" />

        <div className="hero-left">
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            AI-Powered Smart Triage · Trusted by 50,000+ Patients
          </div>

          <h1 className="hero-heading">
            Smart Healthcare<br />
            Starts with the<br />
            <span className="hero-highlight">Right Diagnosis</span>
          </h1>

          <p className="hero-desc">
            Describe your symptoms and let NabzAI's intelligent triage engine assess urgency, identify the right specialist, and book your appointment — all in under 60 seconds.
          </p>

          <div className="hero-trust-row">
            <div className="trust-pill"><span className="trust-dot green" />HIPAA Compliant</div>
            <div className="trust-pill"><span className="trust-dot blue" />200+ Verified Doctors</div>
            <div className="trust-pill"><span className="trust-dot teal" />Instant Booking</div>
          </div>

          <div className="hero-cta-row">
            <button className="hero-cta-primary" onClick={() => document.getElementById("symptom-section").scrollIntoView({ behavior: "smooth" })}>
              Check My Symptoms <ChevronRight size={18} />
            </button>
            <button className="hero-cta-secondary" onClick={() => document.getElementById("how-it-works").scrollIntoView({ behavior: "smooth" })}>
              See How It Works
            </button>
          </div>
        </div>

        <div className="hero-right">
          {/* medical card mockup */}
          <div className="hero-card-mockup">
            <div className="mockup-header">
              <div className="mockup-avatar">🩺</div>
              <div>
                <p className="mockup-title">NabzAI Analysis</p>
                <p className="mockup-sub">Real-time triage result</p>
              </div>
              <div className="mockup-live"><span className="live-dot" />Live</div>
            </div>

            <div className="mockup-urgency high">
              <span className="murg-label">URGENCY</span>
              <span className="murg-val">High Priority</span>
            </div>

            <div className="mockup-specialist-row">
              <div className="mspec-icon">🫀</div>
              <div>
                <p className="mspec-name">Cardiologist</p>
                <p className="mspec-sub">Recommended specialist</p>
              </div>
            </div>

            <div className="mockup-steps">
              {["Symptoms parsed", "Urgency classified", "Specialist mapped", "Doctor matched"].map((s, i) => (
                <div className="mockup-step" key={i} style={{ animationDelay: `${0.4 + i * 0.25}s` }}>
                  <span className="mstep-check">✓</span>
                  <span>{s}</span>
                </div>
              ))}
            </div>

            <div className="mockup-doctor">
              <div className="mdoc-avatar">RS</div>
              <div>
                <p className="mdoc-name">Dr. Rajesh Sharma</p>
                <p className="mdoc-slot">Available · 9:00 AM today</p>
              </div>
              <button className="mdoc-btn">Book</button>
            </div>
          </div>

          {/* side badges */}
          <div className="hero-side-badge badge-top">
            <span className="badge-num">98%</span>
            <span className="badge-label">Triage Accuracy</span>
          </div>
          <div className="hero-side-badge badge-bot">
            <span className="badge-num">&lt;30s</span>
            <span className="badge-label">Avg. Analysis Time</span>
          </div>
        </div>

        <div className="hero-scroll-hint">
          <div className="scroll-dot" />
          Scroll to begin
        </div>
      </section>

      {/* ── STATS BAR ── */}
      <section className="stats-bar">
        {stats.map((s) => (
          <div className="stat-item" key={s.label}>
            <div className="stat-value">
              <StatCounter target={s.value} suffix={s.suffix} />
            </div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </section>

      {/* ── MAIN FORM ── */}
      <div className="home-container" id="symptom-section">

        {/* Symptoms */}
        <div className="symptoms-section">
          <h3>Select your symptoms</h3>
          <div className="symptoms-grid">
            {predefinedSymptoms.map((sym) => (
              <button
                key={sym.id}
                className={`symptom-card ${selectedSymptoms.includes(sym.name) ? "selected" : ""}`}
                onClick={() => toggleSymptom(sym.name)}
              >
                <div className="symptom-emoji">{sym.emoji}</div>
                <div className="symptom-name">{sym.name}</div>
              </button>
            ))}
            <button className="symptom-card add-symptom-btn" onClick={() => setShowCustomInput(!showCustomInput)}>
              <Plus size={26} />
              <div className="symptom-name">Add Other</div>
            </button>
          </div>

          {showCustomInput && (
            <div className="custom-symptom-input">
              <input
                type="text"
                placeholder="Describe your symptom..."
                value={customSymptom}
                onChange={(e) => setCustomSymptom(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addCustomSymptom()}
                autoFocus
              />
              <button onClick={addCustomSymptom} className="add-btn">Add</button>
            </div>
          )}

          {selectedSymptoms.length > 0 && (
            <div className="selected-symptoms">
              <h4>Selected ({selectedSymptoms.length})</h4>
              <div className="symptoms-list">
                {selectedSymptoms.map((s, i) => (
                  <div key={i} className="symptom-tag">
                    {s}
                    <button className="remove-symptom" onClick={() => removeSymptom(s)}>×</button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Assessment */}
        <div className="assessment-section">
          <div className="assessment-group">
            <label>Duration of symptoms</label>
            <div className="options-row">
              {["Less than 24h", "1-3 days", "3-7 days", "More than a week"].map((opt) => (
                <button key={opt} className={`option-btn ${duration === opt ? "active" : ""}`} onClick={() => setDuration(opt)}>{opt}</button>
              ))}
            </div>
          </div>
          <div className="assessment-group">
            <label>Symptom severity</label>
            <div className="options-row">
              {["Mild", "Moderate", "Severe"].map((opt) => (
                <button key={opt} className={`option-btn severity-btn ${opt.toLowerCase()} ${severity === opt ? "active" : ""}`} onClick={() => setSeverity(opt)}>{opt}</button>
              ))}
            </div>
          </div>
        </div>

        {/* Analyze */}
        <button className={`analyze-btn ${loading ? "loading" : ""}`} onClick={handleAnalyze} disabled={loading || !selectedSymptoms.length}>
          {loading ? (
            <><span className="spinner" /> Analyzing your symptoms...</>
          ) : (
            <><Zap size={20} /> Analyze My Symptoms</>
          )}
        </button>

        <p className="disclaimer">⚠️ AI-powered triage only — not a medical diagnosis. Always consult a qualified healthcare professional.</p>
      </div>

      {/* ── HOW IT WORKS ── */}
      <section className="how-section" id="how-it-works">
        <div className="how-section-header">
          <div className="section-label">Process</div>
          <h2 className="section-title">How NabzAI Works</h2>
          <p className="section-sub">Four intelligent steps. One seamless experience.</p>
        </div>

        <div className="how-zigzag">
          {howItWorks.map((h, i) => (
            <div className={`how-zitem how-zitem-${i % 2 === 0 ? "left" : "right"}`} key={i} data-howitem>
              <div className="how-zitem-inner">
                <div className="how-znum">{h.step}</div>
                <div className="how-zcontent">
                  <h4>{h.title}</h4>
                  <p>{h.desc}</p>
                </div>
              </div>
              {i < howItWorks.length - 1 && (
                <div className="how-zconnector">
                  <div className="how-zline" />
                  <div className="how-zarrow">↓</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section className="features-section">
        <div className="features-container">
          <div className="section-label">Capabilities</div>
          <h2 className="section-title">Why Choose NabzAI?</h2>
          <p className="section-sub">Built for speed, trust, and clarity — not complexity.</p>

          <div className="features-grid">
            {features.map(({ Icon, title, desc }) => (
              <div className="feature-card" key={title}>
                <div className="feature-icon"><Icon size={24} /></div>
                <h4>{title}</h4>
                <p>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── TESTIMONIAL STRIP ── */}
      <section className="testimonial-strip">
        <div className="testimonial-track">
          {[
            { text: "Diagnosed my chest pain correctly — saw a cardiologist the same day.", name: "Rahul M., Delhi" },
            { text: "The step-by-step reasoning made me actually trust the recommendation.", name: "Sneha P., Mumbai" },
            { text: "Booked an appointment in 30 seconds. Absolutely seamless.", name: "Aditya K., Bangalore" },
            { text: "Finally an app that explains WHY it recommends a specialist.", name: "Priya S., Chennai" },
            { text: "The AI was right — turned out to be a neurological issue.", name: "Vikram R., Hyderabad" },
            { text: "Diagnosed my chest pain correctly — saw a cardiologist the same day.", name: "Rahul M., Delhi" },
            { text: "The step-by-step reasoning made me actually trust the recommendation.", name: "Sneha P., Mumbai" },
          ].map((t, i) => (
            <div className="testimonial-card" key={i}>
              <p className="t-text">"{t.text}"</p>
              <p className="t-name">— {t.name}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── UPGRADED CTA BANNER ── */}
      <CTABannerUpgraded />

      {/* ── FOOTER ── */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <div className="footer-logo">
              <span className="footer-logo-icon">💊</span>
              <span>Nabz<span style={{ color: "var(--teal)" }}>AI</span></span>
            </div>
            <p>Smart Appointment Triage Agent. Built for speed, trust, and clarity.</p>
            <div className="footer-socials">
              <a href="#" className="social-pill">Twitter</a>
              <a href="#" className="social-pill">GitHub</a>
              <a href="#" className="social-pill">LinkedIn</a>
            </div>
          </div>

          <div className="footer-links">
            <div className="footer-col">
              <h5>Product</h5>
              <a href="#">How it works</a>
              <a href="#">Specialists</a>
              <a href="#">Pricing</a>
              <a href="#">For Hospitals</a>
            </div>
            <div className="footer-col">
              <h5>Company</h5>
              <a href="#">About</a>
              <a href="#">Team</a>
              <a href="#">Blog</a>
              <a href="#">Contact</a>
            </div>
            <div className="footer-col">
              <h5>Legal</h5>
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Use</a>
              <a href="#">Disclaimer</a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p>© 2025 NabzAI. All rights reserved. · Not a substitute for professional medical advice.</p>
          <div className="footer-pulse">
            <span className="pulse-dot" />
            All systems operational
          </div>
        </div>
      </footer>
    </div>
  );
}
