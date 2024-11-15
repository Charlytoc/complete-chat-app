import React, { useState, useEffect, useRef } from "react";
import { useLoaderData } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import "./ArticleDetail.css";

interface Article {
  title: string;
  slug: string;
  html_content: string;
  article_content_md: string;
}

interface Suggestion {
  id: number;
  original_text: string;
  replacement_text: string;
}

interface SuggestionData {
  article: Article;
  suggestion: Suggestion[];
}

function replaceSubstring(
  articleContent: string,
  substring: string,
  replacement: string
): string {
  return articleContent.replace(new RegExp(substring, "g"), replacement);
}

const ArticleDetail: React.FC = () => {
  const loaderData = useLoaderData() as SuggestionData;
  const [editorContent, setEditorContent] = useState(
    // loaderData.article.article_content_md 
    // TODO: This content should be the HTML content instead
    // HINT: article.html_content es la key que nos interesa
    loaderData.article.html_content
  );

  const [suggestions, setSuggestions] = useState(
    loaderData.suggestion as Suggestion[]
  );
  const [results, setResults] = useState([] as JSX.Element[]);

  useEffect(() => {
    const _results = highlightSubstring(
      editorContent,
      suggestions[0].original_text,
      suggestions[0].replacement_text
    );

    setResults(_results);
  }, [suggestions]);

  const rejectSuggestion = () => {
    const suggestionsCopy = [...suggestions];
    const rejectedSuggestion = suggestionsCopy.shift();

    setSuggestions(suggestionsCopy);
    console.log(loaderData.article.slug);

    fetch(`v1/seo/article/${loaderData.article.slug}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        // @ts-ignore
        suggestion_id: rejectedSuggestion.id,
        new_status: "REJECTED",
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Success: ", data);
      })
      .catch((error) => {
        console.error("Error: ", error);
      });
  };
  const acceptSuggestion = (replacementText: string) => {
    // @ts-ignore
    const suggestionsCopy = [...suggestions];
    const aceptedSuggestion = suggestionsCopy.shift();

    if (aceptedSuggestion) {
      const newContent = replaceSubstring(
        editorContent,
        aceptedSuggestion?.original_text,
        replacementText
      );

      setSuggestions(suggestionsCopy);
      setEditorContent(newContent);
      console.log(loaderData.article.slug);

      // TODO: SENT A PUT REQUEST TO THE BACKEND
      // {new_status: "ACCEPTED", article_content: newContent, suggestion_id: suggestionAccepted.id}
      fetch(`v1/seo/article/${loaderData.article.slug}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          new_status: "ACCEPTED",
          article_content: newContent,
          suggestion_id: aceptedSuggestion.id,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          console.log("Succes: ", data);
        })
        .catch((error) => {
          console.error("Error: ", error);
        });
    }
  };

  function highlightSubstring(
    articleContent: string,
    searchValue: string,
    replacementText: string
  ): JSX.Element[] {
    const startIndex = articleContent.indexOf(searchValue);

    if (startIndex === -1) {
      return [<span>{articleContent}</span>];
    }

    const beforeHighlight = articleContent.slice(0, startIndex);
    const afterHighlight = articleContent.slice(
      startIndex + searchValue.length
    );

    return [
      <span key="before">{beforeHighlight}</span>,
      <SuggestionComponent
        rejectSuggestion={rejectSuggestion}
        acceptSuggestion={acceptSuggestion}
        originalText={searchValue}
        replacementText={replacementText}
      ></SuggestionComponent>,
      <span key="after">{afterHighlight}</span>,
    ];
  }

  console.log(suggestions);

  return (
    <div className="article-detail-container">
      <h3>{loaderData.article.title}</h3>
      <div className="article-detail-section">{results.map((e) => e)}</div>
    </div>
  );
};

const SuggestionComponent = ({
  originalText,
  replacementText,
  rejectSuggestion,
  acceptSuggestion,
}) => {
  const [text, setText] = useState(originalText);
  const [editableText, setEditableText] = useState(replacementText);
  const editableRef = useRef(null);

  useEffect(() => {
    setText(originalText);
    setEditableText(replacementText);
  }, [originalText, replacementText]);

  const handleAccept = () => {
    acceptSuggestion(editableText);
  };

  const handleReject = () => {
    rejectSuggestion();
  };

  const handleChange = (event: React.ChangeEvent<HTMLDivElement>) => {
    // TODO: Esto va a cambiar. Debes poder imprimir exactamente qué elemento del DOM está siendo modificado
    console.log("Modified element: ", event.currentTarget);
    setEditableText(event.target.innerText);
  };

  useEffect(() => {
    // Establecer el foco en el div editable y mover el cursor al final
    if (editableRef.current) {
      // @ts-ignore
      editableRef.current.focus();
      const range = document.createRange();
      const selection = window.getSelection();
      range.selectNodeContents(editableRef.current);
      range.collapse(false); // Colapsar al final

      if (selection) {
        selection.removeAllRanges();
        selection.addRange(range);
      }
    }
  }, [editableText]); // Ejecutar cada vez que editableText cambie

  return (
    <div className="suggestion-component">
      {text}
      <button onClick={handleAccept}>Accept</button>
      <button onClick={handleReject}>Reject</button>
      <div
        className="suggestion-modal"
        contentEditable={true}
        onInput={handleChange}
        suppressContentEditableWarning={true}
        ref={editableRef}
        // TODO:  dangerouslySetInnerHTML={{ __html: editableText }}
        // Set tiene que ver el contenido HTML renderizado
        dangerouslySetInnerHTML={{ __html: editableText }}
      >
        {editableText}
      </div>
    </div>
  );
};
export default ArticleDetail;
