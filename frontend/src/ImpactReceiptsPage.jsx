import { useEffect, useMemo, useState } from "react";
import { ExternalLink, ReceiptText, ShieldCheck } from "lucide-react";

import { getImpactReceipts, updateImpactReceipt } from "./api";

function formatLabel(value = "") {
  return value
    .replace(/-/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function ImpactReceiptsPage() {
  const [receipts, setReceipts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState(null);

  async function loadReceipts() {
    try {
      const data = await getImpactReceipts();
      setReceipts(data.receipts ?? []);
      setError("");
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("bragstack_token");
        window.location.assign("/login");
        return;
      }
      setError("Impact Receipts could not be loaded.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadReceipts();
    }, 0);

    return () => window.clearTimeout(timeoutId);
  }, []);

  const stats = useMemo(() => {
    const publicCount = receipts.filter((receipt) => receipt.is_public).length;
    const evidenceCount = receipts.reduce(
      (total, receipt) => total + (receipt.evidence?.length ?? 0),
      0,
    );
    const confirmedCount = receipts.reduce(
      (total, receipt) =>
        total +
        (receipt.confirmations?.filter(
          (confirmation) => confirmation.status === "confirmed",
        ).length ?? 0),
      0,
    );

    return { publicCount, evidenceCount, confirmedCount };
  }, [receipts]);

  async function toggleVisibility(receipt) {
    setUpdatingId(receipt.id);
    try {
      await updateImpactReceipt(receipt.id, {
        is_public: !receipt.is_public,
      });
      await loadReceipts();
    } catch (err) {
      setError(
        err.response?.data?.detail ?? "Receipt visibility could not be changed.",
      );
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <main className="product-page receipt-library-page">
      <section className="product-page-hero">
        <div>
          <p className="mini-label">Evidence-backed career proof</p>
          <h1>Impact Receipts</h1>
          <p>
            Your strongest accomplishments, packaged with contribution, result,
            evidence, skills, and trust signals.
          </p>
        </div>
        <a className="product-page-link" href="/app/accomplishments">
          Create from an accomplishment <ExternalLink size={16} />
        </a>
      </section>

      <section className="receipt-kpi-grid">
        <article>
          <ReceiptText size={20} />
          <span>Total receipts</span>
          <strong>{receipts.length}</strong>
        </article>
        <article>
          <ShieldCheck size={20} />
          <span>Public receipts</span>
          <strong>{stats.publicCount}</strong>
        </article>
        <article>
          <span className="receipt-kpi-dot" />
          <span>Evidence items</span>
          <strong>{stats.evidenceCount}</strong>
        </article>
        <article>
          <span className="receipt-kpi-dot" />
          <span>Confirmed signals</span>
          <strong>{stats.confirmedCount}</strong>
        </article>
      </section>

      {error && <div className="product-alert error">{error}</div>}

      {isLoading ? (
        <section className="product-empty">Loading Impact Receipts…</section>
      ) : receipts.length === 0 ? (
        <section className="product-empty">
          <h2>No receipts yet.</h2>
          <p>
            Turn a meaningful accomplishment into a receipt to start building
            portable evidence of your work.
          </p>
          <a href="/app/accomplishments">Browse accomplishments</a>
        </section>
      ) : (
        <section className="receipt-library-grid">
          {receipts.map((receipt) => (
            <article className="receipt-library-card" key={receipt.id}>
              <div className="receipt-library-card-top">
                <div>
                  <p className="mini-label">Impact Receipt</p>
                  <h2>{receipt.accomplishment}</h2>
                </div>
                <button
                  type="button"
                  className={`visibility-pill ${
                    receipt.is_public ? "public" : "private"
                  }`}
                  disabled={updatingId === receipt.id}
                  onClick={() => toggleVisibility(receipt)}
                >
                  {updatingId === receipt.id
                    ? "Saving…"
                    : receipt.is_public
                      ? "Public"
                      : "Private"}
                </button>
              </div>

              <div className="receipt-proof-columns">
                <div>
                  <span>Contribution</span>
                  <p>{receipt.contribution}</p>
                </div>
                <div>
                  <span>Result</span>
                  <p>{receipt.result}</p>
                </div>
              </div>

              <div className="receipt-signal-row">
                <span>{receipt.evidence?.length ?? 0} evidence</span>
                <span>{receipt.skills?.length ?? 0} skills</span>
                <span>{receipt.credit?.length ?? 0} contributors</span>
              </div>

              {receipt.skills?.length > 0 && (
                <div className="receipt-chip-row">
                  {receipt.skills.map((skill) => (
                    <span key={`${receipt.id}-${skill}`}>{skill}</span>
                  ))}
                </div>
              )}

              {receipt.trust_signals?.length > 0 && (
                <div className="receipt-trust-row">
                  {receipt.trust_signals.map((signal) => (
                    <span key={`${receipt.id}-${signal}`}>
                      <ShieldCheck size={14} /> {formatLabel(signal)}
                    </span>
                  ))}
                </div>
              )}
            </article>
          ))}
        </section>
      )}
    </main>
  );
}

export default ImpactReceiptsPage;
