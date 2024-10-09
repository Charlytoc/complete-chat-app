import React, { useState } from "react";
import { useLoaderData } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import "./ArticleDetail.css";

interface Article {
  title: string;
  slug: string;
  content: string;
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

const ArticleDetail: React.FC = () => {
  const loaderData = useLoaderData() as SuggestionData; 
  const [editorContent, setEditorContent] = useState(loaderData.article.content);

  const modules = {
    toolbar: [
      [{ 'size': ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline'], 
      ['link', 'image'], 
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      ['clean'],
    ],
  };

  return (
    <div className="article-detail-container">
      <div className="article-detail-section">
        <h3>{loaderData.article.title}</h3>
        <h3>{loaderData.article.slug}</h3>
        <div className="article-detail-content">
          <ReactMarkdown>{loaderData.article.content}</ReactMarkdown>
        </div>
      </div>
      <div className="article-detail-section">
        <div className="react-quill-container">
          <ReactQuill
            value={editorContent}
            onChange={setEditorContent} 
            modules={modules}
            placeholder="Enter your text here"
          />
        </div>
      </div>
    </div>
  );
};

export default ArticleDetail;
