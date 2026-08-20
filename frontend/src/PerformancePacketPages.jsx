import {
  Award,
  BadgeCheck,
  BarChart3,
  BookOpenCheck,
  CheckCircle2,
  FileCheck2,
  LineChart,
  Medal,
  ReceiptText,
  ShieldCheck,
  Sparkles,
  Target,
  UsersRound,
} from "lucide-react";

import "./PerformancePacketPages.css";

function formatShortDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(new Date(`${value}T12:00:00`));
}
function formatMonth(value) {
  if (!value) return "";
  const [year, month] = value.split("-");
  return new Intl.DateTimeFormat("en-US", { month: "short", year: "2-digit" }).format(new Date(Number(year), Number(month) - 1, 1));
}
function formatLabel(value = "") { return String(value).replace(/-/g, " ").replace(/\b\w/g, (character) => character.toUpperCase()); }
function chunk(items, size) { const result = []; for (let index = 0; index < items.length; index += size) result.push(items.slice(index, index + size)); return result.length ? result : [[]]; }
function themeClass(packet) { return `packet-theme-${packet?.render_config?.theme || "classic-dossier"}`; }

function PacketFooter({ page }) { return <footer className="packet-page-footer"><span>BragStack · Career Evidence System</span><span>Page {page}</span></footer>; }
function PacketHeader({ index, title, eyebrow }) { return <header className="packet-page-header"><div><p>{String(index).padStart(2, "0")} · {eyebrow}</p><h2>{title}</h2></div><div className="packet-page-header-mark">BRAGSTACK</div></header>; }
function EmptyState({ children }) { return <div className="packet-document-empty"><BookOpenCheck size={22} /><p>{children}</p></div>; }
function ItemNote({ packet, itemKey }) {
  const annotations = packet?.annotations ?? {};
  const note = annotations.include_in_export === false ? "" : annotations.item_notes?.[itemKey];
  return note ? <aside className="packet-user-note"><strong>User-authored context</strong><p>{note}</p><small>{annotations.authorship}</small></aside> : null;
}
function HorizontalBars({ items, limit = 6 }) {
  const entries = Object.entries(items ?? {}).slice(0, limit);
  const highest = Math.max(...entries.map(([, count]) => Number(count) || 0), 1);
  if (!entries.length) return <EmptyState>Add categorized accomplishments to build this view.</EmptyState>;
  return <div className="packet-horizontal-bars">{entries.map(([label, count]) => <div key={label}><div className="packet-horizontal-bar-copy"><span>{label}</span><strong>{count}</strong></div><div className="packet-horizontal-bar-track"><span style={{ width: `${Math.max(8, (count / highest) * 100)}%` }} /></div></div>)}</div>;
}

function ImpactAnalyticsPage({ packet, page }) {
  const analytics = packet?.impact_analytics ?? {}; const activity = Object.entries(analytics.activity_by_month ?? {}).slice(-12); const maxActivity = Math.max(...activity.map(([, count]) => Number(count) || 0), 1); const scorecard = packet?.scorecard ?? {};
  return <section className={`packet-sheet packet-document-page ${themeClass(packet)}`}><PacketHeader index={2} eyebrow="Impact Analytics" title="How the work shows up" /><p className="packet-page-lead">A period-level view of documented activity, work themes, and proof quality. These charts summarize recorded evidence; they do not assign a subjective rating.</p><div className="packet-kpi-ribbon"><div><strong>{scorecard.quantified_result_coverage_percent ?? 0}%</strong><span>Quantified coverage</span></div><div><strong>{scorecard.verification_coverage_percent ?? 0}%</strong><span>Recognition coverage</span></div><div><strong>{scorecard.evidence_depth ?? 0}×</strong><span>Evidence depth</span></div></div><section className="packet-document-section"><div className="packet-document-section-title"><div><p>Activity trend</p><h3>Documented accomplishments over time</h3></div><LineChart size={20} /></div>{activity.length ? <div className="packet-activity-chart">{activity.map(([month, count]) => <div key={month} className="packet-activity-column"><span className="packet-activity-value">{count}</span><div className="packet-activity-bar-wrap"><span className="packet-activity-bar" style={{ height: `${Math.max(10, (count / maxActivity) * 100)}%` }} /></div><small>{formatMonth(month)}</small></div>)}</div> : <EmptyState>Activity appears as dated accomplishments are recorded.</EmptyState>}</section><div className="packet-document-two-column"><section className="packet-document-section compact"><div className="packet-document-section-title"><div><p>Work mix</p><h3>Primary themes</h3></div><BarChart3 size={19} /></div><HorizontalBars items={analytics.categories} /></section><section className="packet-document-section compact"><div className="packet-document-section-title"><div><p>Trust signals</p><h3>Proof strength</h3></div><ShieldCheck size={19} /></div><HorizontalBars items={analytics.trust_signals} /></section></div><PacketFooter page={page} /></section>;
}

