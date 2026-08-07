import { useEffect, useMemo, useState } from "react";
import { ExternalLink, Search } from "lucide-react";
import {
  getPublicCategoriesSummary,
  getPublicEntries,
  getPublicImpactReceipts,
  getPublicProfile,
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

function formatSignal(value = "") {
  return value
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function PublicBragPage() {
  const [profile, setProfile] = useState(null);
  const [entries, setEntries] = useState([]);
  const [impactReceipts, setImpactReceipts] = useState([]);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [tagsSummary, setTagsSummary] = useState(null);
  const [categoriesSummary, setCategoriesSummary] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");
  const [isOffline, setIsOffline] = useState(false);

  const publicSlug = useMemo(() => {
    const [, page, slug] = window.location.pathname.split("/");
    return page === "brag" ? slug : undefined;
  }, []);

  useEffect(() => {
    async function loadPublicPage() {
      try {
        const [
          profileData,
          entriesData,
          receiptsData,
          weeklyData,
          tagsData,
          categoriesData,
        ] = await Promise.all([
          getPublicProfile(publicSlug),
          getPublicEntries(publicSlug),
          getPublicImpactReceipts(publicSlug),
          getPublicWeeklyReport(publicSlug),
          getPublicTagsSummary(publicSlug),
          getPublicCategoriesSummary(publicSlug),
        ]);

        setProfile(profileData.profile ?? null);
        setEntries(entriesData.entries || []);
        setImpactReceipts(receiptsData.receipts || []);
        setWeeklyReport(weeklyData);
        setTagsSummary(tagsData);
        setCategoriesSummary(categoriesData);
        setIsOffline(false);
      } catch (err) {
        console.error("Failed to load public BragStack page:", err);
        setIsOffline(true);
      }
    }

    void loadPublicPage();
  }, [publicSlug]);

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
  const displayName = profile?.name || "BragStack member";
  const avatarLetter = displayName.charAt(0).toUpperCase() || "B";

  return (
    <main className="public-page">
      <section className="public-hero">
        <div>
          <p className="mini-label">Public BragStack</p>
          <h1>{displayName}&apos;s Career Proof Timeline</h1>
          <p>
            {profile?.bio ||
              "A searchable record of accomplishments, skill growth, and career proof."}
          </p>

          <div className="public-actions">
            {profile?.github_url && (
              <a
                href={profile.github_url}
                target="_blank"
                rel="noreferrer"
                className="public-button primary"
              >
                <ExternalLink size={17} />
                GitHub
              </a>
            )}

            {profile?.portfolio_url && (
              <a
                href={profile.portfolio_url}
                target="_blank"
                rel="noreferrer"
                className="public-button secondary"
              >
                <ExternalLink size={17} />
                Portfolio
              </a>
            )}

            {profile?.resume_url && (
              <a
                href={profile.resume_url}
                target="_blank"
                rel="noreferrer"
                className="public-button secondary"
              >
                <ExternalLink size={17} />
                Résumé
              </a>
            )}

            <a href="/" className="public-button secondary">
              BragStack
            </a>
          </div>
        </div>

        <aside className="public-proof-card">
          <div className="avatar">{avatarLetter}</div>
          <h2>{profile?.headline || displayName}</h2>

          {(profile?.location || profile?.bio) && (
            <p>
              {[profile?.location, profile?.bio]
                .filter(Boolean)
                .join(" • ")}
            </p>
          )}

          <div className="public-stat-list">
            <span>{entries.length} total entries</span>
            <span>{impactReceipts.length} public receipts</span>
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
          <strong>Unable to load profile</strong>
          <span>Public BragStack data could not be loaded right now.</span>
        </section>
      )}

      <section className="public-controls">
        <div className="search-box">
          <Search size={18} />
          <input
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search skills, projects, categories, and results..."
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
          {impactReceipts.length > 0 && (
            <>
              <div className="timeline-header">
                <div>
                  <p className="mini-label">Verified Structure</p>
                  <h2>Public Impact Receipts</h2>
                </div>

                <span>{impactReceipts.length} receipts</span>
              </div>

              {impactReceipts.map((receipt) => (
                <article className="public-entry" key={receipt.id}>
                  <div className="public-entry-top">
                    <div>
                      <p className="mini-label">Impact Receipt</p>
                      <h3>{receipt.accomplishment}</h3>
                    </div>

                    <div className="public-entry-meta">
                      {receipt.trust_signals?.map((signal) => (
                        <span key={`${receipt.id}-${signal}`}>
                          {formatSignal(signal)}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="proof-grid">
                    <div>
                      <strong>Contribution</strong>
                      <p>{receipt.contribution}</p>
                    </div>

                    <div>
                      <strong>Result</strong>
                      <p>{receipt.result}</p>
                    </div>
                  </div>

                  {receipt.evidence?.length > 0 && (
                    <div className="proof-grid">
                      {receipt.evidence.map((item, index) => (
                        <div key={`${receipt.id}-evidence-${index}`}>
                          <strong>{item.title}</strong>
                          <p>{item.description || item.reference}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="tags">
                    {receipt.skills?.map((skill) => (
                      <span key={`${receipt.id}-${skill}`}>{skill}</span>
                    ))}
                  </div>
                </article>
              ))}
            </>
          )}

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
            <p className="mini-label">Profile</p>
            <h2>More proof</h2>

            <div className="proof-links">
              {profile?.github_url && (
                <a href={profile.github_url} target="_blank" rel="noreferrer">
                  GitHub <span>Open</span>
                </a>
              )}

              {profile?.resume_url && (
                <a href={profile.resume_url} target="_blank" rel="noreferrer">
                  Résumé <span>Open</span>
                </a>
              )}

              {profile?.portfolio_url && (
                <a
                  href={profile.portfolio_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Portfolio <span>Visit</span>
                </a>
              )}
            </div>
          </section>
        </aside>
      </section>
    </main>
  );
}

export default PublicBragPage;
