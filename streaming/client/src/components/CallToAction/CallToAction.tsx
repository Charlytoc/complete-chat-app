import React from "react";
import "./CallToAction.css";
import { createPublishSitemapIndex } from "../../modules/apiCalls";
import { toast } from "react-hot-toast";
import { useNavigate } from "react-router-dom";

export const CallToAction = () => {
  const [url, setUrl] = React.useState("");
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

  return (
    <section className="call-to-action">
      <h2>Are you ready to boost your website?</h2>
      <input
        onChange={(e) => setUrl(e.target.value)}
        className="input"
        placeholder="Paste your sitemap link here"
      />
      <button onClick={createSitemap}>Make magic</button>
    </section>
  );
};
