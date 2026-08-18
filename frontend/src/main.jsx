import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import App from "./App.jsx";
import AccomplishmentsPage from "./AccomplishmentsPage.jsx";
import AppSidebar from "./AppSidebar.jsx";

const path = window.location.pathname;
const isAuthenticatedApp = path.startsWith("/app");
const isAccomplishmentsPage = path === "/app/accomplishments";
const Content = isAccomplishmentsPage ? AccomplishmentsPage : App;

createRoot(document.getElementById("root")).render(
  <StrictMode>
    {isAuthenticatedApp ? (
      <div className="app-shell">
        <AppSidebar />
        <div className="authenticated-content">
          <Content />
        </div>
      </div>
    ) : (
      <Content />
    )}
  </StrictMode>,
);
