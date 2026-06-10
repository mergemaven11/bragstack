import { useEffect, useMemo, useState } from "react";
import { ExternalLink, Code2, Search } from "lucide-react";
import {
  getPublicCategoriesSummary,
  getPublicEntries,
  getPublicTagsSummary,
  getPublicWeeklyReport,
} from "./api";

import "./PublicBragPage.css";

const FILTERS = [
  "All",
  "Current Job",
  "Previous Job",
  "Personal Development",
  "Side Project",
  "Open Source",
  "Learning / Certification",
];

function normalizeTags(tags) {
  if (Array.isArray(tags)) {
    return tags;
  }

  if (typeof tags === "string") {
    return tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);
  }

  return [];
}

function safeText(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value);
}

function PublicBragPage() {
  const [entries, setEntries] = useState([]);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [tagsSummary, setTagsSummary] = useState(null);
  const [categoriesSummary, setCategoriesSummary] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
  async function loadPublicPage() {
    try {
      const [entriesData, weeklyData, tagsData, categoriesData] =
        await Promise.all([
          getPublicEntries(),
          getPublicWeeklyReport(),
          getPublicTagsSummary(),
          getPublicCategoriesSummary(),
        ]);

      setEntries(entriesData.entries || []);
      setWeeklyReport(weeklyData);
      setTagsSummary(tagsData);
      setCategoriesSummary(categoriesData);
      setIsPreviewMode(false);
    } catch (err) {
      console.error("Failed to load public BragStack page:", err);
      setIsPreviewMode(true);
    }
  }

    loadPublicPage();
  }, []);

  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      const tags = normalizeTags(entry.tags);

      const searchableText = [
        entry.title,
        entry.category,
        entry.entry_type,
        entry.entry_date,
        entry.resume_bullet,
        entry.situation,
        entry.action,
        entry.impact,
        entry.lesson,
        ...tags,
      ]
        .map(safeText)
        .join(" ")
        .toLowerCase();

      const matchesSearch = searchableText.includes(searchTerm.toLowerCase());
      const matchesFilter =
        activeFilter === "All" || entry.entry_type === activeFilter;

      return matchesSearch && matchesFilter;
    });
  }, [entries, searchTerm, activeFilter]);

  const topTags = tagsSummary?.tags ? Object.entries(tagsSummary.tags) : [];

  return (
    <main className="public-page">
      <section className="public-hero">
        <div>
          <p className="mini-label">Public BragStack</p>
          <h1>Tee’s Career Proof Timeline</h1>
          <p>
            A searchable portfolio of technical wins, project progress, skill
            growth, and SaaS-building evidence.
          </p>

          <div className="public-actions">
            <a
              href="https://github.com/mergemaven11/bragstack"
              target="_blank"
              rel="noreferrer"
              className="public-button primary"
            >
              <Code2 size={17} />
              GitHub Repo
            </a>

            <a href="/" className="public-button secondary">
              <ExternalLink size={17} />
              Dashboard
            </a>
          </div>
        </div>

        <aside className="public-proof-card">
          <div className="avatar">T</div>
          <h2>Docker Support Engineer</h2>
          <p>Backend builder • SaaS founder-in-progress • DevOps learner</p>

          <div className="public-stat-list">
            <span>{entries.length} total entries</span>
            <span>{weeklyReport?.total_entries ?? 0} this week</span>
            <span>{tagsSummary?.total_unique_tags ?? 0} skill tags</span>
            <span>
              {categoriesSummary?.total_unique_categories ?? 0} categories
            </span>
          </div>
        </aside>
      </section>

      {isOffline && (
        <section className="public-notice">
          <strong>Preview mode</strong>
          <span>Live BragStack data is not connected right now.</span>
        </section>
      )}

      <section className="public-controls">
        <div className="search-box">
          <Search size={18} />
          <input
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search Docker, React, MongoDB, Kubernetes..."
          />
        </div>

        <div className="filter-pills">
          {FILTERS.map((filter) => (
            <button
              type="button"
              key={filter}
              className={activeFilter === filter ? "active" : ""}
              onClick={() => setActiveFilter(filter)}
            >
              {filter}
            </button>
          ))}
        </div>
      </section>

      <section className="public-layout">
        <section className="public-timeline">
          <div className="timeline-header">
            <div>
              <p className="mini-label">Career Evidence</p>
              <h2>Readable proof entries</h2>
            </div>

            <span>{filteredEntries.length} results</span>
          </div>

          {filteredEntries.length === 0 ? (
            <div className="public-empty">
              <h3>No matching entries found.</h3>
              <p>Try searching a different skill or clearing the filters.</p>
            </div>
          ) : (
            filteredEntries.map((entry) => {
              const tags = normalizeTags(entry.tags);

              return (
                <article className="public-entry" key={entry.id}>
                  <div className="public-entry-top">
                    <div>
                      <p className="mini-label">
                        {entry.category ?? "General"}
                      </p>
                      <h3>{entry.title ?? "Untitled entry"}</h3>
                    </div>

                    <div className="public-entry-meta">
                      <span>{entry.entry_type ?? "General"}</span>
                      <span>{entry.entry_date ?? "No date"}</span>
                    </div>
                  </div>

                  <p className="public-bullet">
                    {entry.resume_bullet ?? "No resume bullet generated yet."}
                  </p>

                  <div className="proof-grid">
                    <div>
                      <strong>Situation</strong>
                      <p>{entry.situation ?? "No situation added."}</p>
                    </div>

                    <div>
                      <strong>Action</strong>
                      <p>{entry.action ?? "No action added."}</p>
                    </div>

                    <div>
                      <strong>Impact</strong>
                      <p>{entry.impact ?? "No impact added."}</p>
                    </div>

                    {entry.lesson && (
                      <div>
                        <strong>Lesson</strong>
                        <p>{entry.lesson}</p>
                      </div>
                    )}
                  </div>

                  <div className="tags">
                    {tags.map((tag) => (
                      <span key={tag}>{tag}</span>
                    ))}
                  </div>
                </article>
              );
            })
          )}
        </section>

        <aside className="public-sidebar">
          <section className="sidebar-card">
            <p className="mini-label">Top Skills</p>
            <h2>Skill signal</h2>

            {topTags.length === 0 ? (
              <p className="muted">No skills found yet.</p>
            ) : (
              <div className="skill-list">
                {topTags.slice(0, 8).map(([tag, count]) => (
                  <div className="skill-row" key={tag}>
                    <span>{tag}</span>
                    <strong>{count}</strong>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="sidebar-card">
            <p className="mini-label">Links</p>
            <h2>More proof</h2>

            <div className="proof-links">
              <a
                href="https://github.com/mergemaven11/bragstack"
                target="_blank"
                rel="noreferrer"
              >
                GitHub <span>Repo</span>
              </a>
              <a href="#">
                Resume <span>Coming soon</span>
              </a>
              <a href="#">
                Portfolio <span>Coming soon</span>
              </a>
            </div>
          </section>
        </aside>
      </section>
    </main>
  );
}

export default PublicBragPage;