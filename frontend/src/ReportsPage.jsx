import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  CalendarDays,
  Clipboard,
  Download,
  FileText,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import PacketBuilderPanel from "./PacketBuilderPanel";
import PerformancePacketPreview from "./PerformancePacketPreview";
import {
  getAllTimeCareerReport,
  getCustomCareerReport,
  getPerformancePacket,
  getWeeklyCareerReport,
} from "./api";
import "./ReportsPage.css";

const REPORT_TYPES = [
  { key: "weekly", label: "Weekly" },
  { key: "all-time", label: "All time" },
  { key: "custom", label: "Custom" },
];

const DEFAULT_PACKET_OPTIONS = {
  careerArea: "",
  roleTitle: "",
  organization: "",
  confidential: true,
};

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

function buildReportMarkdown(report) {
  if (!report) return "";

  const totals = report.totals ?? {};
  const period = report.period ?? {};
  const lines = [
    "# BragStack Career Report",
    "",
    `**Period:** ${period.label ?? "Career report"}`,
    period.start_date && period.end_date
      ? `**Dates:** ${period.start_date} to ${period.end_date}`
      : "**Dates:** All recorded work",
    "",
    report.summary ?? "",
    "",
    "## Metrics",
    "",
    `- Accomplishments: ${totals.entries ?? 0}`,
    `- Impact Receipts: ${totals.impact_receipts ?? 0}`,
    `- Evidence items: ${totals.evidence_items ?? 0}`,
    `- Confirmed contributions: ${totals.confirmed_assertions ?? 0}`,
    `- Quantified results: ${totals.quantified_results ?? 0}`,
    "",
    "## Top Skills",
    "",
  ];

  const skills = Object.entries(report.top_skills ?? {});
  if (skills.length) {
    skills.forEach(([skill, count]) => lines.push(`- ${skill}: ${count}`));
  } else {
    lines.push("- No skill data for this period.");
  }

  lines.push("", "## Career Highlights", "");
  if (report.highlights?.length) {
    report.highlights.forEach((highlight) => {
      lines.push(`### ${highlight.title}`);
      lines.push(`- Category: ${highlight.category ?? "Uncategorized"}`);
      if (highlight.result) lines.push(`- Result: ${highlight.result}`);
      if (highlight.skills?.length) lines.push(`- Skills: ${highlight.skills.join(", ")}`);
      lines.push("");
    });
  } else {
    lines.push("No highlights for this period.", "");
  }

  lines.push("## Résumé Bullets", "");
  if (report.resume_bullets?.length) {
    report.resume_bullets.forEach((bullet) => lines.push(`- ${bullet}`));
  } else {
    lines.push("- No résumé bullets generated for this period.");
  }

  return `${lines.join("\n").trim()}\n`;
}

