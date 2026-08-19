import { useState } from "react";
import {
  ArrowLeft,
  Award,
  BarChart3,
  Download,
  FileText,
  Layers3,
  Printer,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import {
  downloadCertificationPacketPdf,
  downloadInterviewPacketPdf,
  downloadPerformancePacketPdf,
  downloadPromotionPacketPdf,
} from "./api";
import CertificationPacketPages from "./CertificationPacketPages";
import InterviewPacketPages from "./InterviewPacketPages";
import PerformancePacketPages from "./PerformancePacketPages";
import PromotionPacketPages from "./PromotionPacketPages";
import "./PerformancePacketPreview.css";
import "./PerformancePacketExport.css";

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function formatPeriod(period = {}) {
  if (period.start_date && period.end_date) {
    return `${formatDate(`${period.start_date}T12:00:00`)} — ${formatDate(`${period.end_date}T12:00:00`)}`;
  }
  return "All recorded work";
}

function CoverageRow({ label, value, note }) {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div className="packet-coverage-row">
      <div className="packet-coverage-copy">
        <div><strong>{label}</strong><span>{note}</span></div>
        <b>{safeValue}%</b>
      </div>
      <div className="packet-coverage-track" aria-hidden="true"><span style={{ width: `${safeValue}%` }} /></div>
    </div>
  );
}

function RankedList({ title, items }) {
  const entries = Object.entries(items ?? {}).slice(0, 5);
  const highest = entries[0]?.[1] || 1;
  return (
    <div className="packet-ranked-card">
      <p className="packet-section-kicker">{title}</p>
      {entries.length ? (
        <div className="packet-ranked-list">
          {entries.map(([label, count]) => (
            <div key={label}>
              <div className="packet-ranked-copy"><span>{label}</span><strong>{count}</strong></div>
              <div className="packet-ranked-track" aria-hidden="true"><span style={{ width: `${Math.max(12, (count / highest) * 100)}%` }} /></div>
            </div>
          ))}
        </div>
      ) : (
        <p className="packet-empty-copy">Add accomplishments and skills to build this view.</p>
      )}
    </div>
  );
}

function PacketFooter({ page }) {
  return <footer className="packet-page-footer"><span>BragStack · Career Evidence System</span><span>Page {page}</span></footer>;
}

