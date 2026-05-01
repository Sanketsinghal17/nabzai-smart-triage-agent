export default function CTASection() {
  const handleAnalyze = () => {
    document.getElementById("symptom-section")?.scrollIntoView({ behavior: "smooth" });
  };
  const howitworks = () => {
    document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <>
      <section className="cta-section">
        <div className="cta-top-line" />

        <p className="cta-eyebrow">Free · Instant · Private</p>

        <h2 className="cta-headline">
          Ready to find out<br />
          what's <span>really</span> going on?
        </h2>

        <p className="cta-sub">
          Describe your symptoms. Get a specialist recommendation in under 30 seconds.
        </p>

        <div className="cta-btns">
          <button className="cta-btn-primary" onClick={handleAnalyze}>
            Analyze Symptoms →
          </button>
          <button className="cta-btn-ghost" onClick={howitworks}>
            How it works
          </button>
        </div>

        <div className="cta-meta">
          <span>50K+ patients</span>
          <span className="cta-dot" />
          <span>98% accuracy</span>
          <span className="cta-dot" />
          <span>HIPAA safe</span>
        </div>
      </section>

      <style>{`
        .cta-section {
          font-family: 'DM Sans', sans-serif;
          background: #020d18;
          padding: 90px 60px;
          text-align: center;
          position: relative;
          overflow: hidden;
        }

        .cta-top-line {
          position: absolute;
          top: 0;
          left: 15%;
          right: 15%;
          height: 1px;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(0, 212, 180, 0.25),
            transparent
          );
        }

        .cta-eyebrow {
          font-size: 0.7rem;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: rgba(0, 212, 180, 0.5);
          margin-bottom: 24px;
        }

        .cta-headline {
          font-family: 'Syne', sans-serif;
          font-size: clamp(2rem, 4vw, 3rem);
          font-weight: 800;
          color: #ddf0ec;
          letter-spacing: -0.03em;
          line-height: 1.1;
          margin-bottom: 16px;
        }

        .cta-headline span {
          color: #00d4b4;
        }

        .cta-sub {
          font-size: 0.88rem;
          color: rgba(150, 190, 185, 0.5);
          font-weight: 300;
          margin-bottom: 40px;
          line-height: 1.7;
        }

        .cta-btns {
          display: flex;
          gap: 12px;
          justify-content: center;
          align-items: center;
          flex-wrap: wrap;
        }

        .cta-btn-primary {
          background: #00d4b4;
          color: #011a14;
          border: none;
          border-radius: 10px;
          padding: 14px 28px;
          font-family: 'Syne', sans-serif;
          font-weight: 700;
          font-size: 0.88rem;
          cursor: pointer;
          transition: all 0.2s ease;
          letter-spacing: 0.01em;
        }

        .cta-btn-primary:hover {
          background: #00ffe6;
          transform: translateY(-1px);
          box-shadow: 0 12px 32px rgba(0, 212, 180, 0.25);
        }

        .cta-btn-ghost {
          background: transparent;
          border: 1px solid rgba(0, 212, 180, 0.18);
          color: rgba(0, 212, 180, 0.5);
          border-radius: 10px;
          padding: 13px 24px;
          font-family: 'DM Sans', sans-serif;
          font-size: 0.83rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .cta-btn-ghost:hover {
          border-color: rgba(0, 212, 180, 0.4);
          color: rgba(0, 212, 180, 0.85);
        }

        .cta-meta {
          margin-top: 36px;
          font-size: 0.7rem;
          color: rgba(150, 190, 185, 0.3);
          letter-spacing: 0.06em;
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 16px;
          flex-wrap: wrap;
        }

        .cta-dot {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: rgba(0, 212, 180, 0.35);
          display: inline-block;
        }

        @media (max-width: 600px) {
          .cta-section {
            padding: 70px 24px;
          }

          .cta-btns {
            flex-direction: column;
          }

          .cta-btn-primary,
          .cta-btn-ghost {
            width: 100%;
          }
        }
      `}</style>
    </>
  );
}