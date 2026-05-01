import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, AlertCircle, CheckCircle, Clock, Star, ChevronRight, Brain } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import Navbar from "../components/Navbar";
import "../styles/result.css";

/* ─── mock data ─────────────────────────────────────────────────── */
const MOCK = {
  urgency: "High",
  specialist: "Cardiologist",
  icon: "🫀",
  confidence: "92%",
  reason: "Chest pain combined with breathing difficulty and dizziness suggests a possible cardiac emergency requiring immediate evaluation.",
  symptoms: ["Chest pain", "Breathing difficulty", "Dizziness"],
  severity: "High severity",
  duration: "2 days",
  steps: [
    "Symptoms parsed → chest pain, breathing difficulty, dizziness",
    "High-risk pattern detected in symptom cluster",
    "Condition mapped to Cardiologist specialist type",
    "Fetched available doctors sorted by rating and availability",
    "Best-matched slot selected based on urgency level",
  ],
  doctors: [
    { name: "Dr. Arjun Sharma",  specialization: "Senior Cardiologist",       exp: "14 yrs", rating: "4.6", slots: ["10:00 AM", "1:30 PM", "4 PM"] },
    { name: "Dr. Priya Menon",   specialization: "Interventional Cardiology", exp: "9 yrs",  rating: "4.7", slots: ["11:00 AM", "3:00 PM"] },
    { name: "Dr. Rahul Verma",   specialization: "Cardiac Electrophysiology", exp: "11 yrs", rating: "4.8", slots: ["9:30 AM",  "2:30 PM", "5:00 PM"] },
  ],
};

const URGENCY = {
  High:   { color: "#f87171", bg: "rgba(248,113,113,0.08)", border: "rgba(248,113,113,0.35)", label: "Seek urgent care today" },
  Medium: { color: "#fbbf24", bg: "rgba(251,191,36,0.08)",  border: "rgba(251,191,36,0.35)",  label: "Schedule within 2–3 days" },
  Low:    { color: "#10b981", bg: "rgba(16,185,129,0.08)",  border: "rgba(16,185,129,0.35)",  label: "Book at your convenience" },
};

/* ── Confidence Ring — pure CSS conic-gradient, zero SVG ────────── */
function ConfRing({ pct }) {
  const [displayed, setDisplayed] = useState(0);

  useEffect(() => {
    // small delay so the CSS transition fires after mount
    const t = setTimeout(() => setDisplayed(pct), 120);
    return () => clearTimeout(t);
  }, [pct]);

  const deg = Math.round(displayed * 3.6); // pct → degrees (100% = 360°)

  return (
    <div className="conf-ring-wrap">
      <div
        className="conf-ring"
        style={{
          background: `conic-gradient(
            #00d4b4 0deg ${deg}deg,
            rgba(0,212,180,0.1) ${deg}deg 360deg
          )`,
        }}
      >
        <div className="conf-ring-inner">
          <span className="conf-ring-num">{pct}%</span>
        </div>
      </div>
    </div>
  );
}

