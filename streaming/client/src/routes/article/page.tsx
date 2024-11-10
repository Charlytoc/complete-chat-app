import React from "react";
import { useLoaderData, Link } from "react-router-dom";

interface Article {
  title: string;
  // slug: string;
  id: string;
  content: string;
}

interface ArticleData {
  article: Article;
  suggestions: number;
}

const ArticleList: React.FC = () => {
  const loaderData = useLoaderData() as ArticleData[];

  return (
    <div>
      {loaderData.map((article: ArticleData, index: number) => (
        <div key={index}>
          <Link to={`/article/${article.article.id}`}>
            <h3>{article.article.title}</h3>
            {/* <h3>{article.article.id}</h3> */}
            <p>Number of suggestions: {article.suggestions}</p>
          </Link>
        </div>
      ))}
    </div>
  );
};

export default ArticleList;
