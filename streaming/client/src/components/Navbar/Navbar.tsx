import React, { useEffect, useState } from "react";
import "./Navbar.css";
import { Link, useNavigate } from "react-router-dom";
import { SVGS } from "../../assets/svgs";
import { SvgButton } from "../SvgButton/SvgButton";
import toast from "react-hot-toast";
import { useStore } from "../../modules/store";

export const Navbar = () => {
  // If the user is inside dashboard and is not logged in (doesn't have a token (not a public_token, a token) in the localStorage), the navbar should show the following buttons:
  // Create an account
  // {AVAILABLECREDITS} Credits y un svg de moneda (coin)

  // But is it is logged in
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  const checkLogIn = () => {
    try {
      const token = localStorage.getItem("public_token");
      setIsLoggedIn(!!token);
    } catch (error) {
      console.error("Error checking loggin status", error);
    }
  };

  const hanldeLogout = () => {
    localStorage.removeItem("public_token");
    setIsLoggedIn(false);
    toast.success("Logged out successfully");
  };

  useEffect(()=> {
    checkLogIn();
  }, [])

  return (
    <nav className="navbar">
      div
      <section className="logo">
        <h1 className="text-white">
          <strong>Chaseo</strong>
        </h1>
      </section>
      <section className="nav-links">
        {/* TODO if is logged in, don't show this buttons */}
        {!isLoggedIn && (
          <button className="fancy-bg text-white" onClick={() => navigate('/signup')}>
            Signup
          </button>
        )}
        {isLoggedIn && (
          <button className="fancy-bg text-white" onClick={hanldeLogout}>
            Loguot
          </button>
        )}

        <ChaseoCredits />
      </section>
    </nav>
  );
};

const ChaseoCredits = () => {
  const {credits} = useStore((s)=>({
    credits: s.credits
  }))

  const fetchCredits = async () => {
    // const token = localStorage.getItem("token");
    // const response = await fetch('url to credits', {
    //   method: 'GET',
    //   headers: {
    //     'Authorization': `Bearer ${token}`,
    //     'isPublic': 'false' || 'true',
    //   }
    // });
    // const data = await response.json();
    // useStore.setState({ credits: data.credits })
  };

  useEffect(() => {
    // fetch credits from the user
    // TODO: This function will be stored in the zustand store, it will call the backend to retrieve the remaining credits for the given token.
    // FUTURE: Sent a proper header isPublic weatcher the token is public or not
    // fetchCredits(5);
  });
  return (
    <div className="credits d-flex align-center gap-small">
      <SvgButton
        onClick={() => toast.success("No me has implementado")}
        text={"Chaseo credits"}
        svg={SVGS.coin}
      />

      <span>{credits}</span>
    </div>
  );
};
