import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import "./ProductPolish.css";
import App from "./App.jsx";
import AccomplishmentsPage from "./AccomplishmentsPage.jsx";
import ImpactReceiptsPage from "./ImpactReceiptsPage.jsx";
import AppSidebar from "./AppSidebar.jsx";

const path = window.location.pathname;
const isAuthenticatedApp = path.startsWith("/app");

let Content = App;

if (path === "/app/accomplishments") {
  Content = AccomplishmentsPage;
} else if (path === "/app/impact-receipts") {
  Content = ImpactReceiptsPage;
}

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
