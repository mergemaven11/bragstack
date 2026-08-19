import {
  Award,
  BadgeCheck,
  BarChart3,
  BookOpenCheck,
  CalendarDays,
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
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(`${value}T12:00:00`));
}

function formatMonth(value) {
  if (!value) return "";
  const [year, month] = value.split("-");
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    year: "2-digit",
  }).format(new Date(Number(year), Number(month) - 1, 1));
}

function formatLabel(value = "") {
  return String(value)
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function chunk(items, size) {
  const result = [];
  for (let index = 0; index < items.length; index += size) {
    result.push(items.slice(index, index + size));
  }
  return result.length ? result : [[]];
}

function PacketFooter({ page }) {
  return (
    <footer className="packet-page-footer">
      <span>BragStack · Career Evidence System</span>
      <span>Page {page}</span>
    </footer>
  );
}

function PacketHeader({ index, title, eyebrow }) {
  return (
    <header className="packet-page-header">
      <div>
        <p>{String(index).padStart(2, "0")} · {eyebrow}</p>
        <h2>{title}</h2>
      </div>
      <div className="packet-page-header-mark">BRAGSTACK</div>
    </header>
  );
}

function EmptyState({ children }) {
  return (
    <div className="packet-document-empty">
      <BookOpenCheck size={22} />
      <p>{children}</p>
    </div>
  );
}

function HorizontalBars({ items, limit = 6 }) {
  const entries = Object.entries(items ?? {}).slice(0, limit);
  const highest = Math.max(...entries.map(([, count]) => Number(count) || 0), 1);

  if (!entries.length) {
    return <EmptyState>Add categorized accomplishments to build this view.</EmptyState>;
  }

  return (
    <div className="packet-horizontal-bars">
      {entries.map(([label, count]) => (
        <div key={label}>
          <div className="packet-horizontal-bar-copy">
            <span>{label}</span>
            <strong>{count}</strong>
          </div>
          <div className="packet-horizontal-bar-track">
            <span style={{ width: `${Math.max(8, (count / highest) * 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function ImpactAnalyticsPage({ packet, page }) {
  const analytics = packet?.impact_analytics ?? {};
  const activity = Object.entries(analytics.activity_by_month ?? {}).slice(-12);
  const maxActivity = Math.max(...activity.map(([, count]) => Number(count) || 0), 1);
  const scorecard = packet?.scorecard ?? {};

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={2} eyebrow="Impact Analytics" title="How the work shows up" />

      <p className="packet-page-lead">
        A period-level view of documented activity, work themes, and proof quality.
        These charts summarize recorded career evidence; they do not assign a
        subjective performance rating.
      </p>

      <div className="packet-kpi-ribbon">
        <div><strong>{scorecard.quantified_result_coverage_percent ?? 0}%</strong><span>Quantified result coverage</span></div>
        <div><strong>{scorecard.verification_coverage_percent ?? 0}%</strong><span>Verification coverage</span></div>
        <div><strong>{scorecard.evidence_depth ?? 0}×</strong><span>Evidence depth</span></div>
      </div>

      <section className="packet-document-section">
        <div className="packet-document-section-title">
          <div><p>Activity trend</p><h3>Documented accomplishments over time</h3></div>
          <LineChart size={20} />
        </div>

        {activity.length ? (
          <div className="packet-activity-chart" aria-label="Accomplishments by month">
            {activity.map(([month, count]) => (
              <div key={month} className="packet-activity-column">
                <span className="packet-activity-value">{count}</span>
                <div className="packet-activity-bar-wrap">
                  <span
                    className="packet-activity-bar"
                    style={{ height: `${Math.max(10, (count / maxActivity) * 100)}%` }}
                  />
                </div>
                <small>{formatMonth(month)}</small>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState>Activity will appear as accomplishments are dated and recorded.</EmptyState>
        )}
      </section>

      <div className="packet-document-two-column">
        <section className="packet-document-section compact">
          <div className="packet-document-section-title">
            <div><p>Work mix</p><h3>Primary themes</h3></div>
            <BarChart3 size={19} />
          </div>
          <HorizontalBars items={analytics.categories} />
        </section>

        <section className="packet-document-section compact">
          <div className="packet-document-section-title">
            <div><p>Trust signals</p><h3>Proof strength</h3></div>
            <ShieldCheck size={19} />
          </div>
          <HorizontalBars items={analytics.trust_signals} />
        </section>
      </div>

      <PacketFooter page={page} />
    </section>
  );
}

function SignatureAccomplishmentsPage({ packet, page }) {
  const items = packet?.signature_accomplishments ?? [];

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={3} eyebrow="Signature Accomplishments" title="Work worth discussing" />
      <p className="packet-page-lead">
        Strong examples are prioritized using documented results, evidence,
        verification, and Impact Receipt completeness—not profession-specific rules.
      </p>

      {items.length ? (
        <div className="packet-accomplishment-list">
          {items.slice(0, 6).map((item, index) => (
            <article key={item.entry_id} className="packet-accomplishment-record">
              <div className="packet-accomplishment-number">{String(index + 1).padStart(2, "0")}</div>
              <div>
                <div className="packet-record-meta">
                  <span>{item.category || "Accomplishment"}</span>
                  {item.entry_date && <span>{formatShortDate(item.entry_date)}</span>}
                  {item.verified && <span className="packet-verified-chip"><BadgeCheck size={12} /> Verified</span>}
                </div>
                <h3>{item.title}</h3>
                {item.result && <p>{item.result}</p>}
                <div className="packet-record-tags">
                  {item.skills?.slice(0, 5).map((skill) => <span key={skill}>{skill}</span>)}
                </div>
              </div>
              <div className="packet-record-proof">
                <strong>{item.evidence_count ?? 0}</strong>
                <span>evidence</span>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState>Add accomplishments with clear results to populate signature examples.</EmptyState>
      )}

      <PacketFooter page={page} />
    </section>
  );
}

function MeasurableResultsPage({ packet, page }) {
  const results = packet?.measurable_results ?? [];
  const coverage = packet?.scorecard?.quantified_result_coverage_percent ?? 0;

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={4} eyebrow="Measurable Results" title="Outcomes with numbers behind them" />

      <div className="packet-result-hero">
        <Target size={24} />
        <div>
          <strong>{coverage}%</strong>
          <span>of Impact Receipts include a quantified result</span>
        </div>
      </div>

      {results.length ? (
        <div className="packet-result-grid">
          {results.slice(0, 8).map((item) => (
            <article key={`${item.entry_id}-${item.result}`}>
              <div className="packet-result-metric">{item.metric_display || "Measured"}</div>
              <p className="packet-section-kicker">{item.category}</p>
              <h3>{item.title}</h3>
              <p>{item.result}</p>
              <div className="packet-result-proofline">
                {item.verified ? <><CheckCircle2 size={13} /> Verified contribution</> : <><FileCheck2 size={13} /> Documented result</>}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState>
          Quantified results appear when an accomplishment or Impact Receipt contains a
          number, percentage, amount, count, duration, or other measurable signal.
        </EmptyState>
      )}

      <div className="packet-document-note">
        <strong>Interpretation note</strong>
        <p>
          BragStack displays the numeric language already present in your records. It
          does not invent savings, percentages, revenue, or outcomes.
        </p>
      </div>

      <PacketFooter page={page} />
    </section>
  );
}

function SkillsGrowthPage({ packet, page }) {
  const skills = packet?.skill_details ?? [];
  const maxCount = Math.max(...skills.map((item) => Number(item.count) || 0), 1);

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={5} eyebrow="Skills & Growth" title="Capabilities demonstrated in real work" />
      <p className="packet-page-lead">
        Skill evidence is based on accomplishments and Impact Receipts. Frequency
        reflects how often a capability appears in documented work—not a proficiency score.
      </p>

      {skills.length ? (
        <div className="packet-skill-evidence-list">
          {skills.slice(0, 12).map((item, index) => (
            <article key={item.skill}>
              <div className="packet-skill-rank">{index + 1}</div>
              <div className="packet-skill-main">
                <div><strong>{item.skill}</strong><span>{item.count} documented use{item.count === 1 ? "" : "s"}</span></div>
                <div className="packet-skill-track"><span style={{ width: `${Math.max(8, (item.count / maxCount) * 100)}%` }} /></div>
              </div>
              <div className="packet-skill-dates">
                <span>First shown</span><strong>{formatShortDate(item.first_seen)}</strong>
                <span>Most recent</span><strong>{formatShortDate(item.last_seen)}</strong>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState>Add skills to accomplishments or Impact Receipts to build capability evidence.</EmptyState>
      )}

      <div className="packet-growth-callout">
        <Sparkles size={19} />
        <div>
          <strong>Career-neutral by design</strong>
          <p>
            Skills can be clinical, instructional, interpersonal, operational,
            technical, creative, sales-focused, trade-specific, managerial, or anything
            else your work demonstrates.
          </p>
        </div>
      </div>

      <PacketFooter page={page} />
    </section>
  );
}

function ContributionPage({ packet, page }) {
  const contributions = packet?.contribution_records ?? [];
  const confirmed = packet?.scorecard?.confirmed_assertions ?? 0;

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={6} eyebrow="Contribution & Recognition" title="What you personally moved forward" />

      <div className="packet-contribution-summary">
        <div><UsersRound size={21} /><strong>{contributions.length}</strong><span>structured contribution records</span></div>
        <div><BadgeCheck size={21} /><strong>{confirmed}</strong><span>confirmed assertions</span></div>
      </div>

      {contributions.length ? (
        <div className="packet-contribution-list">
          {contributions.slice(0, 6).map((item) => (
            <article key={item.reference}>
              <div className="packet-contribution-topline">
                <span>{item.reference}</span>
                {item.verified && <span className="packet-verified-chip"><BadgeCheck size={12} /> Confirmed</span>}
              </div>
              <h3>{item.accomplishment}</h3>
              {item.contribution && <p><strong>Contribution:</strong> {item.contribution}</p>}
              {item.result && <p><strong>Result:</strong> {item.result}</p>}
              <div className="packet-contribution-meta">
                <span>{item.evidence_count ?? 0} evidence item{item.evidence_count === 1 ? "" : "s"}</span>
                {item.confirmations?.slice(0, 2).map((confirmation) => (
                  <span key={`${item.reference}-${confirmation.name}`}>
                    {confirmation.name}{confirmation.role ? ` · ${confirmation.role}` : ""}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState>Create Impact Receipts to document the specific contribution behind each result.</EmptyState>
      )}

      <PacketFooter page={page} />
    </section>
  );
}

function ImpactReceiptCard({ receipt }) {
  return (
    <article className="packet-receipt-card">
      <div className="packet-receipt-top">
        <div><ReceiptText size={17} /><span>Impact Receipt</span></div>
        <strong>{receipt.reference}</strong>
      </div>
      <div className="packet-receipt-title">
        <p>{receipt.entry_date ? formatShortDate(receipt.entry_date) : "Documented proof"}</p>
        <h3>{receipt.accomplishment}</h3>
      </div>
      <dl>
        <div><dt>Contribution</dt><dd>{receipt.contribution || "Documented in source accomplishment."}</dd></div>
        <div><dt>Result</dt><dd>{receipt.result || "Result not yet added."}</dd></div>
      </dl>
      <div className="packet-receipt-skills">
        {receipt.skills?.slice(0, 7).map((skill) => <span key={skill}>{skill}</span>)}
      </div>
      <div className="packet-receipt-proof-grid">
        <div><strong>{receipt.evidence?.length ?? 0}</strong><span>Evidence</span></div>
        <div><strong>{receipt.confirmations?.filter((item) => item.status === "confirmed").length ?? 0}</strong><span>Confirmations</span></div>
        <div><strong>{receipt.credit?.length ?? 0}</strong><span>Shared credit</span></div>
      </div>
      <div className="packet-receipt-status">
        {receipt.verified ? <><BadgeCheck size={14} /> Confirmed contribution</> : <><ShieldCheck size={14} /> Evidence-backed record</>}
      </div>
    </article>
  );
}

function ReceiptPages({ packet, startPage }) {
  const receipts = packet?.receipt_records ?? [];
  const pages = chunk(receipts, 2);

  return pages.map((items, index) => (
    <section key={`receipt-page-${index}`} className="packet-sheet packet-document-page">
      <PacketHeader
        index={7}
        eyebrow="Impact Receipts"
        title={index === 0 ? "Receipts for the work" : "Impact Receipts · continued"}
      />
      <p className="packet-page-lead">
        Each receipt ties an accomplishment to contribution, result, skills,
        supporting evidence, credit, and confirmation signals.
      </p>
      {items.length ? (
        <div className="packet-receipt-stack">
          {items.map((receipt) => <ImpactReceiptCard key={receipt.reference} receipt={receipt} />)}
        </div>
      ) : (
        <EmptyState>Turn accomplishments into Impact Receipts to create printable proof records.</EmptyState>
      )}
      <PacketFooter page={startPage + index} />
    </section>
  ));
}

function EvidencePages({ packet, startPage }) {
  const evidence = packet?.evidence_index ?? [];
  const pages = chunk(evidence, 10);

  return pages.map((items, index) => (
    <section key={`evidence-page-${index}`} className="packet-sheet packet-document-page">
      <PacketHeader
        index={8}
        eyebrow="Evidence Index"
        title={index === 0 ? "Source material behind the claims" : "Evidence Index · continued"}
      />
      <p className="packet-page-lead">
        A private packet can include evidence references whether or not those items
        are public on a Proof Profile.
      </p>

      {items.length ? (
        <div className="packet-evidence-table" role="table" aria-label="Evidence index">
          <div className="packet-evidence-row header" role="row">
            <span>Receipt</span><span>Evidence</span><span>Type</span><span>Reference</span>
          </div>
          {items.map((item, itemIndex) => (
            <div className="packet-evidence-row" role="row" key={`${item.receipt_reference}-${item.title}-${itemIndex}`}>
              <span>{item.receipt_reference}</span>
              <span><strong>{item.title}</strong><small>{item.description}</small></span>
              <span>{formatLabel(item.type)}</span>
              <span>{item.reference || "Stored in BragStack"}</span>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState>Add documents, feedback, certificates, links, photos, or other proof to your Impact Receipts.</EmptyState>
      )}

      <PacketFooter page={startPage + index} />
    </section>
  ));
}

function ReviewSummaryPage({ packet, page }) {
  const talkingPoints = packet?.talking_points ?? [];
  const context = packet?.context ?? {};

  return (
    <section className="packet-sheet packet-document-page packet-summary-page">
      <PacketHeader index={9} eyebrow="Review Summary" title="The case, assembled" />

      <div className="packet-summary-context">
        {context.career_area && <span>{context.career_area}</span>}
        {context.organization && <span>{context.organization}</span>}
      </div>

      <section className="packet-summary-narrative">
        <Medal size={26} />
        <div>
          <p className="packet-section-kicker">Evidence-backed summary</p>
          <p>{packet?.review_summary}</p>
        </div>
      </section>

      <section className="packet-talking-points">
        <div className="packet-document-section-title">
          <div><p>Conversation guide</p><h3>Review talking points</h3></div>
          <Award size={19} />
        </div>
        {talkingPoints.length ? (
          <ol>
            {talkingPoints.map((item) => (
              <li key={`${item.title}-${item.result}`}>
                <strong>{item.title}</strong>
                {item.result && <span>{item.result}</span>}
              </li>
            ))}
          </ol>
        ) : (
          <EmptyState>Add accomplishments to generate evidence-backed talking points.</EmptyState>
        )}
      </section>

      <div className="packet-summary-close">
        <CheckCircle2 size={20} />
        <div>
          <strong>Bring the receipts.</strong>
          <p>
            Every section in this packet is designed to lead back to documented
            work instead of relying on memory at review time.
          </p>
        </div>
      </div>

      <PacketFooter page={page} />
    </section>
  );
}

function PerformancePacketPages({ packet }) {
  const receiptPageCount = Math.max(1, Math.ceil((packet?.receipt_records?.length ?? 0) / 2));
  const evidencePageCount = Math.max(1, Math.ceil((packet?.evidence_index?.length ?? 0) / 10));
  const receiptStartPage = 8;
  const evidenceStartPage = receiptStartPage + receiptPageCount;
  const summaryPage = evidenceStartPage + evidencePageCount;

  return (
    <>
      <ImpactAnalyticsPage packet={packet} page={3} />
      <SignatureAccomplishmentsPage packet={packet} page={4} />
      <MeasurableResultsPage packet={packet} page={5} />
      <SkillsGrowthPage packet={packet} page={6} />
      <ContributionPage packet={packet} page={7} />
      <ReceiptPages packet={packet} startPage={receiptStartPage} />
      <EvidencePages packet={packet} startPage={evidenceStartPage} />
      <ReviewSummaryPage packet={packet} page={summaryPage} />
    </>
  );
}

export default PerformancePacketPages;
