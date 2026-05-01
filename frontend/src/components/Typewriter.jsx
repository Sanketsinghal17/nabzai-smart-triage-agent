import { useState, useEffect } from "react";
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
export default Typewriter;