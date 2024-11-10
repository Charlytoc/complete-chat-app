import React, { useState, useRef } from "react";
import "./Headline.css";

export const Headline = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const headlineRef = useRef<HTMLDivElement | null>(null);

  const handleMouseMove = (event) => {
    if (headlineRef.current) {
      const rect = headlineRef.current.getBoundingClientRect();
      setMousePosition({
        x: event.clientX - rect.left + 5, 
        y: event.clientY - rect.top + 5, 
      });
    }
  };

  return (
    <div
      className="headline"
      ref={headlineRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <h1 className="fancy-text">Your AI internal linking companion</h1>
      {isHovering && (
        <div
          className="mouse-follower"
          style={{
            position: "absolute",
            top: mousePosition.y,
            left: mousePosition.x,

            pointerEvents: "none",
            transform: "translate(-50%, -50%)",
          }}
        />
      )}
    </div>
  );
};
