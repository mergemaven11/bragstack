import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2, X } from "lucide-react";

import AuthPage from "./AuthPage";
import PublicBragPage from "./PublicBragPage";
import LandingPage from "./LandingPage";
import ReportsPage from "./ReportsPage";

import {
  createEntry,
  createImpactReceiptFromEntry,
  deleteEntry,
  getCategoriesSummary,
  getCurrentUser,
  getEntries,
  getImpactReceipts,
  getTagsSummary,
  getWeeklyReport,
  loginUser,
  registerUser,
  updateCurrentUserProfile,
  updateImpactReceipt,
  updateEntry,
} from "./api";
import "./App.css";

const DASHBOARD_PAGE_SIZE = 5;
const ENTRY_TYPES = [
  "Current Job",
  "Previous Job",
  "Personal Development",
  "Side Project",
  "Open Source",
  "Learning / Certification",
];

const getTodayDate = () => new Date().toISOString().slice(0, 10);

const formatLabel = (value = "") =>
  value
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());

const EMPTY_FORM = {
  title: "",
  category: "",
  entry_date: getTodayDate(),
  entry_type: "Current Job",
  situation: "",
  action: "",
  impact: "",
  lesson: "",
  tags: "",
  is_public: false,
};

const EMPTY_PROFILE_FORM = {
  name: "",
  headline: "",
  bio: "",
  location: "",
  github_url: "",
  portfolio_url: "",
  resume_url: "",
};

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [entries, setEntries] = useState([]);
  const [entriesMeta, setEntriesMeta] = useState({ total_entries: 0 });
  const [impactReceipts, setImpactReceipts] = useState([]);
  const [creatingReceiptEntryId, setCreatingReceiptEntryId] = useState(null);
  const [receiptNotice, setReceiptNotice] = useState("");
  const [receiptError, setReceiptError] = useState("");
  const [updatingReceiptId, setUpdatingReceiptId] = useState(null);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [tagsSummary, setTagsSummary] = useState(null);
  const [categoriesSummary, setCategoriesSummary] = useState(null);
  const [isOffline, setIsOffline] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEntryId, setEditingEntryId] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [profileForm, setProfileForm] = useState(EMPTY_PROFILE_FORM);

  const path = window.location.pathname;
  const isLandingPage = path === "/";
  const isPublicPage = path.startsWith("/brag");
  const isLoginPage = path === "/login";
  const isRegisterPage = path === "/register";
  const isReportsPage = path === "/app/reports";
  const dashboardPage = Math.max(
    1,
    Number(new URLSearchParams(window.location.search).get("page")) || 1,
  );

  async function loadDashboard() {
    try {
      const [
        userData,
        entriesData,
        receiptsData,
        weeklyData,
        tagsData,
        categoriesData,
      ] = await Promise.all([
        getCurrentUser(),
        getEntries(
          DASHBOARD_PAGE_SIZE,
          (dashboardPage - 1) * DASHBOARD_PAGE_SIZE,
        ),
        getImpactReceipts(),
        getWeeklyReport(),
        getTagsSummary(),
        getCategoriesSummary(),
      ]);

      setCurrentUser(userData);
      setEntries(entriesData.entries ?? []);
      setEntriesMeta({
        total_entries: entriesData.total_entries ?? 0,
      });
      setImpactReceipts(receiptsData.receipts ?? []);
      setWeeklyReport(weeklyData);
      setTagsSummary(tagsData);
      setCategoriesSummary(categoriesData);
      setIsOffline(false);
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        localStorage.removeItem("bragstack_token");
        window.location.href = "/login";
        return;
      }

      setIsOffline(true);
    }
  }

  function openProfileModal() {
    setProfileForm({
      name: currentUser?.name ?? "",
      headline: currentUser?.headline ?? "",
      bio: currentUser?.bio ?? "",
      location: currentUser?.location ?? "",
      github_url: currentUser?.github_url ?? "",
      portfolio_url: currentUser?.portfolio_url ?? "",
      resume_url: currentUser?.resume_url ?? "",
    });

    setProfileError("");
    setIsProfileModalOpen(true);
  }

  function closeProfileModal() {
    setIsProfileModalOpen(false);
    setProfileError("");
  }

  function handleProfileInputChange(event) {
    const { name, value } = event.target;

    setProfileForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleProfileSubmit(event) {
    event.preventDefault();
    setIsSavingProfile(true);
    setProfileError("");

    try {
      const updatedUser = await updateCurrentUserProfile(profileForm);

      setCurrentUser(updatedUser);
      closeProfileModal();
    } catch (error) {
      console.error(error);

      setProfileError(
        error.response?.data?.detail ??
          "Your profile could not be saved.",
      );
    } finally {
      setIsSavingProfile(false);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("bragstack_token");

    if (
      isLandingPage ||
      isPublicPage ||
      isLoginPage ||
      isRegisterPage ||
      isReportsPage
    ) {
      return;
    }

    if (!token) {
      window.location.assign("/login");
      return;
    }

    const timeoutId = window.setTimeout(() => {
      void loadDashboard();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, [
    isLandingPage,
    isPublicPage,
    isLoginPage,
    isRegisterPage,
    isReportsPage,
    dashboardPage,
  ]);

  function openCreateModal() {
    setEditingEntryId(null);

    setFormData({
      ...EMPTY_FORM,
      entry_date: getTodayDate(),
    });

    setIsModalOpen(true);
  }

  function openEditModal(entry) {
    setEditingEntryId(entry.id);

    setFormData({
      title: entry.title ?? "",
      category: entry.category ?? "",
      entry_date: entry.entry_date ?? getTodayDate(),
      entry_type: entry.entry_type ?? "Current Job",
      situation: entry.situation ?? "",
      action: entry.action ?? "",
      impact: entry.impact ?? "",
      lesson: entry.lesson ?? "",
      tags: entry.tags?.join(", ") ?? "",
      is_public: entry.is_public ?? false,
    });

    setIsModalOpen(true);
  }

  function closeModal() {
    setIsModalOpen(false);
    setEditingEntryId(null);

    setFormData({
      ...EMPTY_FORM,
      entry_date: getTodayDate(),
    });
  }

  function handleInputChange(event) {
    const { name, value, type, checked } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleCreateEntry(event) {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      const payload = {
        ...formData,
        tags: formData.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      };

      if (editingEntryId) {
        await updateEntry(editingEntryId, payload);
      } else {
        await createEntry(payload);
      }

      closeModal();
      await loadDashboard();
    } catch (err) {
      console.error(err);
      setIsOffline(true);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteEntry(entryId) {
    const confirmed = window.confirm("Delete this brag entry?");

    if (!confirmed) {
      return;
    }

    try {
      await deleteEntry(entryId);
      await loadDashboard();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleCreateImpactReceipt(entryId) {
    setCreatingReceiptEntryId(entryId);
    setReceiptNotice("");
    setReceiptError("");

    try {
      await createImpactReceiptFromEntry(entryId, {
        contribution: null,
        result: null,
        evidence: [],
        skills: [],
        credit: [],
        is_public: false,
      });

      await loadDashboard();
      setReceiptNotice("Impact Receipt created successfully.");
    } catch (error) {
      console.error(error);

      if (error.response?.status === 409) {
        setReceiptError("This entry already has an Impact Receipt.");
      } else {
        setReceiptError(
          error.response?.data?.detail ??
            "The Impact Receipt could not be created.",
        );
      }
    } finally {
      setCreatingReceiptEntryId(null);
    }
  }

  async function handleToggleReceiptVisibility(receipt) {
    setUpdatingReceiptId(receipt.id);
    setReceiptNotice("");
    setReceiptError("");

    try {
      const nextVisibility = !receipt.is_public;

      await updateImpactReceipt(receipt.id, {
        is_public: nextVisibility,
      });

      await loadDashboard();
      setReceiptNotice(
        nextVisibility
          ? "Impact Receipt is now public."
          : "Impact Receipt is now private.",
      );
    } catch (error) {
      console.error(error);
      setReceiptError(
        error.response?.data?.detail ??
          "Receipt visibility could not be updated.",
      );
    } finally {
      setUpdatingReceiptId(null);
    }
  }

  async function handleLogin(credentials) {
    const data = await loginUser(credentials);
    localStorage.setItem("bragstack_token", data.access_token);
    window.location.href = "/app";
  }

  async function handleRegister(user) {
    const data = await registerUser(user);
    localStorage.setItem("bragstack_token", data.access_token);
    window.location.href = "/app";
  }

  const topTags = tagsSummary?.tags ? Object.entries(tagsSummary.tags) : [];

  const receiptSourceEntryIds = new Set(
    impactReceipts.map((receipt) => receipt.source_entry_id),
  );

  if (isPublicPage) {
    return <PublicBragPage />;
  }

  if (isLandingPage) {
    return <LandingPage />;
  }

  if (isLoginPage) {
    return <AuthPage mode="login" onLogin={handleLogin} />;
  }

  if (isRegisterPage) {
    return <AuthPage mode="register" onRegister={handleRegister} />;
  }

  if (isReportsPage) {
    return <ReportsPage />;
  }

  const token = localStorage.getItem("bragstack_token");

  if (!token) {
    return null;
  }

  const totalDashboardPages = Math.max(
    1,
    Math.ceil(entriesMeta.total_entries / DASHBOARD_PAGE_SIZE),
  );
  const dashboardStart = entriesMeta.total_entries
    ? (dashboardPage - 1) * DASHBOARD_PAGE_SIZE + 1
    : 0;
  const dashboardEnd = Math.min(
    dashboardPage * DASHBOARD_PAGE_SIZE,
    entriesMeta.total_entries,
  );

  return (
    <main className="page">
      <section className="hero">
        <div className="hero-copy">
          <div className="badge">BragStack</div>

          <h1>
            Turn daily work into
            <span> career proof.</span>
          </h1>

          <p>
            Track technical wins, skill growth, resume bullets, and project
            evidence in one clean portfolio-ready space.
          </p>

          <div className="hero-actions">
            <a className="btn primary" href="#entries">
              View proof
            </a>

            <a className="btn secondary" href="/app/reports">
              Reports
            </a>

            <a
              className="btn secondary"
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
            >
              API docs
            </a>
          </div>
        </div>

        <aside className="profile-card">
          <div className="profile-card-heading">
            <p className="mini-label">Proof Profile Card</p>

            <button
              type="button"
              className="profile-edit-button"
              onClick={openProfileModal}
            >
              <Pencil size={15} />
              Edit profile
            </button>
          </div>

          <div className="avatar">
            {currentUser?.name?.charAt(0).toUpperCase() || "B"}
          </div>

          <h2>
            {currentUser?.name
              ? `${currentUser.name}'s BragStack`
              : "Your BragStack"}
          </h2>

          <p className="profile-headline">
            {currentUser?.headline ||
              "Add a professional headline to introduce yourself."}
          </p>

          {currentUser?.bio && <p className="profile-bio">{currentUser.bio}</p>}

          {currentUser?.location && (
            <p className="profile-location">{currentUser.location}</p>
          )}

          <div className="proof-links">
            {currentUser?.public_slug && (
              <a
                href={`/brag/${currentUser.public_slug}`}
                target="_blank"
                rel="noreferrer"
              >
                Proof Profile <span>View profile</span>
              </a>
            )}

            {currentUser?.resume_url && (
              <a
                href={currentUser.resume_url}
                target="_blank"
                rel="noreferrer"
              >
                Résumé <span>Open</span>
              </a>
            )}

            {currentUser?.portfolio_url && (
              <a
                href={currentUser.portfolio_url}
                target="_blank"
                rel="noreferrer"
              >
                Portfolio <span>Visit</span>
              </a>
            )}

            {currentUser?.github_url && (
              <a
                href={currentUser.github_url}
                target="_blank"
                rel="noreferrer"
              >
                GitHub <span>Profile</span>
              </a>
            )}
          </div>
        </aside>
      </section>

      {isOffline && (
        <section className="notice">
          <strong>Connection problem</strong>
          <span>BragStack could not load all dashboard data.</span>
        </section>
      )}

      <section className="stats-grid">
        <article className="stat-card">
          <p>Weekly Entries</p>
          <strong>{weeklyReport?.total_entries ?? 0}</strong>
          <span>Wins logged in the last 7 days</span>
        </article>

        <article className="stat-card">
          <p>Unique Tags</p>
          <strong>{tagsSummary?.total_unique_tags ?? 0}</strong>
          <span>Skills tracked across entries</span>
        </article>

        <article className="stat-card">
          <p>Categories</p>
          <strong>{categoriesSummary?.total_unique_categories ?? 0}</strong>
          <span>Career areas documented</span>
        </article>
      </section>

      <section className="impact-section" id="impact-receipts">
        <div className="impact-section-header">
          <div>
            <p className="mini-label">Evidence-Backed Proof</p>
            <h2>Impact Receipts</h2>
            <p>
              Structured proof of what you contributed, what changed, and what
              evidence supports it.
            </p>
          </div>

          <span className="impact-count">
            {impactReceipts.length}{" "}
            {impactReceipts.length === 1 ? "receipt" : "receipts"}
          </span>
        </div>

        {receiptNotice && (
          <p className="receipt-feedback success">{receiptNotice}</p>
        )}

        {receiptError && (
          <p className="receipt-feedback error">{receiptError}</p>
        )}

        {impactReceipts.length === 0 ? (
          <div className="impact-empty-state">
            <h3>No Impact Receipts yet.</h3>
            <p>Use the Create Impact Receipt button on a meaningful entry below.</p>
          </div>
        ) : (
          <div className="impact-receipt-grid">
            {impactReceipts.map((receipt) => (
              <article className="impact-receipt-card compact" key={receipt.id}>
                <div className="impact-receipt-top">
                  <div>
                    <p className="mini-label">Impact Receipt</p>
                    <h3>{receipt.accomplishment}</h3>
                  </div>

                  <div className="entry-actions">
                    <span
                      className={`visibility-badge ${
                        receipt.is_public ? "public" : "private"
                      }`}
                    >
                      {receipt.is_public ? "Public" : "Private"}
                    </span>

                    <button
                      type="button"
                      className="profile-edit-button"
                      disabled={updatingReceiptId === receipt.id}
                      onClick={() => handleToggleReceiptVisibility(receipt)}
                    >
                      {updatingReceiptId === receipt.id
                        ? "Saving..."
                        : receipt.is_public
                          ? "Make private"
                          : "Make public"}
                    </button>
                  </div>
                </div>

                <div className="impact-result-preview">
                  <span>Result</span>
                  <p>{receipt.result}</p>
                </div>

                <div className="receipt-summary-row">
                  <span>{receipt.evidence?.length ?? 0} evidence</span>
                  <span>{receipt.credit?.length ?? 0} contributors</span>
                  <span>
                    {receipt.confirmations?.filter(
                      (confirmation) => confirmation.status === "confirmed",
                    ).length ?? 0}{" "}
                    confirmed
                  </span>
                </div>

                <div className="trust-signal-list">
                  {receipt.trust_signals?.map((signal) => (
                    <span key={signal}>{formatLabel(signal)}</span>
                  ))}
                </div>

                <details className="receipt-details">
                  <summary>View receipt details</summary>

                  <div className="receipt-details-content">
                    <div className="impact-receipt-detail">
                      <span>My contribution</span>
                      <p>{receipt.contribution}</p>
                    </div>

                    {receipt.skills?.length > 0 && (
                      <div className="impact-receipt-detail">
                        <span>Skills demonstrated</span>

                        <div className="tags">
                          {receipt.skills.map((skill) => (
                            <span key={skill}>{skill}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {receipt.evidence?.length > 0 && (
                      <div className="impact-receipt-detail">
                        <span>Evidence</span>

                        <div className="impact-evidence-list">
                          {receipt.evidence.map((evidenceItem, index) => (
                            <div
                              className="impact-evidence-item"
                              key={`${evidenceItem.title}-${index}`}
                            >
                              <strong>{evidenceItem.title}</strong>

                              <small>
                                {formatLabel(evidenceItem.evidence_type)}
                              </small>

                              {evidenceItem.reference && (
                                <p>{evidenceItem.reference}</p>
                              )}

                              {evidenceItem.description && (
                                <p>{evidenceItem.description}</p>
                              )}

                              <span
                                className={`visibility-badge ${
                                  evidenceItem.is_public ? "public" : "private"
                                }`}
                              >
                                {evidenceItem.is_public
                                  ? "Public evidence"
                                  : "Private evidence"}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {receipt.credit?.length > 0 && (
                      <div className="impact-receipt-detail">
                        <span>Shared credit</span>

                        <div className="impact-credit-list">
                          {receipt.credit.map((creditItem, index) => (
                            <p key={`${creditItem.name}-${index}`}>
                              <strong>{creditItem.name}</strong>
                              {" — "}
                              {creditItem.contribution}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </details>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="toolbar">
        <div>
          <p className="mini-label">Action</p>
          <h2>Manage your proof</h2>
        </div>

        <div className="toolbar-actions">
          <button
            className="btn secondary"
            type="button"
            onClick={() => {
              localStorage.removeItem("bragstack_token");
              window.location.href = "/login";
            }}
          >
            Logout
          </button>

          <button
            className="btn primary icon-btn"
            type="button"
            onClick={openCreateModal}
          >
            <Plus size={18} />
            New Entry
          </button>
        </div>
      </section>

      <section className="dashboard-grid">
        <article className="panel" id="entries">
          <div className="panel-header">
            <div>
              <p className="mini-label">Recent Proof</p>
              <h2>Latest entries</h2>
            </div>
          </div>

          {entries.length === 0 ? (
            <div className="empty-state">
              <h3>No entries loaded yet.</h3>
              <p>
                Add a brag entry to begin building your evidence-backed career
                record.
              </p>
            </div>
          ) : (
            <>
              <div className="entry-list">
                {entries.map((entry) => {
                  const hasReceipt = receiptSourceEntryIds.has(entry.id);
                  const isCreatingReceipt = creatingReceiptEntryId === entry.id;

                  return (
                    <article className="entry-card" key={entry.id}>
                      <div className="entry-top">
                        <div>
                          <p className="mini-label">
                            {entry.category}
                            {entry.entry_type ? ` • ${entry.entry_type}` : ""}
                            {entry.entry_date ? ` • ${entry.entry_date}` : ""}
                          </p>

                          <h3>{entry.title}</h3>
                        </div>

                        <div className="entry-actions">
                          <span
                            className={`visibility-badge ${
                              entry.is_public ? "public" : "private"
                            }`}
                          >
                            {entry.is_public ? "Public" : "Private"}
                          </span>

                          <button
                            type="button"
                            className="icon-action"
                            onClick={() => openEditModal(entry)}
                            aria-label="Edit entry"
                            title="Edit entry"
                          >
                            <Pencil size={17} strokeWidth={2.4} />
                          </button>

                          <button
                            type="button"
                            className="icon-action danger"
                            onClick={() => handleDeleteEntry(entry.id)}
                            aria-label="Delete entry"
                            title="Delete entry"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>

                      <p>{entry.resume_bullet}</p>

                      <div className="tags">
                        {entry.tags?.map((tag) => (
                          <span key={tag}>{tag}</span>
                        ))}
                      </div>

                      <div className="entry-receipt-action">
                        <button
                          type="button"
                          className="btn secondary receipt-button"
                          disabled={hasReceipt || isCreatingReceipt}
                          onClick={() => handleCreateImpactReceipt(entry.id)}
                        >
                          {isCreatingReceipt
                            ? "Creating receipt..."
                            : hasReceipt
                              ? "Impact Receipt created"
                              : "Create Impact Receipt"}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>

              <div className="pagination-shell">
                <span className="pagination-summary">
                  Showing {dashboardStart}–{dashboardEnd} of{" "}
                  {entriesMeta.total_entries} accomplishments · Page{" "}
                  {dashboardPage} of {totalDashboardPages}
                </span>
                <div className="pagination-controls">
                  {dashboardPage > 1 ? (
                    <a href={`/app?page=${dashboardPage - 1}#entries`}>
                      Previous
                    </a>
                  ) : (
                    <span className="disabled">Previous</span>
                  )}

                  {Array.from(
                    { length: totalDashboardPages },
                    (_, index) => index + 1,
                  ).map((pageNumber) => (
                    <a
                      className={pageNumber === dashboardPage ? "active" : ""}
                      href={`/app?page=${pageNumber}#entries`}
                      key={pageNumber}
                    >
                      {pageNumber}
                    </a>
                  ))}

                  {dashboardPage < totalDashboardPages ? (
                    <a href={`/app?page=${dashboardPage + 1}#entries`}>Next</a>
                  ) : (
                    <span className="disabled">Next</span>
                  )}
                </div>
              </div>
            </>
          )}
        </article>

        <aside className="panel">
          <p className="mini-label">Skill Signal</p>
          <h2>Top skills</h2>

          {topTags.length === 0 ? (
            <div className="empty-state small">
              <p>Your top skills will show here after entries load.</p>
            </div>
          ) : (
            <div className="skill-list">
              {topTags.map(([tag, count]) => (
                <div className="skill-row" key={tag}>
                  <span>{tag}</span>
                  <strong>{count}</strong>
                </div>
              ))}
            </div>
          )}
        </aside>
      </section>

      {isProfileModalOpen && (
        <div className="modal-backdrop" onClick={closeProfileModal}>
          <div
            className="modal-card profile-modal-card"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <p className="mini-label">Profile Settings</p>
                <h2>Edit your Proof Profile</h2>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={closeProfileModal}
                aria-label="Close profile editor"
              >
                <X size={18} />
              </button>
            </div>

            <form className="entry-form" onSubmit={handleProfileSubmit}>
              <label>
                Display name
                <input
                  name="name"
                  value={profileForm.name}
                  onChange={handleProfileInputChange}
                  placeholder="Tee"
                  maxLength={80}
                  required
                />
              </label>

              <label>
                Professional headline
                <input
                  name="headline"
                  value={profileForm.headline}
                  onChange={handleProfileInputChange}
                  placeholder="Docker support engineer and backend developer"
                  maxLength={120}
                />
              </label>

              <label>
                About you
                <textarea
                  name="bio"
                  value={profileForm.bio}
                  onChange={handleProfileInputChange}
                  placeholder="Share a short professional introduction."
                  maxLength={500}
                />
              </label>

              <label>
                Location
                <input
                  name="location"
                  value={profileForm.location}
                  onChange={handleProfileInputChange}
                  placeholder="Atlanta, Georgia"
                  maxLength={100}
                />
              </label>

              <label>
                GitHub URL
                <input
                  type="url"
                  name="github_url"
                  value={profileForm.github_url}
                  onChange={handleProfileInputChange}
                  placeholder="https://github.com/username"
                />
              </label>

              <label>
                Portfolio URL
                <input
                  type="url"
                  name="portfolio_url"
                  value={profileForm.portfolio_url}
                  onChange={handleProfileInputChange}
                  placeholder="https://yourportfolio.com"
                />
              </label>

              <label>
                Résumé URL
                <input
                  type="url"
                  name="resume_url"
                  value={profileForm.resume_url}
                  onChange={handleProfileInputChange}
                  placeholder="https://example.com/resume"
                />
              </label>

              {profileError && (
                <p className="profile-form-error">{profileError}</p>
              )}

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn secondary"
                  onClick={closeProfileModal}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="btn primary form-button"
                  disabled={isSavingProfile}
                >
                  {isSavingProfile ? "Saving..." : "Save profile"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div
            className="modal-card"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <p className="mini-label">
                  {editingEntryId ? "Edit Proof" : "Create Proof"}
                </p>

                <h2>
                  {editingEntryId ? "Update brag entry" : "Add a new brag entry"}
                </h2>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={closeModal}
                aria-label="Close modal"
              >
                <X size={18} />
              </button>
            </div>

            <form className="entry-form" onSubmit={handleCreateEntry}>
              <div className="form-row">
                <label>
                  Title
                  <input
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="Debugged Docker networking issue"
                    required
                  />
                </label>

                <label>
                  Category
                  <input
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    placeholder="Docker"
                    required
                  />
                </label>
              </div>

              <div className="form-row">
                <label>
                  Entry Date
                  <input
                    type="date"
                    name="entry_date"
                    value={formData.entry_date}
                    onChange={handleInputChange}
                    required
                  />
                </label>

                <label>
                  Entry Type
                  <select
                    name="entry_type"
                    value={formData.entry_type}
                    onChange={handleInputChange}
                    required
                  >
                    {ENTRY_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label>
                Situation
                <textarea
                  name="situation"
                  value={formData.situation}
                  onChange={handleInputChange}
                  placeholder="What was happening?"
                  required
                />
              </label>

              <label>
                Action
                <textarea
                  name="action"
                  value={formData.action}
                  onChange={handleInputChange}
                  placeholder="What did you do?"
                  required
                />
              </label>

              <label>
                Impact
                <textarea
                  name="impact"
                  value={formData.impact}
                  onChange={handleInputChange}
                  placeholder="What changed because of your work?"
                  required
                />
              </label>

              <label>
                Lesson
                <input
                  name="lesson"
                  value={formData.lesson}
                  onChange={handleInputChange}
                  placeholder="What did you learn?"
                />
              </label>

              <label>
                Tags
                <input
                  name="tags"
                  value={formData.tags}
                  onChange={handleInputChange}
                  placeholder="Docker, FastAPI, MongoDB"
                />
              </label>

              <label className="visibility-toggle">
                <span>Show this entry on my Proof Profile</span>

                <input
                  type="checkbox"
                  name="is_public"
                  checked={formData.is_public}
                  onChange={handleInputChange}
                />
              </label>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn secondary"
                  onClick={closeModal}
                >
                  Cancel
                </button>

                <button
                  className="btn primary form-button"
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting
                    ? "Saving..."
                    : editingEntryId
                      ? "Update entry"
                      : "Save brag entry"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

export default App;