function PerformancePacketPreview({ packet, onBack }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState("");
  const scorecard = packet?.scorecard ?? {};
  const subject = packet?.subject ?? {};
  const context = packet?.context ?? {};
  const target = packet?.target ?? {};
  const credentialReview = packet?.credential_review ?? {};
  const topSignature = packet?.signature_accomplishments?.[0];
  const generatedDate = formatDate(packet?.generated_at);
  const isPromotion = packet?.kind === "promotion";
  const isInterview = packet?.kind === "interview";
  const isCertification = packet?.kind === "certification";
  const packetTitle = packet?.title || "Performance Review Packet";
  const targetText = isInterview
    ? [target.role, target.organization].filter(Boolean).join(" · ")
    : [target.role, target.level].filter(Boolean).join(" · ");
  const credentialTargetText = [credentialReview.credential_name, credentialReview.issuing_body]
    .filter(Boolean)
    .join(" · ");

  async function handleDownloadPdf() {
    setIsDownloading(true);
    setDownloadError("");
    try {
      const downloader = isCertification
        ? downloadCertificationPacketPdf
        : isInterview
          ? downloadInterviewPacketPdf
          : isPromotion
            ? downloadPromotionPacketPdf
            : downloadPerformancePacketPdf;
      const { blob, filename } = await downloader(packet);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      if (error.response?.status === 401) {
        localStorage.removeItem("bragstack_token");
        window.location.href = "/login";
        return;
      }
      setDownloadError(
        error.response?.status === 403
          ? "PDF export is included with BragStack Pro and higher plans."
          : "The PDF could not be generated. Try again or use Print as a fallback."
      );
    } finally {
      setIsDownloading(false);
    }
  }

  const scorecardLabel = isPromotion
    ? "Promotion Evidence Scorecard"
    : isInterview
      ? "Interview Story Scorecard"
      : isCertification
        ? "Credential Evidence Scorecard"
        : "Executive Scorecard";
  const scorecardTitle = isPromotion
    ? "The proof behind the case"
    : isInterview
      ? "The stories you chose"
      : isCertification
        ? "Evidence for the review"
        : "Proof at a glance";
  const scorecardIntro = isPromotion
    ? "A transparent view of the documentation supporting this progression conversation. These measures describe the evidence record; they do not calculate promotion readiness."
    : isInterview
      ? "A transparent view of the accomplishments selected for interview preparation. Coverage measures describe documented story quality; missing details become prep prompts instead of invented answers."
      : isCertification
        ? "A transparent view of the work and evidence supporting this credential review. BragStack distinguishes self-added, confirmed, and organization-issued evidence instead of treating every uploaded credential as verified."
        : "A transparent summary of documented work for this review period. Coverage measures are calculated from actual accomplishments, Impact Receipts, evidence, and confirmations—not an opaque AI score.";

  return (
    <main className="packet-preview-shell">
      <header className="packet-preview-toolbar">
        <button type="button" onClick={onBack}><ArrowLeft size={17} />Back to reports</button>
        <div><span>{packetTitle}</span><strong>Physical dossier preview</strong></div>
        <span className="packet-preview-toolbar-actions">
          <button type="button" onClick={() => window.print()}><Printer size={17} />Print</button>
          <button type="button" className="packet-download-button" onClick={() => void handleDownloadPdf()} disabled={isDownloading}>
            <Download size={17} />{isDownloading ? "Building PDF..." : "Download PDF"}
          </button>
        </span>
      </header>

      {downloadError && <p className="packet-preview-download-error" role="alert">{downloadError}</p>}

      <div className="packet-paper-stack">
        <section className="packet-sheet packet-cover" aria-label="Packet cover">
          <div className="packet-cover-topline">
            <div className="packet-wordmark"><span className="packet-wordmark-mark">B</span><span>BRAGSTACK</span></div>
            <span className="packet-confidential">{packet?.confidential ? "Confidential · Professional development record" : "Professional development record"}</span>
          </div>

          <div className="packet-cover-main">
            <p className="packet-document-type">{packetTitle}</p>
            <h1>{subject.name || "BragStack Member"}</h1>
            <h2>{subject.role || "Professional"}</h2>
            {context.organization && <p className="packet-cover-context">{context.organization}</p>}
            {context.career_area && <p className="packet-cover-context">{context.career_area}</p>}
            {subject.location && <p className="packet-location">{subject.location}</p>}
            <div className="packet-cover-rule" />

            {(isPromotion || isInterview) && targetText && (
              <div className="packet-period-block"><span>{isInterview ? "Interview target" : "Progression target"}</span><strong>{targetText}</strong></div>
            )}
            {isCertification && credentialTargetText && (
              <div className="packet-period-block"><span>{credentialReview.review_type || "Credential review"}</span><strong>{credentialTargetText}</strong></div>
            )}

            <div className="packet-period-block"><span>Review period</span><strong>{formatPeriod(packet?.period)}</strong></div>

            <div className="packet-cover-stats">
              <div><strong>{scorecard.accomplishments ?? 0}</strong><span>{isInterview ? "Selected stories" : "Documented accomplishments"}</span></div>
              <div><strong>{scorecard.impact_receipts ?? 0}</strong><span>Impact Receipts</span></div>
              <div><strong>{scorecard.evidence_items ?? 0}</strong><span>Evidence items</span></div>
            </div>
          </div>

          <div className="packet-cover-bottom">
            <div><span>Prepared</span><strong>{generatedDate || "Today"}</strong></div>
            <div className="packet-cover-proofline"><ShieldCheck size={16} /><span>Evidence-backed career record generated from BragStack</span></div>
          </div>
          <PacketFooter page={1} />
        </section>

        <section className="packet-sheet packet-scorecard-page" aria-label={scorecardLabel}>
          <header className="packet-page-header">
            <div><p>01 · {scorecardLabel}</p><h2>{scorecardTitle}</h2></div>
            <div className="packet-page-header-mark">BRAGSTACK</div>
          </header>

          <p className="packet-scorecard-intro">{scorecardIntro}</p>

          <section className="packet-stat-grid" aria-label="Packet totals">
            <article><FileText size={19} /><span>{isInterview ? "Selected Stories" : "Accomplishments"}</span><strong>{scorecard.accomplishments ?? 0}</strong></article>
            <article><Sparkles size={19} /><span>Impact Receipts</span><strong>{scorecard.impact_receipts ?? 0}</strong></article>
            <article><ShieldCheck size={19} /><span>Evidence Items</span><strong>{scorecard.evidence_items ?? 0}</strong></article>
            <article><Layers3 size={19} /><span>Skills Demonstrated</span><strong>{scorecard.skills_demonstrated ?? 0}</strong></article>
          </section>

          <section className="packet-scorecard-section">
            <div className="packet-section-heading"><div><p className="packet-section-kicker">Evidence health</p><h3>{isInterview ? "Story coverage" : "Documentation coverage"}</h3></div><BarChart3 size={20} /></div>
            <div className="packet-coverage-list">
              <CoverageRow label="Impact Receipt coverage" value={scorecard.receipt_coverage_percent} note={isInterview ? "Selected stories with structured proof" : "Accomplishments converted into structured proof"} />
              <CoverageRow label="Quantified result coverage" value={scorecard.quantified_result_coverage_percent} note={isInterview ? "Selected stories containing a measurable result" : "Receipts containing a measurable result"} />
              <CoverageRow label="Evidence coverage" value={scorecard.evidence_coverage_percent} note={isInterview ? "Selected stories supported by evidence" : "Receipts supported by at least one evidence item"} />
              <CoverageRow label="Verification coverage" value={scorecard.verification_coverage_percent} note={isInterview ? "Selected stories with a confirmed contribution" : "Receipts with a confirmed contribution"} />
            </div>
            <div className="packet-evidence-depth"><span>Evidence depth</span><strong>{scorecard.evidence_depth ?? 0}×</strong><p>Average supporting evidence items per Impact Receipt.</p></div>
          </section>

          <section className="packet-ranked-grid">
            <RankedList title="Most demonstrated skills" items={packet?.impact_analytics?.top_skills} />
            <RankedList title={isInterview ? "Selected story themes" : "Work themes"} items={packet?.impact_analytics?.categories} />
          </section>

          <section className="packet-signature-callout">
            <div className="packet-signature-icon"><Award size={21} /></div>
            <div>
              <p className="packet-section-kicker">{isPromotion ? "Promotion evidence highlight" : isInterview ? "Interview story highlight" : isCertification ? "Credential-supporting accomplishment" : "Signature accomplishment"}</p>
              {topSignature ? (
                <><h3>{topSignature.title}</h3>{topSignature.result && <p>{topSignature.result}</p>}</>
              ) : (
                <><h3>Your strongest proof will appear here.</h3><p>Add an accomplishment with a clear result and Impact Receipt to strengthen this packet.</p></>
              )}
            </div>
          </section>
          <PacketFooter page={2} />
        </section>

        {isPromotion ? (
          <PromotionPacketPages packet={packet} />
        ) : isInterview ? (
          <InterviewPacketPages packet={packet} />
        ) : isCertification ? (
          <CertificationPacketPages packet={packet} />
        ) : (
          <PerformancePacketPages packet={packet} />
        )}
      </div>
    </main>
  );
}

export default PerformancePacketPreview;
