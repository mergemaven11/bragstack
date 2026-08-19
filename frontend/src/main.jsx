import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import "./ProductPolish.css";
import RootContent from "./RootContent.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RootContent />
  </StrictMode>,
);
