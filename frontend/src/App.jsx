import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2, X } from "lucide-react";

import AuthPage from "./AuthPage";
import PublicBragPage from "./PublicBragPage";
import LandingPage from "./LandingPage";

import {
  createEntry,
  deleteEntry,
  getCategoriesSummary,
  getCurrentUser,
  getEntries,
  getTagsSummary,
  getWeeklyReport,
  loginUser,
  registerUser,
  updateEntry,
  updateCurrentUserProfile,
} from "./api";
import "./App.css";

const ENTRY_TYPES = [
  "Current Job",
  "Previous Job",
  "Personal Development",
  "Side Project",
  "Open Source",
  "Learning / Certification",
];

const getTodayDate = () => new Date().toISOString().slice(0, 10);

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

  async function loadDashboard() {
    try {
      const [userData, entriesData, weeklyData, tagsData, categoriesData] =
        await Promise.all([
          getCurrentUser(),
          getEntries(),
          getWeeklyReport(),
          getTagsSummary(),
          getCategoriesSummary(),
        ]);

      setCurrentUser(userData);
      setEntries(entriesData.entries ?? []);
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
      const updatedUser =
        await updateCurrentUserProfile(profileForm);

      setCurrentUser(updatedUser);
      closeProfileModal();
    } catch (error) {
      console.error(error);

      setProfileError(
        error.response?.data?.detail ??
        "Your profile could not be saved."
      );
    } finally {
      setIsSavingProfile(false);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("bragstack_token");

    if (isLandingPage || isPublicPage || isLoginPage || isRegisterPage) {
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
  }, [isLandingPage, isPublicPage, isLoginPage, isRegisterPage]);

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

  const topTags = tagsSummary?.tags ? Object.entries(tagsSummary.tags) : [];


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

  const token = localStorage.getItem("bragstack_token");

  if (!token) {
    return null;
  }

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
            <p className="mini-label">Public Proof Card</p>

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

          {currentUser?.bio && (
            <p className="profile-bio">{currentUser.bio}</p>
          )}

          {currentUser?.location && (
            <p className="profile-location">
              {currentUser.location}
            </p>
          )}

          <div className="proof-links">
            {currentUser?.public_slug && (
              <a
                href={`/brag/${currentUser.public_slug}`}
                target="_blank"
                rel="noreferrer"
              >
                Public BragStack <span>View profile</span>
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
          <strong>Preview mode</strong>
          <span>Please contact support.</span>
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

          <button className="btn primary icon-btn" onClick={openCreateModal}>
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
                Once your backend is connected, your technical wins will appear
                here as resume-ready proof.
              </p>
            </div>
          ) : (
            <div className="entry-list">
              {entries.map((entry) => (
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
                        className={`visibility-badge ${entry.is_public ? "public" : "private"
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
                </article>
              ))}
            </div>
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
  <div
    className="modal-backdrop"
    onClick={closeProfileModal}
  >
    <div
      className="modal-card profile-modal-card"
      onClick={(event) => event.stopPropagation()}
    >
      <div className="modal-header">
        <div>
          <p className="mini-label">Profile Settings</p>
          <h2>Edit your public profile</h2>
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

      <form
        className="entry-form"
        onSubmit={handleProfileSubmit}
      >
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
          <p className="profile-form-error">
            {profileError}
          </p>
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
            {isSavingProfile
              ? "Saving..."
              : "Save profile"}
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
            {editingEntryId
              ? "Update brag entry"
              : "Add a new brag entry"}
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

      <form
        className="entry-form"
        onSubmit={handleCreateEntry}
      >
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
          <span>
            Show this entry on my public BragStack
          </span>

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