export default function Result() {
  const { state }  = useLocation();
  const navigate   = useNavigate();
  const data       = state || MOCK;

  const [selectedDoc,  setSelectedDoc]  = useState(null);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [booked,       setBooked]       = useState(false);
  const [visibleSteps, setVisibleSteps] = useState(0);

  const urg     = URGENCY[data.urgency] || URGENCY.Low;
  // accept "92%" or 92 or "92"
  const confNum = parseInt(String(data.confidence).replace("%", "")) || 90;

  useEffect(() => {
    if (visibleSteps >= data.steps.length) return;
    const t = setTimeout(() => setVisibleSteps(v => v + 1), 420);
    return () => clearTimeout(t);
  }, [visibleSteps, data.steps.length]);

  /* ── booked ── */
  if (booked) return (
    <div className="rp">
      <div className="rp-nav-fixed"><Navbar /></div>
      <div className="booked-screen">
        <div className="booked-icon">✓</div>
        <h2>Appointment Confirmed!</h2>
        <p>Your appointment with <strong>{selectedDoc}</strong> is booked for <strong>{selectedSlot}</strong>.<br />A confirmation will be sent to your registered number.</p>
        <button className="btn-outline" onClick={() => navigate("/")}><ArrowLeft size={15} /> Analyze New Symptoms</button>
      </div>
    </div>
  );

  /* ── no data ── */
  if (!state && process.env.NODE_ENV === "production") return (
    <div className="rp">
      <div className="rp-nav-fixed"><Navbar /></div>
      <div className="no-data">
        <AlertCircle size={48} color="var(--teal)" />
        <h2>No analysis found</h2>
        <p>Please go back and analyze your symptoms first.</p>
        <button className="btn-outline" onClick={() => navigate("/")}><ArrowLeft size={15} /> Back to Home</button>
      </div>
    </div>
  );

  return (
    <div className="rp">
      <div className="rp-nav-fixed"><Navbar /></div>

      {/* ── HEADER ── */}
      <header className="rp-header">
        <p className="rp-kicker">Analysis Complete</p>
        <h1 className="rp-title">Your Health Report</h1>
        <p className="rp-meta">
          {data.symptoms.length} symptom{data.symptoms.length !== 1 ? "s" : ""}&nbsp;·&nbsp;
          {data.severity}&nbsp;·&nbsp;{data.duration}
        </p>
      </header>

      <div className="rp-body">

        {/* ══ ROW 1: URGENCY + CONFIDENCE ══ */}
        <div className="top-row">

          <div className="card urgency-card" style={{ background: urg.bg, borderColor: urg.border }}>
            <div className="card-label">Urgency</div>
            <div className="urgency-badge" style={{ color: urg.color }}>{data.urgency}</div>
            <div className="urgency-advice" style={{ color: urg.color }}>{urg.label}</div>
          </div>

          <div className="card confidence-card">
            <div className="card-label">AI Confidence</div>
            <div className="conf-inner">
              <ConfRing pct={confNum} />
              <p className="conf-label-text">Symptom pattern matched to cardiac indicators</p>
            </div>
          </div>

        </div>

        {/* ══ SPECIALIST ══ */}
        <div className="card specialist-card">
          <div className="card-label">Recommended Specialist</div>
          <div className="specialist-row">
            <span className="spec-icon">{data.icon || "🏥"}</span>
            <div>
              <div className="spec-name">{data.specialist}</div>
              <p className="spec-reason">{data.reason}</p>
            </div>
          </div>
        </div>

        {/* ══ REASONING PIPELINE ══ */}
        <div className="card reasoning-card">
          <div className="section-head">
            <Brain size={16} className="section-icon" />
            <h3>Agent Reasoning Pipeline</h3>
            <span className="steps-count">{data.steps.length} steps</span>
          </div>
          <div className="timeline">
            {data.steps.map((step, i) => (
              <div key={i} className={`timeline-step ${i < visibleSteps ? "visible" : "hidden"}`}>
                {i < data.steps.length - 1 && <div className="tl-line" />}
                <div className={`tl-dot ${i < visibleSteps ? "done" : ""}`}>
                  {i < visibleSteps ? <CheckCircle size={13} /> : <span>{i + 1}</span>}
                </div>
                <div className="tl-content">
                  <span className="tl-step-num">Step {i + 1}</span>
                  <p className="tl-text">{step}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ══ SYMPTOMS ══ */}
        <div className="card sym-card">
          <div className="section-head"><h3>Detected Symptoms</h3></div>
          <div className="sym-tags">
            {data.symptoms.map((s, i) => <span className="sym-tag" key={i}>{s}</span>)}
          </div>
          <div className="pill-row">
            <span className="pill amber">{data.severity}</span>
            <span className="pill teal">{data.duration}</span>
          </div>
          <div className="sym-conf-bar-wrap">
            <div className="sym-conf-bar-fill" style={{ width: `${confNum}%` }} />
          </div>
        </div>

        {/* ══ DOCTORS ══ */}
        <div className="card doctors-card">
          <div className="section-head"><h3>Available {data.specialist}s</h3></div>
          <div className="doctors-grid">
            {data.doctors.map((doc, i) => (
              <div
                key={i}
                className={`doctor-item ${selectedDoc === doc.name ? "selected" : ""} ${i === 0 ? "best" : ""}`}
                onClick={() => setSelectedDoc(doc.name)}
              >
                {i === 0 && <span className="best-badge">Best Match</span>}
                <div className="doc-row">
                  <div className="doc-avatar">{doc.name.split(" ")[1]?.charAt(0) || "D"}</div>
                  <div className="doc-info">
                    <h4>{doc.name}</h4>
                    <p className="doc-spec">{doc.specialization}</p>
                    <p className="doc-exp">{doc.exp} experience</p>
                  </div>
                  <div className="doc-rating"><Star size={11} fill="#fbbf24" color="#fbbf24" />{doc.rating}</div>
                </div>
                <div className="slots-wrap">
                  <p className="slots-label"><Clock size={11} /> Available slots</p>
                  <div className="slots-row">
                    {doc.slots.map((slot, si) => (
                      <button
                        key={si}
                        className={`slot-btn ${selectedSlot === slot && selectedDoc === doc.name ? "active" : ""}`}
                        onClick={e => { e.stopPropagation(); setSelectedDoc(doc.name); setSelectedSlot(slot); }}
                      >{slot}</button>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
          {selectedSlot && selectedDoc && (
            <button className="book-btn" onClick={() => setBooked(true)}>
              Confirm — {selectedDoc} at {selectedSlot} <ChevronRight size={16} />
            </button>
          )}
        </div>

        {/* ══ DISCLAIMER ══ */}
        <div className="disclaimer">
          <span>ℹ️</span>
          <p><strong>Important:</strong> This is an AI-generated triage report, not a medical diagnosis. Always consult a qualified healthcare professional. In emergencies, call 112 or visit the nearest hospital.</p>
        </div>

        {/* ══ ACTIONS ══ */}
        <div className="actions-row">
          <button className="btn-outline" onClick={() => navigate("/")}><ArrowLeft size={15} /> Back to Home</button>
          <button className="btn-print" onClick={() => window.print()}>📄 Print Report</button>
        </div>

      </div>
    </div>
  );
}