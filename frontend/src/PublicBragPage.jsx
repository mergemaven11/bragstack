import { useEffect, useMemo, useState } from "react";
import {
  ExternalLink,
  MapPin,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import {
  getPublicCategoriesSummary,
  getPublicEntries,
  getPublicImpactReceipts,
  getPublicProfile,
  getPublicTagsSummary,
  getPublicWeeklyReport,
} from "./api";

import "./ProofProfile.css";

const PAGE_SIZE = 4;
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

function searchableEntry(entry) {
  return [
    entry.title,
    entry.category,
    entry.entry_type,
    entry.entry_date,
    entry.resume_bullet,
    entry.situation,
    entry.action,
    entry.impact,
    entry.lesson,
    ...normalizeTags(entry.tags),
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function formatSignal(value = "") {
  return value
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function PublicBragPage() {
  const [profile, setProfile] = useState(null);
  const [entries, setEntries] = useState([]);
  const [entryMeta, setEntryMeta] = useState({
    total_entries: 0,
    activity_last_6_months: [],
  });
  const [impactReceipts, setImpactReceipts] = useState([]);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [tagsSummary, setTagsSummary] = useState(null);
  const [categoriesSummary, setCategoriesSummary] = useState(null);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");
  const [isOffline, setIsOffline] = useState(false);

  const publicSlug = useMemo(() => {
    const [, route, slug] = window.location.pathname.split("/");
    return route === "brag" ? slug : undefined;
  }, []);

  useEffect(() => {
    async function loadProfileData() {
      try {
        const [profileData, receiptsData, weeklyData, tagsData, categoriesData] =
          await Promise.all([
            getPublicProfile(publicSlug),
            getPublicImpactReceipts(publicSlug),
            getPublicWeeklyReport(publicSlug),
            getPublicTagsSummary(publicSlug),
            getPublicCategoriesSummary(publicSlug),
          ]);

        setProfile(profileData.profile ?? null);
        setImpactReceipts(receiptsData.receipts ?? []);
        setWeeklyReport(weeklyData);
        setTagsSummary(tagsData);
        setCategoriesSummary(categoriesData);
        setIsOffline(false);
      } catch (error) {
        console.error("Failed to load Proof Profile:", error);
        setIsOffline(true);
      }
    }

    void loadProfileData();
  }, [publicSlug]);

  useEffect(() => {
    async function loadPage() {
      try {
        const data = await getPublicEntries(
          publicSlug,
          PAGE_SIZE,
          (page - 1) * PAGE_SIZE,
        );
        setEntries(data.entries ?? []);
        setEntryMeta({
          total_entries: data.total_entries ?? 0,
          activity_last_6_months: data.activity_last_6_months ?? [],
        });
        setIsOffline(false);
      } catch (error) {
        console.error("Failed to load Proof Profile entries:", error);
        setIsOffline(true);
      }
    }

    void loadPage();
  }, [publicSlug, page]);

  useEffect(() => {
    setPage(1);
  }, [searchTerm, activeFilter]);

  const filteredEntries = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return entries.filter((entry) => {
      const matchesSearch = !query || searchableEntry(entry).includes(query);
      const matchesFilter =
        activeFilter === "All" || entry.entry_type === activeFilter;
      return matchesSearch && matchesFilter;
    });
  }, [entries, searchTerm, activeFilter]);

  const categories = Object.entries(categoriesSummary?.categories ?? {});
  const tags = Object.entries(tagsSummary?.tags ?? {});
  const maxCategoryCount = Math.max(...categories.map(([, count]) => count), 1);
  const maxActivity = Math.max(
    ...entryMeta.activity_last_6_months.map((item) => item.count),
    1,
  );

  const evidenceCount = impactReceipts.reduce(
    (total, receipt) => total + (receipt.evidence?.length ?? 0),
    0,
  );
  const evidenceLinked = impactReceipts.filter((receipt) =>
    receipt.trust_signals?.includes("evidence-linked"),
  ).length;
  const receiptCoverage = entryMeta.total_entries
    ? Math.min(
        100,
        Math.round((impactReceipts.length / entryMeta.total_entries) * 100),
      )
    : 0;
  const evidenceCoverage = impactReceipts.length
    ? Math.round((evidenceLinked / impactReceipts.length) * 100)
    : 0;

  const displayName = profile?.name || "BragStack member";
  const avatarLetter = displayName.charAt(0).toUpperCase() || "B";
  const totalPages = Math.max(
    1,
    Math.ceil(entryMeta.total_entries / PAGE_SIZE),
  );
  const start = entryMeta.total_entries
    ? (page - 1) * PAGE_SIZE + 1
    : 0;
  const end = Math.min(page * PAGE_SIZE, entryMeta.total_entries);

  return (
    <main className="proof-profile">
      <div className="proof-profile-inner">
        <header className="proof-topbar">
          <a className="proof-brand" href="/">
            <span className="proof-brand-mark">B</span>
            <span>BragStack</span>
          </a>
          <span className="proof-topbar-tag">Proof Profile</span>
        </header>

        <section className="proof-hero">
          <div>
            <p className="proof-eyebrow">Proof Profile</p>
            <h1>
              Career proof,
              <span>not just claims.</span>
            </h1>
            <p className="proof-headline">
              {profile?.headline || `${displayName}'s evidence-backed career story`}
            </p>
            <p className="proof-bio">
              {profile?.bio ||
                "A living record of accomplishments, demonstrated skills, and evidence-backed impact."}
            </p>

            {profile?.location && (
              <p className="proof-location">
                <MapPin size={15} /> {profile.location}
              </p>
            )}

            <div className="proof-actions">
              {profile?.github_url && (
                <a
                  className="proof-action primary"
                  href={profile.github_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  GitHub <ExternalLink size={15} />
                </a>
              )}
              {profile?.portfolio_url && (
                <a
                  className="proof-action"
                  href={profile.portfolio_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Portfolio <ExternalLink size={15} />
                </a>
              )}
              {profile?.resume_url && (
                <a
                  className="proof-action"
                  href={profile.resume_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Résumé <ExternalLink size={15} />
                </a>
              )}
            </div>
          </div>

          <aside className="proof-scorecard">
            <div>
              <div className="proof-avatar">{avatarLetter}</div>
              <h2>{displayName}</h2>
            </div>
            <div className="proof-score-grid">
              <article>
                <strong>{entryMeta.total_entries}</strong>
                <span>public wins</span>
              </article>
              <article>
                <strong>{impactReceipts.length}</strong>
                <span>Impact Receipts</span>
              </article>
              <article>
                <strong>{tagsSummary?.total_unique_tags ?? 0}</strong>
                <span>skills shown</span>
              </article>
              <article>
                <strong>{weeklyReport?.total_entries ?? 0}</strong>
                <span>this week</span>
              </article>
            </div>
          </aside>
        </section>

        {isOffline && (
          <section className="proof-section">
            <div className="proof-error">
              Proof Profile data could not be loaded right now.
            </div>
          </section>
        )}

        {!isOffline && entryMeta.total_entries > 0 && (
          <section className="proof-section">
            <div className="proof-section-heading">
              <div>
                <p className="proof-eyebrow">Career signal</p>
                <h2>Impact at a glance</h2>
                <p>
                  A visual summary of the evidence behind this career story.
                </p>
              </div>
              <span className="proof-live-badge">
                <Sparkles size={14} /> Live from public proof
              </span>
            </div>

            <div className="proof-kpi-grid">
              <article className="proof-kpi">
                <span>Receipt coverage</span>
                <strong>{receiptCoverage}%</strong>
                <small>
                  {impactReceipts.length} of {entryMeta.total_entries} wins packaged as receipts
                </small>
              </article>
              <article className="proof-kpi">
                <span>Evidence-linked</span>
                <strong>{evidenceCoverage}%</strong>
                <small>{evidenceCount} public evidence items</small>
              </article>
              <article className="proof-kpi">
                <span>Skill breadth</span>
                <strong>{tagsSummary?.total_unique_tags ?? 0}</strong>
                <small>distinct demonstrated skills</small>
              </article>
            </div>

            <div className="proof-analytics-grid">
              <article className="proof-chart-card">
                <h3>Accomplishment momentum · last 6 months</h3>
                <div className="proof-activity">
                  {entryMeta.activity_last_6_months.map((item) => (
                    <div className="proof-activity-item" key={item.key}>
                      <div className="proof-activity-bar-wrap">
                        <span
                          className="proof-activity-bar"
                          style={{
                            height: `${Math.max(
                              8,
                              (item.count / maxActivity) * 100,
                            )}%`,
                          }}
                          title={`${item.count} accomplishments`}
                        />
                      </div>
                      <span>{item.label}</span>
                    </div>
                  ))}
                </div>
              </article>

              <article className="proof-chart-card">
                <h3>Proof by category</h3>
                <div className="proof-bars">
                  {categories.slice(0, 7).map(([category, count]) => (
                    <div className="proof-bar-row" key={category}>
                      <div className="proof-bar-label">
                        <span>{category}</span>
                        <strong>{count}</strong>
                      </div>
                      <div className="proof-bar-track">
                        <span
                          style={{
                            width: `${Math.max(
                              8,
                              (count / maxCategoryCount) * 100,
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </article>
            </div>
          </section>
        )}

        {impactReceipts.length > 0 && (
          <section className="proof-section">
            <div className="proof-section-heading">
              <div>
                <p className="proof-eyebrow">Featured proof</p>
                <h2>Impact Receipts</h2>
                <p>
                  Structured proof of contribution, result, skills, and evidence.
                </p>
              </div>
              <span className="proof-live-badge">
                <ShieldCheck size={14} /> {impactReceipts.length} public
              </span>
            </div>

            <div className="proof-receipt-grid">
              {impactReceipts.slice(0, 4).map((receipt) => (
                <article className="proof-receipt" key={receipt.id}>
                  <p className="proof-eyebrow">Impact Receipt</p>
                  <h3>{receipt.accomplishment}</h3>
                  <div className="proof-receipt-block">
                    <span>Contribution</span>
                    <p>{receipt.contribution}</p>
                  </div>
                  <div className="proof-receipt-block">
                    <span>Result</span>
                    <p>{receipt.result}</p>
                  </div>
                  <div className="proof-chips">
                    {receipt.trust_signals?.map((signal) => (
                      <span key={`${receipt.id}-${signal}`}>
                        {formatSignal(signal)}
                      </span>
                    ))}
                    {receipt.skills?.slice(0, 4).map((skill) => (
                      <span key={`${receipt.id}-${skill}`}>{skill}</span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        <section className="proof-section">
          <div className="proof-section-heading">
            <div>
              <p className="proof-eyebrow">Evidence library</p>
              <h2>Explore the work</h2>
              <p>
                Search the action, impact, projects, skills, and lessons behind the profile.
              </p>
            </div>
          </div>

          <div className="proof-controls">
            <div className="proof-search">
              <Search size={17} />
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Search this page by skill, action, impact, or project..."
              />
            </div>
            <div className="proof-filter-row">
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
          </div>

          {filteredEntries.length === 0 ? (
            <div className="proof-empty">
              No matching proof on this page. Try another filter or page.
            </div>
          ) : (
            <div className="proof-entry-grid">
              {filteredEntries.map((entry) => (
                <article className="proof-entry-card" key={entry.id}>
                  <div>
                    <p className="proof-eyebrow">{entry.category || "General"}</p>
                    <h3>{entry.title}</h3>
                  </div>
                  <div className="proof-entry-meta">
                    <span>{entry.entry_type || "General"}</span>
                    <span>{entry.entry_date || "No date"}</span>
                  </div>
                  <div className="proof-entry-impact">
                    <strong>Impact</strong>
                    <p>{entry.impact || entry.resume_bullet}</p>
                  </div>
                  <div className="proof-entry-details">
                    <div>
                      <strong>Action</strong>
                      <p>{entry.action || "No action added."}</p>
                    </div>
                    <div>
                      <strong>Situation</strong>
                      <p>{entry.situation || "No situation added."}</p>
                    </div>
                  </div>
                  <div className="proof-chips">
                    {normalizeTags(entry.tags).map((tag) => (
                      <span key={`${entry.id}-${tag}`}>{tag}</span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          )}

          <div className="proof-pagination">
            <span className="proof-pagination-summary">
              Showing {start}–{end} of {entryMeta.total_entries} public wins · Page {page} of {totalPages}
            </span>
            <div className="proof-pagination-controls">
              <button
                type="button"
                disabled={page === 1}
                onClick={() => setPage((current) => Math.max(1, current - 1))}
              >
                Previous
              </button>
              {Array.from({ length: totalPages }, (_, index) => index + 1).map(
                (pageNumber) => (
                  <button
                    type="button"
                    className={pageNumber === page ? "active" : ""}
                    key={pageNumber}
                    onClick={() => setPage(pageNumber)}
                  >
                    {pageNumber}
                  </button>
                ),
              )}
              <button
                type="button"
                disabled={page === totalPages}
                onClick={() =>
                  setPage((current) => Math.min(totalPages, current + 1))
                }
              >
                Next
              </button>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

export default PublicBragPage;
