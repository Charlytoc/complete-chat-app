import React from "react";
import { useLoaderData, useNavigate } from "react-router-dom";
import "./page.css";
import { fetchArticleAndSuggest } from "../../modules/apiCalls";
import toast from "react-hot-toast";
import { SvgButton } from "../../components/SvgButton/SvgButton";
import { useStore } from "../../modules/store";

type TArticle = {
  id: string;
  title: string;
};

type TSitemap = {
  id: string;
  url: string;
  articles: TArticle[];
};

type TSitemapIndex = {
  id: string;
  url: string;
  sitemaps: TSitemap[];
};

export default function Dashboard() {
  const loaderData = useLoaderData() as TSitemapIndex[];

  return (
    <main>
      {/* <h1 className="fancy-bg padding-big text-center">Dashboard</h1> */}

      <div className="d-flex gap-medium flex-y">
        <h3 className="fancy-bg text-center">
          We found this sitemaps for you!
        </h3>
        <p>Select one article and wait for the magic!</p>

        <SvgButton
          svg={"p"}
          onClick={() => toast.success("IMPLEMENTAMEEE")}
          text={"Select one for me"}
        />
        {loaderData &&
          loaderData.map((item) => {
            return (
              <div key={item.id}>
                <h2>Index: {item.url}</h2>
                <ul>
                  {item.sitemaps.map((sitemap) => {
                    return (
                      <li key={sitemap.id}>
                        <details>
                          <summary>
                            <span>{sitemap.url}</span>
                          </summary>
                          {sitemap.articles.map((article) => {
                            return (
                              <ArticleDetail
                                key={article.id}
                                article={article}
                              />
                            );
                          })}
                        </details>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
      </div>
    </main>
  );
}

const ArticleDetail = ({ article }) => {
  const {} = useStore((s) => ({
    // credits
    // TODO: Traer el useCredit
  }));
  const navigate = useNavigate();

  const suggest = async () => {
    // TODO: usa un chaseo credit antes de hacer el fetch de las sugerencias
    const tid = toast.loading("Suggesting changes to article...");
    try {
      const res = await fetchArticleAndSuggest(article.id);
      console.log("Suggestion:", res);
      toast.dismiss(tid);
      toast.success("Ready to boost your website!");
      navigate("/article/" + article.id);
    } catch (error) {
      toast.dismiss(tid);
      toast.error("Error suggesting article", {
        icon: "🥲",
      });
      console.error("Error suggesting article", error);
    }
  };

  return (
    <div onClick={suggest} className="article-detail">
      <h3>{article.title}</h3>
      <p>{article.url}</p>
    </div>
  );
};
