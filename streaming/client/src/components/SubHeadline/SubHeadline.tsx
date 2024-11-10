import React, { useEffect, useState } from "react";

import "./SubHeadline.css";

export const SubHeadline = () => {
  return (
    <div className="sub-headline">
      <h2>Give us your sitemap, we take care of</h2>
      <SimpleSlider
        texts={[
          "Find the most relevant articles to link to",
          "Automatically add links to your articles",
          "Improve your SEO",
        ]}
      />
    </div>
  );
};

const SimpleSlider = ({ texts }: { texts: string[] }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % texts.length);
    }, 3000); // Change text every 3 seconds

    return () => clearInterval(interval);
  }, [texts.length]);

  return (
    <div className="simple-slider">
      {texts.map((text, index) => (
        <div
          key={index}
          className={`slider-text ${index === currentIndex ? "active" : ""}`}
        >
          {text}
        </div>
      ))}
    </div>
  );
};
