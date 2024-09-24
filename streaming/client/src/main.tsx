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
import { Article } from "./routes/article/page.tsx";
import { articleLoader } from "./routes/article/loader.ts"

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
  // {
  //   path: "/new",
  //   element: <Layout />,
  //   children: [
  //     {
  //       path: "/new/article",
  //       element: <Article />,
  //     },
  //   ],
  // },
  {
    path: "/article",
    element: <Article />,
    loader: articleLoader
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
