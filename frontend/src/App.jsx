import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2, X } from "lucide-react";
import {
  createEntry,
  deleteEntry,
  getCategoriesSummary,
  getEntries,
  getTagsSummary,
  getWeeklyReport,
  updateEntry,
} from "./api";
import "./App.css";

function App() {
  const [entries, setEntries] = useState([]);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [tagsSummary, setTagsSummary] = useState(null);
  const [categoriesSummary, setCategoriesSummary] = useState(null);
  const [isOffline, setIsOffline] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEntryId, setEditingEntryId] = useState(null);

  const [formData, setFormData] = useState({
    title: "",
    category: "",
    situation: "",
    action: "",
    impact: "",
    lesson: "",
    tags: "",
  });

  async function loadDashboard() {
    try {
      const [entriesData, weeklyData, tagsData, categoriesData] =
        await Promise.all([
          getEntries(),
          getWeeklyReport(),
          getTagsSummary(),
          getCategoriesSummary(),
        ]);

      setEntries(entriesData.entries ?? []);
      setWeeklyReport(weeklyData);
      setTagsSummary(tagsData);
      setCategoriesSummary(categoriesData);
      setIsOffline(false);
    } catch (err) {
      console.error(err);
      setIsOffline(true);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  function openCreateModal() {
    setEditingEntryId(null);
    setFormData({
      title: "",
      category: "",
      situation: "",
      action: "",
      impact: "",
      lesson: "",
      tags: "",
    });
    setIsModalOpen(true);
  }

  function openEditModal(entry) {
    setEditingEntryId(entry.id);
    setFormData({
      title: entry.title ?? "",
      category: entry.category ?? "",
      situation: entry.situation ?? "",
      action: entry.action ?? "",
      impact: entry.impact ?? "",
      lesson: entry.lesson ?? "",
      tags: entry.tags?.join(", ") ?? "",
    });
    setIsModalOpen(true);
  }

  function closeModal() {
    setIsModalOpen(false);
    setEditingEntryId(null);
  }

  function handleInputChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
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

      setFormData({
        title: "",
        category: "",
        situation: "",
        action: "",
        impact: "",
        lesson: "",
        tags: "",
      });

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
          <p className="mini-label">Public Proof Card</p>

          <div className="avatar">T</div>

          <h2>Tee’s BragStack</h2>
          <p>
            Docker support engineer, backend builder, and SaaS
            founder-in-progress.
          </p>

          <div className="proof-links">
            <a href="#" aria-label="Resume link">
              Resume <span>Coming soon</span>
            </a>
            <a href="#" aria-label="Portfolio link">
              Portfolio <span>Coming soon</span>
            </a>
            <a
              href="https://github.com/mergemaven11/bragstack"
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub link"
            >
              GitHub <span>Repo</span>
            </a>
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

        <button className="btn primary icon-btn" onClick={openCreateModal}>
          <Plus size={18} />
          New Entry
        </button>
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
                      <p className="mini-label">{entry.category}</p>
                      <h3>{entry.title}</h3>
                    </div>

                    <div className="entry-actions">
                      <button
                        type="button"
                        className="icon-action"
                        onClick={() => openEditModal(entry)}
                        aria-label="Edit entry"
                      >
                        <Pencil size={16} />
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

              <div className="modal-footer">
                <button type="button" className="btn secondary" onClick={closeModal}>
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
