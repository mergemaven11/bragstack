import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  CalendarDays,
  FileText,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import {
  getAllTimeCareerReport,
  getCustomCareerReport,
  getWeeklyCareerReport,
} from "./api";
import "./ReportsPage.css";

const REPORT_TYPES = [
  { key: "weekly", label: "Weekly" },
  { key: "all-time", label: "All time" },
  { key: "custom", label: "Custom" },
];

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

function getThirtyDaysAgo() {
  const value = new Date();
  value.setDate(value.getDate() - 30);
  return value.toISOString().slice(0, 10);
}

function formatLabel(value = "") {
  return value
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function ReportsPage() {
  const [activeType, setActiveType] = useState("weekly");
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [startDate, setStartDate] = useState(getThirtyDaysAgo());
  const [endDate, setEndDate] = useState(getToday());

  async function loadReport(type = activeType) {
    const token = localStorage.getItem("bragstack_token");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      let data;

      if (type === "all-time") {
        data = await getAllTimeCareerReport();
      } else if (type === "custom") {
        data = await getCustomCareerReport(startDate, endDate);
      } else {
        data = await getWeeklyCareerReport();
      }

      setReport(data);
    } catch (requestError) {
      console.error(requestError);

      if (requestError.response?.status === 401) {
        localStorage.removeItem("bragstack_token");
        window.location.href = "/login";
        return;
      }

      setError(
        requestError.response?.data?.detail ??
          "The report could not be generated."
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadReport("weekly");
  }, []);

  const topSkills = useMemo(
    () => Object.entries(report?.top_skills ?? {}).slice(0, 8),
    [report]
  );

  const topCategories = useMemo(
    () => Object.entries(report?.categories ?? {}).slice(0, 8),
    [report]
  );

  function handleTypeChange(type) {
    setActiveType(type);

    if (type !== "custom") {
      void loadReport(type);
    }
  }

  function handleCustomSubmit(event) {
    event.preventDefault();
    setActiveType("custom");
    void loadReport("custom");
  }

  const totals = report?.totals ?? {};

  return (
    <main className="reports-page">
      <header className="reports-header">
        <div>
          <a className="reports-back" href="/app">
            <ArrowLeft size={17} />
            Dashboard
          </a>

          <p className="reports-eyebrow">BragStack Reports</p>
          <h1>Turn your proof into a career summary.</h1>
          <p className="reports-intro">
            Review recent work, see your all-time impact, or build a report for
            a specific review period.
          </p>
        </div>

        <button
          type="button"
          className="reports-refresh"
          onClick={() => void loadReport(activeType)}
          disabled={isLoading || activeType === "custom"}
        >
          <RefreshCw size={17} />
          Refresh
        </button>
      </header>

      <section className="reports-tabs" aria-label="Report period">
        {REPORT_TYPES.map((type) => (
          <button
            type="button"
            key={type.key}
            className={activeType === type.key ? "active" : ""}
            onClick={() => handleTypeChange(type.key)}
          >
            {type.label}
          </button>
        ))}
      </section>

      {activeType === "custom" && (
        <form className="custom-report-form" onSubmit={handleCustomSubmit}>
          <label>
            Start date
            <input
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
              required
            />
          </label>

          <label>
            End date
            <input
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
              required
            />
          </label>

          <button type="submit" disabled={isLoading}>
            <CalendarDays size={17} />
            Generate report
          </button>
        </form>
      )}

      {error && <section className="reports-error">{String(error)}</section>}

      {isLoading ? (
        <section className="reports-loading">
          <RefreshCw size={22} />
          <span>Building your report...</span>
        </section>
      ) : report ? (
        <>
          <section className="report-summary-card">
            <div>
              <p className="reports-eyebrow">
                {report.period?.label ?? "Career report"}
              </p>
              <h2>{report.summary}</h2>
              <p>
                Report dates use the date the work happened, not simply the day
                it was added to BragStack.
              </p>
            </div>

            <span className="report-period-badge">
              {report.period?.start_date && report.period?.end_date
                ? `${report.period.start_date} → ${report.period.end_date}`
                : "All recorded work"}
            </span>
          </section>

          <section className="report-metrics">
            <article>
              <FileText size={20} />
              <span>Accomplishments</span>
              <strong>{totals.entries ?? 0}</strong>
            </article>

            <article>
              <Sparkles size={20} />
              <span>Impact Receipts</span>
              <strong>{totals.impact_receipts ?? 0}</strong>
            </article>

            <article>
              <ShieldCheck size={20} />
              <span>Evidence items</span>
              <strong>{totals.evidence_items ?? 0}</strong>
            </article>

            <article>
              <ShieldCheck size={20} />
              <span>Confirmed contributions</span>
              <strong>{totals.confirmed_assertions ?? 0}</strong>
            </article>

            <article>
              <Sparkles size={20} />
              <span>Quantified results</span>
              <strong>{totals.quantified_results ?? 0}</strong>
            </article>

            <article>
              <FileText size={20} />
              <span>Public proof</span>
              <strong>
                {(totals.public_entries ?? 0) +
                  (totals.public_receipts ?? 0)}
              </strong>
            </article>
          </section>

          <section className="report-two-column">
            <article className="report-panel">
              <p className="reports-eyebrow">Skill signal</p>
              <h2>Top skills</h2>

              {topSkills.length === 0 ? (
                <p className="report-muted">No skill data for this period.</p>
              ) : (
                <div className="report-ranked-list">
                  {topSkills.map(([skill, count]) => (
                    <div key={skill}>
                      <span>{skill}</span>
                      <strong>{count}</strong>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="report-panel">
              <p className="reports-eyebrow">Work mix</p>
              <h2>Top categories</h2>

              {topCategories.length === 0 ? (
                <p className="report-muted">No category data for this period.</p>
              ) : (
                <div className="report-ranked-list">
                  {topCategories.map(([category, count]) => (
                    <div key={category}>
                      <span>{category}</span>
                      <strong>{count}</strong>
                    </div>
                  ))}
                </div>
              )}
            </article>
          </section>

          <section className="report-panel report-highlights">
            <div className="report-panel-heading">
              <div>
                <p className="reports-eyebrow">Career proof</p>
                <h2>Highlights</h2>
              </div>
              <span>{report.highlights?.length ?? 0} shown</span>
            </div>

            {report.highlights?.length ? (
              <div className="report-highlight-list">
                {report.highlights.map((highlight) => (
                  <article key={highlight.entry_id}>
                    <div className="report-highlight-top">
                      <div>
                        <p>{highlight.category}</p>
                        <h3>{highlight.title}</h3>
                      </div>

                      <div className="report-highlight-badges">
                        {highlight.has_receipt && <span>Impact Receipt</span>}
                        {highlight.is_public && <span>Public</span>}
                      </div>
                    </div>

                    {highlight.result && <p>{highlight.result}</p>}

                    <div className="report-skill-tags">
                      {highlight.skills?.map((skill) => (
                        <span key={`${highlight.entry_id}-${skill}`}>
                          {skill}
                        </span>
                      ))}
                    </div>

                    {highlight.trust_signals?.length > 0 && (
                      <div className="report-trust-line">
                        {highlight.trust_signals.map((signal) => (
                          <span key={`${highlight.entry_id}-${signal}`}>
                            {formatLabel(signal)}
                          </span>
                        ))}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <p className="report-muted">
                No accomplishments were recorded for this period.
              </p>
            )}
          </section>

          <section className="report-panel">
            <p className="reports-eyebrow">Ready-to-use material</p>
            <h2>Résumé bullets</h2>

            {report.resume_bullets?.length ? (
              <ul className="resume-bullet-list">
                {report.resume_bullets.map((bullet, index) => (
                  <li key={`${index}-${bullet}`}>{bullet}</li>
                ))}
              </ul>
            ) : (
              <p className="report-muted">
                No résumé bullets were generated for this period.
              </p>
            )}
          </section>
        </>
      ) : null}
    </main>
  );
}

export default ReportsPage;
