import React, { useEffect, useState } from "react";
import "./CallToAction.css";
import { createPublishSitemapIndex } from "../../modules/apiCalls";
import { toast } from "react-hot-toast";
import { useNavigate } from "react-router-dom";

export const CallToAction = () => {
  const [url, setUrl] = useState("");
  const [hasPublicToken, setHasPublicToken] = useState(false);
  const navigate = useNavigate();

  const createSitemap = async () => {
    const tid = toast.loading("Creating sitemap...");
    try {
      const res = await createPublishSitemapIndex(url);
      console.log("Sitemap created", res);
      toast.dismiss(tid);
      toast.success("Sitemap created", {
        icon: "🚀",
      });
      localStorage.setItem("public_token", res.publish_token);
      navigate("/dashboard");
    } catch (error) {
      console.error("Error creating sitemap", error);
      toast.dismiss(tid);
      toast.error(`Error creating sitemap: ${error.response.data.error}`, {
        icon: "🥲",
      });
    }
  };

  useEffect(() => {
    const publicToken = localStorage.getItem("public_token");
    if (publicToken) {
      setHasPublicToken(true);
    }
  }, [navigate]);

  return (
    <section className="call-to-action">
      <h2>Are you ready to boost your website?</h2>
      {hasPublicToken && (
        <>
          <p>
            You already have a sitemap created. Go to the dashboard to see the
            magic! Or create an account to add unlimited sitemaps if you are
            already in love with Chaseo
          </p>
          <button onClick={() => navigate("/dashboard")}>
            Go to dashboard
          </button>
        </>
      )}
      {!hasPublicToken && (
        <>
          <input
            onChange={(e) => setUrl(e.target.value)}
            className="input"
            placeholder="Paste your sitemap link here"
          />
          <button onClick={createSitemap}>Make magic</button>
        </>
      )}
    </section>
  );
};