function SignaturePage({ packet, page }) {
  const items = packet?.signature_accomplishments ?? [];
  return <section className={`packet-sheet packet-document-page ${themeClass(packet)}`}><PacketHeader index={3} eyebrow="Signature Accomplishments" title="Work selected for the conversation" /><p className="packet-page-lead">Auto-ranking is the default. When you pin accomplishments, this page follows your exact selected order without changing the source records or period metrics.</p>{items.length ? <div className="packet-accomplishment-list">{items.slice(0, 8).map((item, index) => <article key={item.entry_id} className="packet-accomplishment-record"><div className="packet-accomplishment-number">{String(index + 1).padStart(2, "0")}</div><div><div className="packet-record-meta"><span>{item.category || "Accomplishment"}</span>{item.entry_date && <span>{formatShortDate(item.entry_date)}</span>}{item.verified && <span className="packet-verified-chip"><BadgeCheck size={12} /> Recognized</span>}</div><h3>{item.title}</h3>{item.result && <p>{item.result}</p>}<div className="packet-record-tags">{item.skills?.slice(0, 5).map((skill) => <span key={skill}>{skill}</span>)}</div><ItemNote packet={packet} itemKey={item.entry_id} /></div><div className="packet-record-proof"><strong>{item.evidence_count ?? 0}</strong><span>evidence</span></div></article>)}</div> : <EmptyState>Add accomplishments or leave pinning empty to use automatic ranking.</EmptyState>}<PacketFooter page={page} /></section>;
}

function ResultsPage({ packet, page }) {
  const results = packet?.measurable_results ?? []; const coverage = packet?.scorecard?.quantified_result_coverage_percent ?? 0;
  return <section className={`packet-sheet packet-document-page ${themeClass(packet)}`}><PacketHeader index={4} eyebrow="Measurable Results" title="Outcomes with numbers behind them" /><div className="packet-result-hero"><Target size={24} /><div><strong>{coverage}%</strong><span>of Impact Receipts include a quantified result</span></div></div>{results.length ? <div className="packet-result-grid">{results.slice(0, 8).map((item) => <article key={`${item.entry_id}-${item.result}`}><div className="packet-result-metric">{item.metric_display || "Measured"}</div><p className="packet-section-kicker">{item.category}</p><h3>{item.title}</h3><p>{item.result}</p><div className="packet-result-proofline">{item.verified ? <><CheckCircle2 size={13} /> Recognized contribution</> : <><FileCheck2 size={13} /> Documented result</>}</div></article>)}</div> : <EmptyState>Measured results appear when documented work contains a truthful numeric signal.</EmptyState>}<div className="packet-document-note"><strong>Interpretation note</strong><p>BragStack displays numeric language already present in the record. It does not invent savings, percentages, revenue, or outcomes.</p></div><PacketFooter page={page} /></section>;
}

