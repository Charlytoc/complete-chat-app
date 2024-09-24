import React from "react";

import { useLoaderData, useSearchParams } from "react-router-dom";

interface Article {
  title: string;
  slug: string;
  content: string;
}

interface ArticleData {
  article: Article;
  suggestions: number;
}

interface Suggestion {
  id: number;
  original_text: string;
  replacement_text: string;
}

interface SuggestionData {
  article: Article;
  suggestion: Suggestion;
}

export function Article() {
  const loaderData = useLoaderData() as ArticleData[] | SuggestionData;
  console.log(loaderData);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [searchParams, setSearchParams] = useSearchParams();

  const handleArticleClick = (slug: string) => {
    setSearchParams({ article: slug });
  };

  return (
    <main>
      {/* <button onClick={handleSubmit}>Submit</button> */}
      <div>
        {Array.isArray(loaderData) ? (
          loaderData.map((article: ArticleData, index: number) => (
            <div
              key={index}
              onClick={() => handleArticleClick(article.article.slug)}
            >
              <h3>{article.article.title}</h3>
              <h3>{article.article.slug}</h3>
              <p>Number of suggestions: {article.suggestions}</p>
            </div>
          ))
        ) : (
          <div>
            <h3>{loaderData.article.title}</h3>
            <h3>{loaderData.article.slug}</h3>
            <textarea
              value={loaderData.article.content}
              placeholder="Enter your text here"
            />
            <div>
              <h4>{loaderData.suggestion.original_text}</h4>
              <h4>{loaderData.suggestion.replacement_text}</h4>
              {/* {loaderData.suggestion.map(
                (suggestion: Suggestion, index: number) => (
                  <p key={index}>{suggestion.content}</p>
                )
              )} */}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
