import { useEffect, useMemo, useState } from "react";
import { BarChart3, ExternalLink, Search, ShieldCheck, Sparkles } from "lucide-react";
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
  if (Array.isArray(tags)) return tags;
  if (typeof tags === "string") {
    return tags.split(",").map((tag) => tag.trim()).filter(Boolean);
  }
  return [];
}

function safeText(value) {
  if (value === null || value === undefined) return "";
  return String(value);
}

function formatSignal(value = "") {
  return value
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function buildMonthlyActivity(entries) {
  const now = new Date();
  const buckets = Array.from({ length: 6 }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (5 - index), 1);
    return {
      key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`,
      label: date.toLocaleDateString(undefined, { month: "short" }),
      count: 0,
    };
  });

  const indexByKey = Object.fromEntries(buckets.map((bucket, index) => [bucket.key, index]));

  entries.forEach((entry) => {
    if (!entry.entry_date) return;
    const date = new Date(`${entry.entry_date}T00:00:00`);
    if (Number.isNaN(date.getTime())) return;
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
    const index = indexByKey[key];
    if (index !== undefined) buckets[index].count += 1;
  });

  return buckets;
}

function ActivityChart({ data }) {
  const max = Math.max(...data.map((item) => item.count), 1);
  const points = data.map((item, index) => {
    const x = data.length === 1 ? 50 : (index / (data.length - 1)) * 100;
    const y = 82 - (item.count / max) * 58;
    return { ...item, x, y };
  });

  return (
    <div className="activity-chart" aria-label="Accomplishment activity over six months">
      <svg viewBox="0 0 100 92" preserveAspectRatio="none" role="img">
        <defs>
          <linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.42" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          className="activity-area"
          d={`M 0 82 ${points.map((point) => `L ${point.x} ${point.y}`).join(" ")} L 100 82 Z`}
        />
        <polyline
          className="activity-line"
          points={points.map((point) => `${point.x},${point.y}`).join(" ")}
        />
        {points.map((point) => (
          <circle key={point.key} cx={point.x} cy={point.y} r="1.8" className="activity-dot" />
        ))}
      </svg>
      <div className="activity-labels">
        {points.map((point) => (
          <span key={point.key} title={`${point.count} accomplishment${point.count === 1 ? "" : "s"}`}>
            {point.label}
          </span>
        ))}
      </div>
    </div>
  );
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
        const [profileData, entriesData, receiptsData, weeklyData, tagsData, categoriesData] =
          await Promise.all([
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
      const matchesFilter = activeFilter === "All" || entry.entry_type === activeFilter;
      return matchesSearch && matchesFilter;
    });
  }, [entries, searchTerm, activeFilter]);

  const analytics = useMemo(() => {
    const categories = Object.entries(categoriesSummary?.categories || {});
    const tags = Object.entries(tagsSummary?.tags || {});
    const evidenceCount = impactReceipts.reduce(
      (total, receipt) => total + (receipt.evidence?.length || 0),
      0
    );
    const evidenceLinked = impactReceipts.filter((receipt) =>
      receipt.trust_signals?.includes("evidence-linked")
    ).length;
    const receiptCoverage = entries.length
      ? Math.min(100, Math.round((impactReceipts.length / entries.length) * 100))
      : 0;
    const evidenceCoverage = impactReceipts.length
      ? Math.round((evidenceLinked / impactReceipts.length) * 100)
      : 0;

    return {
      categories,
      tags,
      evidenceCount,
      receiptCoverage,
      evidenceCoverage,
      monthlyActivity: buildMonthlyActivity(entries),
    };
  }, [entries, impactReceipts, tagsSummary, categoriesSummary]);

  const topTags = analytics.tags;
  const maxCategoryCount = Math.max(...analytics.categories.map(([, count]) => count), 1);
  const maxSkillCount = Math.max(...topTags.map(([, count]) => count), 1);
  const displayName = profile?.name || "BragStack member";
  const avatarLetter = displayName.charAt(0).toUpperCase() || "B";

  return (
    <main className="public-page">
      <section className="public-hero">
        <div>
          <p className="mini-label">Public BragStack</p>
          <h1>{displayName}&apos;s Career Proof Timeline</h1>
          <p>
            {profile?.bio || "A searchable record of accomplishments, skill growth, and career proof."}
          </p>

          <div className="public-actions">
            {profile?.github_url && (
              <a href={profile.github_url} target="_blank" rel="noreferrer" className="public-button primary">
                <ExternalLink size={17} /> GitHub
              </a>
            )}
            {profile?.portfolio_url && (
              <a href={profile.portfolio_url} target="_blank" rel="noreferrer" className="public-button secondary">
                <ExternalLink size={17} /> Portfolio
              </a>
            )}
            {profile?.resume_url && (
              <a href={profile.resume_url} target="_blank" rel="noreferrer" className="public-button secondary">
                <ExternalLink size={17} /> Résumé
              </a>
            )}
            <a href="/" className="public-button secondary">BragStack</a>
          </div>
        </div>

        <aside className="public-proof-card">
          <div className="avatar">{avatarLetter}</div>
          <h2>{profile?.headline || displayName}</h2>
          {(profile?.location || profile?.bio) && (
            <p>{[profile?.location, profile?.bio].filter(Boolean).join(" • ")}</p>
          )}
          <div className="public-stat-list">
            <span>{entries.length} total entries</span>
            <span>{impactReceipts.length} public receipts</span>
            <span>{weeklyReport?.total_entries ?? 0} this week</span>
            <span>{tagsSummary?.total_unique_tags ?? 0} skill tags</span>
            <span>{categoriesSummary?.total_unique_categories ?? 0} categories</span>
          </div>
        </aside>
      </section>

      {!isOffline && entries.length > 0 && (
        <section className="analytics-shell">
          <div className="analytics-heading">
            <div>
              <p className="mini-label">Career Analytics</p>
              <h2>Impact at a glance</h2>
              <p>Public accomplishments transformed into a visual career signal.</p>
            </div>
            <div className="analytics-badge"><Sparkles size={16} /> Live from public proof</div>
          </div>

          <div className="analytics-kpis">
            <article className="analytics-kpi">
              <BarChart3 size={19} />
              <span>Receipt coverage</span>
              <strong>{analytics.receiptCoverage}%</strong>
              <small>{impactReceipts.length} of {entries.length} public wins have receipts</small>
            </article>
            <article className="analytics-kpi">
              <ShieldCheck size={19} />
              <span>Evidence-linked</span>
              <strong>{analytics.evidenceCoverage}%</strong>
              <small>{analytics.evidenceCount} public evidence item{analytics.evidenceCount === 1 ? "" : "s"}</small>
            </article>
            <article className="analytics-kpi">
              <Sparkles size={19} />
              <span>Skill breadth</span>
              <strong>{tagsSummary?.total_unique_tags ?? 0}</strong>
              <small>distinct skills demonstrated publicly</small>
            </article>
          </div>

          <div className="analytics-grid">
            <article className="chart-card activity-card">
              <div className="chart-card-heading">
                <div>
                  <p className="mini-label">Momentum</p>
                  <h3>Accomplishment activity</h3>
                </div>
                <span>Last 6 months</span>
              </div>
              <ActivityChart data={analytics.monthlyActivity} />
            </article>

            <article className="chart-card">
              <div className="chart-card-heading">
                <div>
                  <p className="mini-label">Impact Mix</p>
                  <h3>Proof by category</h3>
                </div>
                <span>{analytics.categories.length} areas</span>
              </div>
              <div className="bar-chart-list">
                {analytics.categories.slice(0, 7).map(([category, count]) => (
                  <div className="bar-chart-row" key={category}>
                    <div className="bar-chart-label"><span>{category}</span><strong>{count}</strong></div>
                    <div className="bar-chart-track">
                      <span style={{ width: `${Math.max(8, (count / maxCategoryCount) * 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="chart-card skills-chart-card">
              <div className="chart-card-heading">
                <div>
                  <p className="mini-label">Skills</p>
                  <h3>Most demonstrated skills</h3>
                </div>
                <span>Public proof</span>
              </div>
              <div className="skill-bar-grid">
                {topTags.slice(0, 8).map(([tag, count]) => (
                  <div className="skill-bar" key={tag}>
                    <div className="skill-bar-top"><span>{tag}</span><strong>{count}</strong></div>
                    <div className="skill-bar-track">
                      <span style={{ width: `${Math.max(8, (count / maxSkillCount) * 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>
      )}

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
                <div><p className="mini-label">Verified Structure</p><h2>Public Impact Receipts</h2></div>
                <span>{impactReceipts.length} receipts</span>
              </div>
              {impactReceipts.map((receipt) => (
                <article className="public-entry" key={receipt.id}>
                  <div className="public-entry-top">
                    <div><p className="mini-label">Impact Receipt</p><h3>{receipt.accomplishment}</h3></div>
                    <div className="public-entry-meta">
                      {receipt.trust_signals?.map((signal) => (
                        <span key={`${receipt.id}-${signal}`}>{formatSignal(signal)}</span>
                      ))}
                    </div>
                  </div>
                  <div className="proof-grid">
                    <div><strong>Contribution</strong><p>{receipt.contribution}</p></div>
                    <div><strong>Result</strong><p>{receipt.result}</p></div>
                  </div>
                  {receipt.evidence?.length > 0 && (
                    <div className="proof-grid">
                      {receipt.evidence.map((item, index) => (
                        <div key={`${receipt.id}-evidence-${index}`}><strong>{item.title}</strong><p>{item.description || item.reference}</p></div>
                      ))}
                    </div>
                  )}
                  <div className="tags">
                    {receipt.skills?.map((skill) => <span key={`${receipt.id}-${skill}`}>{skill}</span>)}
                  </div>
                </article>
              ))}
            </>
          )}

          <div className="timeline-header">
            <div><p className="mini-label">Career Evidence</p><h2>Readable proof entries</h2></div>
            <span>{filteredEntries.length} results</span>
          </div>

          {filteredEntries.length === 0 ? (
            <div className="public-empty"><h3>No matching entries found.</h3><p>Try searching a different skill or clearing the filters.</p></div>
          ) : (
            filteredEntries.map((entry) => {
              const tags = normalizeTags(entry.tags);
              return (
                <article className="public-entry" key={entry.id}>
                  <div className="public-entry-top">
                    <div><p className="mini-label">{entry.category ?? "General"}</p><h3>{entry.title ?? "Untitled entry"}</h3></div>
                    <div className="public-entry-meta"><span>{entry.entry_type ?? "General"}</span><span>{entry.entry_date ?? "No date"}</span></div>
                  </div>
                  <p className="public-bullet">{entry.resume_bullet ?? "No resume bullet generated yet."}</p>
                  <div className="proof-grid">
                    <div><strong>Situation</strong><p>{entry.situation ?? "No situation added."}</p></div>
                    <div><strong>Action</strong><p>{entry.action ?? "No action added."}</p></div>
                    <div><strong>Impact</strong><p>{entry.impact ?? "No impact added."}</p></div>
                    {entry.lesson && <div><strong>Lesson</strong><p>{entry.lesson}</p></div>}
                  </div>
                  <div className="tags">{tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
                </article>
              );
            })
          )}
        </section>

        <aside className="public-sidebar">
          <section className="sidebar-card">
            <p className="mini-label">Top Skills</p><h2>Skill signal</h2>
            {topTags.length === 0 ? <p className="muted">No skills found yet.</p> : (
              <div className="skill-list">
                {topTags.slice(0, 8).map(([tag, count]) => (
                  <div className="skill-row" key={tag}><span>{tag}</span><strong>{count}</strong></div>
                ))}
              </div>
            )}
          </section>
          <section className="sidebar-card">
            <p className="mini-label">Profile</p><h2>More proof</h2>
            <div className="proof-links">
              {profile?.github_url && <a href={profile.github_url} target="_blank" rel="noreferrer">GitHub <span>Open</span></a>}
              {profile?.resume_url && <a href={profile.resume_url} target="_blank" rel="noreferrer">Résumé <span>Open</span></a>}
              {profile?.portfolio_url && <a href={profile.portfolio_url} target="_blank" rel="noreferrer">Portfolio <span>Visit</span></a>}
            </div>
          </section>
        </aside>
      </section>
    </main>
  );
}

export default PublicBragPage;
