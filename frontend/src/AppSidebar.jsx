import { useEffect, useState } from "react";
import {
  BarChart3,
  FileText,
  Home,
  ListChecks,
  LogOut,
  ReceiptText,
  Settings,
  UserRound,
} from "lucide-react";

import { getCurrentUser } from "./api";
import "./AppShell.css";

const NAV_ITEMS = [
  { href: "/app", label: "Overview", icon: Home },
  { href: "/app/accomplishments", label: "Accomplishments", icon: ListChecks },
  { href: "/app#impact-receipts", label: "Impact Receipts", icon: ReceiptText },
  { href: "/app/reports", label: "Reports", icon: FileText },
];

function AppSidebar() {
  const [user, setUser] = useState(null);
  const path = window.location.pathname;

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      try {
        const data = await getCurrentUser();
        if (isMounted) {
          setUser(data);
        }
      } catch (error) {
        if (error.response?.status === 401) {
          localStorage.removeItem("bragstack_token");
          window.location.assign("/login");
        }
      }
    }

    void loadUser();

    return () => {
      isMounted = false;
    };
  }, []);

  function logout() {
    localStorage.removeItem("bragstack_token");
    window.location.assign("/login");
  }

  return (
    <aside className="app-sidebar">
      <a className="sidebar-brand" href="/app">
        <span className="sidebar-logo">B</span>
        <span>
          <strong>BragStack</strong>
          <small>Career proof</small>
        </span>
      </a>

      <a className="sidebar-add" href="/app#entries">
        + Add accomplishment
      </a>

      <nav className="sidebar-nav" aria-label="BragStack navigation">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const hrefPath = href.split("#")[0];
          const isActive = hrefPath === "/app"
            ? path === "/app" && !href.includes("#")
            : path === hrefPath;

          return (
            <a className={isActive ? "active" : ""} href={href} key={href}>
              <Icon size={18} />
              <span>{label}</span>
            </a>
          );
        })}

        {user?.public_slug && (
          <a href={`/brag/${user.public_slug}`} target="_blank" rel="noreferrer">
            <UserRound size={18} />
            <span>Public Profile</span>
          </a>
        )}

        <a href="/app#profile-settings">
          <Settings size={18} />
          <span>Settings</span>
        </a>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <span className="sidebar-user-avatar">
            {user?.name?.charAt(0).toUpperCase() || "B"}
          </span>
          <span>
            <strong>{user?.name || "BragStack member"}</strong>
            <small>{user?.headline || "Build your proof"}</small>
          </span>
        </div>

        <button type="button" onClick={logout}>
          <LogOut size={17} />
          Logout
        </button>
      </div>
    </aside>
  );
}

export default AppSidebar;
