import {
  BadgeCheck,
  BookOpenCheck,
  Building2,
  FileBadge2,
  GraduationCap,
  ShieldCheck,
} from "lucide-react";

import "./PerformancePacketPages.css";
import "./CertificationPacketPages.css";

function PacketFooter({ page }) {
  return (
    <footer className="packet-page-footer">
      <span>BragStack · Career Evidence System</span>
      <span>Page {page}</span>
    </footer>
  );
}

function PacketHeader({ index, eyebrow, title }) {
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

function StatusChip({ status }) {
  const normalized = (status || "Self-added").toLowerCase().replace(/\s+/g, "-");
  return <span className={`credential-status-chip ${normalized}`}>{status || "Self-added"}</span>;
}

function CertificationPacketPages({ packet }) {
  const review = packet?.credential_review ?? {};
  const summary = packet?.credential_evidence_summary ?? {};
  const credentialEvidence = packet?.credential_evidence ?? [];
  const competencies = packet?.competency_records ?? [];
  const experience = packet?.experience_records ?? [];
  const supportingEvidence = packet?.supporting_evidence ?? [];

  return (
    <>
      <section className="packet-sheet packet-document-page">
        <PacketHeader index={2} eyebrow="Credential Review" title="What this packet is supporting" />

        <div className="credential-review-hero">
          <FileBadge2 size={28} />
          <div>
            <span>{review.review_type || "Certification / Licensure Review"}</span>
            <h3>{review.credential_name || "Credential review"}</h3>
            {review.issuing_body && <p><Building2 size={14} /> {review.issuing_body}</p>}
          </div>
        </div>

        <div className="packet-kpi-ribbon credential-kpi-ribbon">
          <div><strong>{summary.credential_items ?? 0}</strong><span>Credential records</span></div>
          <div><strong>{summary.self_added ?? 0}</strong><span>Self-added</span></div>
          <div><strong>{summary.confirmed ?? 0}</strong><span>Confirmed</span></div>
          <div><strong>{summary.organization_issued ?? 0}</strong><span>Organization-issued</span></div>
        </div>

        <div className="credential-trust-note">
          <ShieldCheck size={20} />
          <p>
            Evidence labels describe the trust signals attached inside BragStack. A self-added certificate or license is not presented as independently verified merely because a file or reference exists.
          </p>
        </div>

        {review.requirement_notes && (
          <section className="credential-requirements-card">
            <span>Review requirements / notes</span>
            <p>{review.requirement_notes}</p>
          </section>
        )}

        <PacketFooter page={3} />
      </section>

      <section className="packet-sheet packet-document-page">
        <PacketHeader index={3} eyebrow="Credential Evidence" title="Certificates, licenses & continuing education" />

        {credentialEvidence.length ? (
          <div className="credential-evidence-list">
            {credentialEvidence.map((item, index) => (
              <article key={`${item.receipt_reference}-${item.title}-${index}`}>
                <div className="credential-evidence-topline">
                  <span>{item.type || "Evidence"}</span>
                  <StatusChip status={item.evidence_status} />
                </div>
                <h3>{item.title || "Credential evidence"}</h3>
                {item.description && <p>{item.description}</p>}
                {item.reference && <small>{item.reference}</small>}
              </article>
            ))}
          </div>
        ) : (
          <EmptyState>
            No evidence item is currently categorized as a certificate, license, credential, or continuing-education record for this period.
          </EmptyState>
        )}

        <PacketFooter page={4} />
      </section>

      <section className="packet-sheet packet-document-page">
        <PacketHeader index={4} eyebrow="Competencies" title="Capabilities demonstrated in the review period" />

        {competencies.length ? (
          <div className="packet-skill-evidence-list">
            {competencies.slice(0, 18).map((item, index) => (
              <article key={item.skill}>
                <div className="packet-skill-rank">{index + 1}</div>
                <div className="packet-skill-main">
                  <div>
                    <strong>{item.skill}</strong>
                    <span>{item.count} documented demonstration{item.count === 1 ? "" : "s"}</span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState>Add skills to accomplishments or Impact Receipts to build a competency record.</EmptyState>
        )}

        <PacketFooter page={5} />
      </section>

      <section className="packet-sheet packet-document-page">
        <PacketHeader index={5} eyebrow="Experience Record" title="Accomplishments supporting the credential review" />

        {experience.length ? (
          <div className="credential-experience-list">
            {experience.slice(0, 14).map((item, index) => (
              <article key={`${item.reference}-${index}`}>
                <div>
                  <span>{item.entry_date || "Documented experience"}</span>
                  {item.verified && <span className="packet-verified-chip"><BadgeCheck size={12} /> Confirmed</span>}
                </div>
                <h3>{item.accomplishment}</h3>
                {item.contribution && <p>{item.contribution}</p>}
                {item.result && <p><strong>Result:</strong> {item.result}</p>}
              </article>
            ))}
          </div>
        ) : (
          <EmptyState>No experience records are documented for this review period yet.</EmptyState>
        )}

        <PacketFooter page={6} />
      </section>

      <section className="packet-sheet packet-document-page">
        <PacketHeader index={6} eyebrow="Evidence Index" title="Supporting records & trust status" />

        {supportingEvidence.length ? (
          <div className="credential-index-list">
            {supportingEvidence.slice(0, 24).map((item, index) => (
              <article key={`${item.receipt_reference}-${item.title}-${index}`}>
                <FileBadge2 size={17} />
                <div>
                  <strong>{item.title || "Evidence item"}</strong>
                  <span>{item.type || "Evidence"} · {item.receipt_reference || "Receipt"}</span>
                  {item.reference && <small>{item.reference}</small>}
                </div>
                <StatusChip status={item.evidence_status} />
              </article>
            ))}
          </div>
        ) : (
          <EmptyState>No supporting evidence is attached for this review period yet.</EmptyState>
        )}

        <section className="packet-summary-narrative credential-summary-narrative">
          <GraduationCap size={26} />
          <div>
            <p className="packet-section-kicker">Credential review summary</p>
            <p>{packet?.review_summary}</p>
          </div>
        </section>

        <PacketFooter page={7} />
      </section>
    </>
  );
}

export default CertificationPacketPages;