function SkillsPage({ packet, page }) {
  const skills = packet?.skill_details ?? []; const maxCount = Math.max(...skills.map((item) => Number(item.count) || 0), 1);
  return <section className={`packet-sheet packet-document-page ${themeClass(packet)}`}><PacketHeader index={5} eyebrow="Skills & Growth" title="Capabilities demonstrated in real work" /><p className="packet-page-lead">Frequency reflects how often a capability appears in documented work—not a proficiency score.</p>{skills.length ? <div className="packet-skill-evidence-list">{skills.slice(0, 12).map((item, index) => <article key={item.skill}><div className="packet-skill-rank">{index + 1}</div><div className="packet-skill-main"><div><strong>{item.skill}</strong><span>{item.count} documented use{item.count === 1 ? "" : "s"}</span></div><div className="packet-skill-track"><span style={{ width: `${Math.max(8, (item.count / maxCount) * 100)}%` }} /></div></div><div className="packet-skill-dates"><span>First shown</span><strong>{formatShortDate(item.first_seen)}</strong><span>Most recent</span><strong>{formatShortDate(item.last_seen)}</strong></div></article>)}</div> : <EmptyState>Add skills to accomplishments or Impact Receipts to build capability evidence.</EmptyState>}<div className="packet-growth-callout"><Sparkles size={19} /><div><strong>Career-neutral by design</strong><p>Clinical, instructional, interpersonal, operational, technical, creative, sales, trade, management, and other capabilities use the same evidence model.</p></div></div><PacketFooter page={page} /></section>;
}

function ContributionPage({ packet, page }) {
  const contributions = packet?.contribution_records ?? []; const confirmed = packet?.scorecard?.confirmed_assertions ?? 0;
  return <section className={`packet-sheet packet-document-page ${themeClass(packet)}`}><PacketHeader index={6} eyebrow="Contribution & Verified Recognition" title="What you moved forward and who recognized it" /><div className="packet-contribution-summary"><div><UsersRound size={21} /><strong>{contributions.length}</strong><span>contribution records</span></div><div><BadgeCheck size={21} /><strong>{confirmed}</strong><span>confirmed recognitions</span></div></div>{contributions.length ? <div className="packet-contribution-list">{contributions.slice(0, 8).map((item) => <article key={item.reference}><div className="packet-contribution-topline"><span>{item.reference}</span>{item.verified && <span className="packet-verified-chip"><BadgeCheck size={12} /> Recognized</span>}</div><h3>{item.accomplishment}</h3>{item.contribution && <p><strong>Contribution:</strong> {item.contribution}</p>}{item.result && <p><strong>Result:</strong> {item.result}</p>}{item.recognition?.length > 0 && <div className="packet-recognition-list">{item.recognition.map((recognition, index) => <span key={`${item.reference}-${recognition.label}-${index}`}>{recognition.label}{recognition.name ? ` · ${recognition.name}` : ""}</span>)}</div>}<ItemNote packet={packet} itemKey={item.reference} /></article>)}</div> : <EmptyState>Create Impact Receipts to document the contribution behind each result.</EmptyState>}<PacketFooter page={page} /></section>;
}

function ReceiptPages({ packet, startPage }) {
  const pages = chunk(packet?.receipt_records ?? [], 2);
  return pages.map((items, pageIndex) => <section key={`receipt-${pageIndex}`} className={`packet-sheet packet-document-page ${themeClass(packet)}`}><PacketHeader index={7} eyebrow="Impact Receipts" title={pageIndex ? "Evidence-backed records · continued" : "Literal receipts for the work"} /><div className="packet-receipt-page-grid">{items.length ? items.map((receipt) => <article key={receipt.id} className="packet-receipt-card"><div className="packet-receipt-top"><div><ReceiptText size={17} /><span>Impact Receipt</span></div><strong>{receipt.reference}</strong></div><div className="packet-receipt-title"><p>{receipt.entry_date ? formatShortDate(receipt.entry_date) : "Documented proof"}</p><h3>{receipt.accomplishment}</h3></div><dl><div><dt>Contribution</dt><dd>{receipt.contribution || "Documented in source accomplishment."}</dd></div><div><dt>Result</dt><dd>{receipt.result || "Result not yet added."}</dd></div></dl>{receipt.recognition?.length > 0 && <div className="packet-recognition-list">{receipt.recognition.map((entry, index) => <span key={`${receipt.reference}-${entry.label}-${index}`}>{entry.label}{entry.name ? ` · ${entry.name}` : ""}</span>)}</div>}<div className="packet-receipt-status">{receipt.verified ? <><BadgeCheck size={14} /> Verified Recognition attached</> : <><ShieldCheck size={14} /> Documented evidence record</>}</div><ItemNote packet={packet} itemKey={receipt.id} /></article>) : <EmptyState>Create Impact Receipts to populate the appendix.</EmptyState>}</div><PacketFooter page={startPage + pageIndex} /></section>);
}

