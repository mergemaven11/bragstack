import {
  Award,
  BadgeCheck,
  BookOpenCheck,
  CheckCircle2,
  FileCheck2,
  Medal,
  ReceiptText,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
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

function PromotionCasePage({ packet, page }) {
  const target = packet?.target ?? {};
  const scorecard = packet?.scorecard ?? {};
  const targetText = [target.role, target.level].filter(Boolean).join(" · ");

  return (
    <section className="packet-sheet packet-document-page packet-summary-page">
      <PacketHeader index={2} eyebrow="Promotion Case" title="The evidence-backed progression case" />

      <div className="packet-result-hero">
        <TrendingUp size={24} />
        <div>
          <strong>{targetText || "Next step"}</strong>
          <span>user-defined progression target</span>
        </div>
      </div>

      <section className="packet-summary-narrative">
        <Medal size={26} />
        <div>
          <p className="packet-section-kicker">Case summary</p>
          <p>{packet?.promotion_summary}</p>
        </div>
      </section>

      <div className="packet-kpi-ribbon">
        <div><strong>{scorecard.receipt_coverage_percent ?? 0}%</strong><span>Structured proof</span></div>
        <div><strong>{scorecard.quantified_result_coverage_percent ?? 0}%</strong><span>Measurable impact</span></div>
        <div><strong>{scorecard.verification_coverage_percent ?? 0}%</strong><span>Verified recognition</span></div>
      </div>

      <div className="packet-document-note">
        <strong>No black-box readiness score</strong>
        <p>
          BragStack organizes the case and the receipts. It does not decide whether
          someone is ready for promotion, assign job level, or make an employment decision.
        </p>
      </div>

      <PacketFooter page={page} />
    </section>
  );
}

function DemonstratedImpactPage({ packet, page }) {
  const items = packet?.promotion_case?.demonstrated_impact ?? [];

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={3} eyebrow="Demonstrated Impact" title="The work supporting progression" />
      <p className="packet-page-lead">
        High-value examples are prioritized using documented results, structured proof,
        evidence, and confirmation signals—not profession-specific assumptions.
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
        <EmptyState>Add accomplishments with outcomes to build the demonstrated-impact case.</EmptyState>
      )}

      <PacketFooter page={page} />
    </section>
  );
}

