import AccomplishmentsPage from "./AccomplishmentsPage.jsx";
import App from "./App.jsx";
import AppSidebar from "./AppSidebar.jsx";
import ImpactReceiptsPage from "./ImpactReceiptsPage.jsx";

function RootContent() {
  const path = window.location.pathname;
  const isAuthenticatedApp = path.startsWith("/app");

  let Content = App;

  if (path === "/app/accomplishments") {
    Content = AccomplishmentsPage;
  } else if (path === "/app/impact-receipts") {
    Content = ImpactReceiptsPage;
  }

  if (!isAuthenticatedApp) {
    return <Content />;
  }

  return (
    <div className="app-shell">
      <AppSidebar />
      <div className="authenticated-content">
        <Content />
      </div>
    </div>
  );
}

export default RootContent;
