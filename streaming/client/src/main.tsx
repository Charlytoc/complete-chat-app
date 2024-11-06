import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import Root from "./routes/root/page.tsx";
import { rootLoader } from "./routes/root/loader.ts";
import { chatLoader } from "./routes/chat/loader.ts";
import "./index.css";
import Signup from "./routes/signup/page.tsx";
import ChatView from "./routes/chat/page.tsx";
import Layout from "./routes/Layout.tsx";
import Login from "./routes/login/page.tsx";
import ArticleList from "./routes/article/page.tsx";
import ArticleDetail from "./components/Article/ArticleDetail";
import { articleLoader } from "./routes/article/loader.ts";
import Dashboard from "./routes/Dashboard/page.tsx";
import { dashboardLoader } from "./routes/Dashboard/loader.ts";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    // element: <Root />,
    children: [
      {
        path: "/",
        element: <Root />,
        loader: rootLoader,
      },
      {
        path: "article",
        element: <ArticleList />,
        loader: articleLoader,
      },
      {
        path: "article/:id",
        element: <ArticleDetail />,
        loader: articleLoader,
      },
      {
        path: "dashboard",
        element: <Dashboard />,
        loader: dashboardLoader
      }
    ],
  },
  {
    path: "/signup",
    element: <Signup />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/chat",
    element: <ChatView />,
    loader: chatLoader,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