function EvidencePages({ packet, startPage }) {
  const pages = chunk(packet?.evidence_index ?? [], 10);
  return pages.map((items, pageIndex) => <section key={`evidence-${pageIndex}`} className={`packet-sheet packet-document-page ${themeClass(packet)}`}><PacketHeader index={8} eyebrow="Evidence Index" title={pageIndex ? "Evidence Index · continued" : "Source material behind the claims"} />{packet?.sharing_notice && <p className="packet-document-note">{packet.sharing_notice}</p>}{items.length ? <div className="packet-evidence-table"><div className="packet-evidence-row header"><span>Receipt</span><span>Evidence</span><span>Type</span><span>Reference</span></div>{items.map((item, index) => <div className="packet-evidence-row" key={`${item.receipt_reference}-${item.title}-${index}`}><span>{item.receipt_reference}</span><span><strong>{item.title}</strong><small>{item.description}</small></span><span>{formatLabel(item.type)}</span><span>{item.reference || "Stored in BragStack"}</span></div>)}</div> : <EmptyState>No evidence references are included in this packet.</EmptyState>}<PacketFooter page={startPage + pageIndex} /></section>);
}

function SummaryPage({ packet, page }) {
  const talkingPoints = packet?.talking_points ?? []; const context = packet?.context ?? {};
  return <section className={`packet-sheet packet-document-page packet-summary-page ${themeClass(packet)}`}><PacketHeader index={9} eyebrow="Review Summary" title="The case, assembled" /><div className="packet-summary-context">{context.career_area && <span>{context.career_area}</span>}{context.organization && <span>{context.organization}</span>}</div><section className="packet-summary-narrative"><Medal size={26} /><div><p className="packet-section-kicker">Evidence-backed summary</p><p>{packet?.review_summary}</p></div></section><section className="packet-talking-points"><div className="packet-document-section-title"><div><p>Conversation guide</p><h3>Review talking points</h3></div><Award size={19} /></div>{talkingPoints.length ? <ol>{talkingPoints.map((item) => <li key={`${item.title}-${item.result}`}><strong>{item.title}</strong>{item.result && <span>{item.result}</span>}</li>)}</ol> : <EmptyState>Add accomplishments to generate evidence-backed talking points.</EmptyState>}</section><div className="packet-summary-close"><CheckCircle2 size={20} /><div><strong>Bring the receipts.</strong><p>Every section leads back to documented work instead of relying on memory at review time.</p></div></div><PacketFooter page={page} /></section>;
}

function PerformancePacketPages({ packet }) {
  const enabled = new Set(packet?.render_config?.sections ?? ["impact-analytics", "signature-accomplishments", "measurable-results", "skills-growth", "contribution-recognition", "impact-receipts", "evidence-index", "review-summary"]);
  let page = 3;
  const nodes = [];
  if (enabled.has("impact-analytics")) { nodes.push(<ImpactAnalyticsPage key="analytics" packet={packet} page={page} />); page += 1; }
  if (enabled.has("signature-accomplishments")) { nodes.push(<SignaturePage key="signatures" packet={packet} page={page} />); page += 1; }
  if (enabled.has("measurable-results")) { nodes.push(<ResultsPage key="results" packet={packet} page={page} />); page += 1; }
  if (enabled.has("skills-growth")) { nodes.push(<SkillsPage key="skills" packet={packet} page={page} />); page += 1; }
  if (enabled.has("contribution-recognition")) { nodes.push(<ContributionPage key="contribution" packet={packet} page={page} />); page += 1; }
  if (enabled.has("impact-receipts")) { const count = Math.max(1, Math.ceil((packet?.receipt_records?.length ?? 0) / 2)); nodes.push(<ReceiptPages key="receipts" packet={packet} startPage={page} />); page += count; }
  if (enabled.has("evidence-index")) { const count = Math.max(1, Math.ceil((packet?.evidence_index?.length ?? 0) / 10)); nodes.push(<EvidencePages key="evidence" packet={packet} startPage={page} />); page += count; }
  if (enabled.has("review-summary")) nodes.push(<SummaryPage key="summary" packet={packet} page={page} />);
  return <>{nodes}</>;
}

export default PerformancePacketPages;