function ReportsPage() {
  const [activeType, setActiveType] = useState("weekly");
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [startDate, setStartDate] = useState(getThirtyDaysAgo());
  const [endDate, setEndDate] = useState(getToday());
  const [searchQuery, setSearchQuery] = useState("");
  const [copyNotice, setCopyNotice] = useState("");
  const [packet, setPacket] = useState(null);
  const [isPacketLoading, setIsPacketLoading] = useState(false);
  const [packetError, setPacketError] = useState("");
  const [showPacket, setShowPacket] = useState(false);
  const [packetOptions, setPacketOptions] = useState(DEFAULT_PACKET_OPTIONS);

  async function loadReport(type = activeType) {
    const token = localStorage.getItem("bragstack_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }

    setIsLoading(true);
    setError("");
    setCopyNotice("");
    setPacketError("");

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
      setPacket(null);
      setShowPacket(false);
    } catch (requestError) {
      console.error(requestError);
      if (requestError.response?.status === 401) {
        localStorage.removeItem("bragstack_token");
        window.location.href = "/login";
        return;
      }
      setError(requestError.response?.data?.detail ?? "The report could not be generated.");
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

  const filteredHighlights = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    const highlights = report?.highlights ?? [];
    if (!query) return highlights;

    return highlights.filter((highlight) =>
      [
        highlight.title,
        highlight.category,
        highlight.result,
        ...(highlight.skills ?? []),
        ...(highlight.trust_signals ?? []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(query)
    );
  }, [report, searchQuery]);

  function handleTypeChange(type) {
    setActiveType(type);
    setSearchQuery("");
    setPacketError("");
    if (type !== "custom") void loadReport(type);
  }

  function handleCustomSubmit(event) {
    event.preventDefault();
    setActiveType("custom");
    setSearchQuery("");
    setPacketError("");
    void loadReport("custom");
  }

  async function copyText(text, message) {
    try {
      await navigator.clipboard.writeText(text);
      setCopyNotice(message);
    } catch (clipboardError) {
      console.error(clipboardError);
      setCopyNotice("Copy failed. Your browser may block clipboard access.");
    }
  }

  function handleCopyReport() {
    void copyText(buildReportMarkdown(report), "Markdown report copied.");
  }

  function handleCopyBullets() {
    const bullets = report?.resume_bullets ?? [];
    void copyText(bullets.map((bullet) => `- ${bullet}`).join("\n"), "Résumé bullets copied.");
  }

  function handleDownloadReport() {
    const markdown = buildReportMarkdown(report);
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const periodName = report?.period?.label?.toLowerCase().replace(/\s+/g, "-") || "career";

    link.href = url;
    link.download = `bragstack-${periodName}-report.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setCopyNotice("Markdown report downloaded.");
  }

  async function handleBuildPacket() {
    if (!report) return;

    setIsPacketLoading(true);
    setPacketError("");

    try {
      const period = report.period ?? {};
      const hasDates = Boolean(period.start_date && period.end_date);
      const data = await getPerformancePacket(
        hasDates ? period.start_date : undefined,
        hasDates ? period.end_date : undefined,
        packetOptions
      );
      setPacket(data.packet);
      setShowPacket(true);
    } catch (requestError) {
      console.error(requestError);
      if (requestError.response?.status === 401) {
        localStorage.removeItem("bragstack_token");
        window.location.href = "/login";
        return;
      }

      if (requestError.response?.status === 403) {
        setPacketError(
          "Performance Review Packets are included with BragStack Pro. Your standard career reports remain available on Free."
        );
      } else {
        setPacketError(
          requestError.response?.data?.detail ??
            "The Performance Review Packet could not be built."
        );
      }
    } finally {
      setIsPacketLoading(false);
    }
  }

  if (showPacket && packet) {
    return <PerformancePacketPreview packet={packet} onBack={() => setShowPacket(false)} />;
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
            Review recent work, see your all-time impact, or build a report for a
            specific review period.
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
            <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} required />
          </label>
          <label>
            End date
            <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} required />
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
              <p className="reports-eyebrow">{report.period?.label ?? "Career report"}</p>
              <h2>{report.summary}</h2>
              <p>Report dates use the date the work happened, not simply the day it was added to BragStack.</p>
            </div>
            <span className="report-period-badge">
              {report.period?.start_date && report.period?.end_date
                ? `${report.period.start_date} → ${report.period.end_date}`
                : "All recorded work"}
            </span>
          </section>

          <PacketBuilderPanel
            options={packetOptions}
            onChange={setPacketOptions}
            onBuild={() => void handleBuildPacket()}
            isLoading={isPacketLoading}
            error={packetError}
          />

          <section className="report-export-bar" aria-label="Report exports">
            <div>
              <strong>Take your proof with you</strong>
              <span>Copy reusable text or download a portable Markdown report.</span>
            </div>
            <div className="report-export-actions">
              <button type="button" onClick={handleCopyBullets}><Clipboard size={16} />Copy résumé bullets</button>
              <button type="button" onClick={handleCopyReport}><Clipboard size={16} />Copy Markdown</button>
              <button type="button" onClick={handleDownloadReport}><Download size={16} />Download .md</button>
            </div>
          </section>

          {copyNotice && <p className="report-copy-notice">{copyNotice}</p>}

          <section className="report-metrics">
            <article><FileText size={20} /><span>Accomplishments</span><strong>{totals.entries ?? 0}</strong></article>
            <article><Sparkles size={20} /><span>Impact Receipts</span><strong>{totals.impact_receipts ?? 0}</strong></article>
            <article><ShieldCheck size={20} /><span>Evidence items</span><strong>{totals.evidence_items ?? 0}</strong></article>
            <article><ShieldCheck size={20} /><span>Confirmed contributions</span><strong>{totals.confirmed_assertions ?? 0}</strong></article>
            <article><Sparkles size={20} /><span>Quantified results</span><strong>{totals.quantified_results ?? 0}</strong></article>
            <article><FileText size={20} /><span>Public proof</span><strong>{(totals.public_entries ?? 0) + (totals.public_receipts ?? 0)}</strong></article>
          </section>

          <section className="report-two-column">
            <article className="report-panel">
              <p className="reports-eyebrow">Skill signal</p>
              <h2>Top skills</h2>
              {topSkills.length === 0 ? (
                <p className="report-muted">No skill data for this period.</p>
              ) : (
                <div className="report-ranked-list">
                  {topSkills.map(([skill, count]) => <div key={skill}><span>{skill}</span><strong>{count}</strong></div>)}
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
                  {topCategories.map(([category, count]) => <div key={category}><span>{category}</span><strong>{count}</strong></div>)}
                </div>
              )}
            </article>
          </section>

          <section className="report-panel report-highlights">
            <div className="report-panel-heading">
              <div><p className="reports-eyebrow">Career proof</p><h2>Highlights</h2></div>
              <span>{filteredHighlights.length} shown</span>
            </div>

            <label className="report-search">
              <Search size={17} />
              <input
                type="search"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search title, category, skill, result, or trust signal"
              />
            </label>

            {filteredHighlights.length ? (
              <div className="report-highlight-list">
                {filteredHighlights.map((highlight) => (
                  <article key={highlight.entry_id}>
                    <div className="report-highlight-top">
                      <div><p>{highlight.category}</p><h3>{highlight.title}</h3></div>
                      <div className="report-highlight-badges">
                        {highlight.has_receipt && <span>Impact Receipt</span>}
                        {highlight.is_public && <span>Public</span>}
                      </div>
                    </div>
                    {highlight.result && <p>{highlight.result}</p>}
                    <div className="report-skill-tags">
                      {highlight.skills?.map((skill) => <span key={`${highlight.entry_id}-${skill}`}>{skill}</span>)}
                    </div>
                    {highlight.trust_signals?.length > 0 && (
                      <div className="report-trust-line">
                        {highlight.trust_signals.map((signal) => <span key={`${highlight.entry_id}-${signal}`}>{formatLabel(signal)}</span>)}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <p className="report-muted">{searchQuery ? "No highlights match that search." : "No accomplishments were recorded for this period."}</p>
            )}
          </section>

          <section className="report-panel">
            <p className="reports-eyebrow">Ready-to-use material</p>
            <h2>Résumé bullets</h2>
            {report.resume_bullets?.length ? (
              <ul className="resume-bullet-list">
                {report.resume_bullets.map((bullet, index) => <li key={`${index}-${bullet}`}>{bullet}</li>)}
              </ul>
            ) : (
              <p className="report-muted">No résumé bullets were generated for this period.</p>
            )}
          </section>
        </>
      ) : null}
    </main>
  );
}

export default ReportsPage;
