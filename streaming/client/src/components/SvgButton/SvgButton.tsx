import React from "react";

// @ts-ignore
import styles from "./SvgButton.module.css";
export const SvgButton = ({ onClick, svg, text }) => {
  return (
    <button className={styles.svgButton} onClick={onClick}>
      <span>{svg}</span>
      <span>{text}</span>
    </button>
  );
};