function ScopeOwnershipPage({ packet, page }) {
  const records = packet?.promotion_case?.scope_and_ownership ?? [];

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={4} eyebrow="Scope & Ownership" title="How responsibility shows up in the record" />
      <p className="packet-page-lead">
        This section focuses on what the person actually carried, changed, coordinated,
        improved, delivered, taught, served, created, or led—across any kind of career.
      </p>

      {records.length ? (
        <div className="packet-contribution-list">
          {records.slice(0, 7).map((item) => (
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
        <EmptyState>Create Impact Receipts to make scope and ownership easier to review.</EmptyState>
      )}

      <PacketFooter page={page} />
    </section>
  );
}

function GrowthRecognitionPage({ packet, page }) {
  const skills = packet?.promotion_case?.growth_and_capabilities ?? [];
  const recognition = packet?.promotion_case?.verified_recognition ?? [];
  const maxCount = Math.max(...skills.map((item) => Number(item.count) || 0), 1);

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={5} eyebrow="Growth & Recognition" title="Capabilities demonstrated and independently confirmed" />

      <div className="packet-document-two-column">
        <section className="packet-document-section compact">
          <div className="packet-document-section-title">
            <div><p>Growth</p><h3>Demonstrated capabilities</h3></div>
            <Sparkles size={19} />
          </div>

          {skills.length ? (
            <div className="packet-skill-evidence-list">
              {skills.slice(0, 7).map((item, index) => (
                <article key={item.skill}>
                  <div className="packet-skill-rank">{index + 1}</div>
                  <div className="packet-skill-main">
                    <div><strong>{item.skill}</strong><span>{item.count} documented use{item.count === 1 ? "" : "s"}</span></div>
                    <div className="packet-skill-track"><span style={{ width: `${Math.max(8, (item.count / maxCount) * 100)}%` }} /></div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <EmptyState>Add skills to work records to build this section.</EmptyState>
          )}
        </section>

        <section className="packet-document-section compact">
          <div className="packet-document-section-title">
            <div><p>Recognition</p><h3>Confirmed contributions</h3></div>
            <BadgeCheck size={19} />
          </div>

          {recognition.length ? (
            <div className="packet-contribution-list">
              {recognition.slice(0, 5).map((item) => (
                <article key={item.reference}>
                  <div className="packet-contribution-topline">
                    <span>{item.reference}</span>
                    <span className="packet-verified-chip"><BadgeCheck size={12} /> Confirmed</span>
                  </div>
                  <h3>{item.accomplishment}</h3>
                  <div className="packet-contribution-meta">
                    {item.confirmations?.filter((confirmation) => confirmation.status === "confirmed").slice(0, 2).map((confirmation) => (
                      <span key={`${item.reference}-${confirmation.name}`}>
                        {confirmation.name}{confirmation.role ? ` · ${confirmation.role}` : ""}
                      </span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <EmptyState>Independent confirmation is optional; confirmed accomplishments will appear here.</EmptyState>
          )}
        </section>
      </div>

      <PacketFooter page={page} />
    </section>
  );
}

function StrengthenCasePage({ packet, page }) {
  const actions = packet?.promotion_case?.strengthening_actions ?? [];
  const results = packet?.promotion_case?.measurable_impact ?? [];

  return (
    <section className="packet-sheet packet-document-page">
      <PacketHeader index={6} eyebrow="Strengthen the Case" title="Useful next proof—not a verdict" />

      <div className="packet-result-hero">
        <Target size={24} />
        <div>
          <strong>{results.length}</strong>
          <span>documented measurable result{results.length === 1 ? "" : "s"} in this case</span>
        </div>
      </div>

      {actions.length ? (
        <div className="packet-accomplishment-list">
          {actions.map((item, index) => (
            <article className="packet-accomplishment-record" key={`${item.area}-${index}`}>
              <div className="packet-accomplishment-number">{String(index + 1).padStart(2, "0")}</div>
              <div>
                <p className="packet-section-kicker">{item.area}</p>
                <h3>{item.action}</h3>
                <p>{item.why}</p>
              </div>
              <div className="packet-record-proof">
                <FileCheck2 size={18} />
                <span>Next proof</span>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState>The current documentation already covers the main evidence-health areas.</EmptyState>
      )}

      <div className="packet-document-note">
        <strong>Keep expectations explicit</strong>
        <p>
          A strong evidence record should still be compared with the actual promotion,
          licensure, grade, scope, or progression expectations used by the organization or profession.
        </p>
      </div>

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
  const pages = chunk(packet?.receipt_records ?? [], 2);
  return pages.map((items, index) => (
    <section key={`promotion-receipt-${index}`} className="packet-sheet packet-document-page">
      <PacketHeader index={7} eyebrow="Impact Receipts" title={index === 0 ? "Receipts behind the case" : "Impact Receipts · continued"} />
      <p className="packet-page-lead">
        The promotion narrative stays traceable to the same contribution, result,
        skill, evidence, credit, and confirmation records used elsewhere in BragStack.
      </p>
      {items.length ? (
        <div className="packet-receipt-stack">
          {items.map((receipt) => <ImpactReceiptCard key={receipt.reference} receipt={receipt} />)}
        </div>
      ) : (
        <EmptyState>Create Impact Receipts to add structured proof to the promotion case.</EmptyState>
      )}
      <PacketFooter page={startPage + index} />
    </section>
  ));
}

function EvidencePages({ packet, startPage }) {
  const pages = chunk(packet?.evidence_index ?? [], 10);
  return pages.map((items, index) => (
    <section key={`promotion-evidence-${index}`} className="packet-sheet packet-document-page">
      <PacketHeader index={8} eyebrow="Evidence Index" title={index === 0 ? "Source material behind the case" : "Evidence Index · continued"} />
      {items.length ? (
        <div className="packet-evidence-table" role="table" aria-label="Promotion evidence index">
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
        <EmptyState>Add evidence to Impact Receipts to populate the source index.</EmptyState>
      )}
      <PacketFooter page={startPage + index} />
    </section>
  ));
}

function ConversationSummaryPage({ packet, page }) {
  const points = packet?.talking_points ?? [];
  return (
    <section className="packet-sheet packet-document-page packet-summary-page">
      <PacketHeader index={9} eyebrow="Conversation Summary" title="Use the proof—keep the decision human" />

      <section className="packet-summary-narrative">
        <Award size={26} />
        <div>
          <p className="packet-section-kicker">Promotion case summary</p>
          <p>{packet?.promotion_summary}</p>
        </div>
      </section>

      <section className="packet-talking-points">
        <div className="packet-document-section-title">
          <div><p>Conversation guide</p><h3>Promotion talking points</h3></div>
          <UsersRound size={19} />
        </div>
        {points.length ? (
          <ol>
            {points.map((item) => (
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
          <strong>Bring the receipts. Make the case.</strong>
          <p>
            Every claim should be traceable to documented work. The final promotion
            decision remains with the people and process responsible for it.
          </p>
        </div>
      </div>

      <PacketFooter page={page} />
    </section>
  );
}

function PromotionPacketPages({ packet }) {
  const receiptPageCount = Math.max(1, Math.ceil((packet?.receipt_records?.length ?? 0) / 2));
  const evidencePageCount = Math.max(1, Math.ceil((packet?.evidence_index?.length ?? 0) / 10));
  const receiptStartPage = 8;
  const evidenceStartPage = receiptStartPage + receiptPageCount;
  const summaryPage = evidenceStartPage + evidencePageCount;

  return (
    <>
      <PromotionCasePage packet={packet} page={3} />
      <DemonstratedImpactPage packet={packet} page={4} />
      <ScopeOwnershipPage packet={packet} page={5} />
      <GrowthRecognitionPage packet={packet} page={6} />
      <StrengthenCasePage packet={packet} page={7} />
      <ReceiptPages packet={packet} startPage={receiptStartPage} />
      <EvidencePages packet={packet} startPage={evidenceStartPage} />
      <ConversationSummaryPage packet={packet} page={summaryPage} />
    </>
  );
}

export default PromotionPacketPages;
