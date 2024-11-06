import React from "react";
import "./Navbar.css";
import { Link } from "react-router-dom";

export const Navbar = () => {
  return (
    <nav className="navbar">
      <section className="logo">
        <h1 className="text-white">
          <strong>Chaseo</strong>
        </h1>
      </section>
      <section className="nav-links">
        <Link className="fancy-bg text-white" to={"/signup"}>
          Signup
        </Link>
        <Link to={"/login"}>Login</Link>
      </section>
    </nav>
  );
};
