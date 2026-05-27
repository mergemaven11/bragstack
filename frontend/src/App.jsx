import { useEffect, useState } from "react";
import {
  getCategoriesSummary,
  getEntries,
  getTagsSummary,
  getWeeklyReport,
} from "./api";
import "./App.css";

function App() {
  const [entries, setEntries] = useState([]);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [tagsSummary, setTagsSummary] = useState(null);
  const [categoriesSummary, setCategoriesSummary] = useState(null);
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
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

    loadDashboard();
  }, []);

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
            Docker support engineer, backend builder, and SaaS founder-in-progress.
          </p>

          <div className="proof-links">
            <a href="#" aria-label="Resume link">
              Resume <span>Coming soon</span>
            </a>
            <a href="#" aria-label="Portfolio link">
              Portfolio <span>Coming soon</span>
            </a>
            <a href="#" aria-label="GitHub link">
              GitHub <span>Coming soon</span>
            </a>
          </div>
        </aside>
      </section>

      {isOffline && (
        <section className="notice">
          <strong>Preview mode</strong>
          <span>
            Connect the backend to load your live BragStack entries.
          </span>
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
                  <div>
                    <p className="mini-label">{entry.category}</p>
                    <h3>{entry.title}</h3>
                    <p>{entry.resume_bullet}</p>
                  </div>

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
    </main>
  );
}

export default App;