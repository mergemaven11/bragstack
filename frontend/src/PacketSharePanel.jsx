import { Copy, Link2, LockKeyhole, ShieldOff, Trash2 } from "lucide-react";
import { useState } from "react";

import { buildPacketShareUrl, createPacketShare, revokePacketShare } from "./api";
import "./PacketSharePanel.css";

function PacketSharePanel({ packet }) {
  const [expiresAt, setExpiresAt] = useState("");
  const [accessCode, setAccessCode] = useState("");
  const [allowDownload, setAllowDownload] = useState(false);
  const [includeEvidence, setIncludeEvidence] = useState(false);
  const [includeNotes, setIncludeNotes] = useState(false);
  const [share, setShare] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function handleCreate() {
    setIsSaving(true); setError(""); setNotice("");
    try {
      const data = await createPacketShare(packet, {
        expiresAt: expiresAt ? new Date(expiresAt).toISOString() : null,
        accessCode: accessCode.trim() || null,
        allowDownload,
        includeEvidence,
        includeNotes,
      });
      setShare(data.share);
      setNotice("Private share created. The token is only returned at creation time.");
    } catch (requestError) {
      console.error(requestError);
      setError(requestError.response?.data?.detail ?? "The private share could not be created.");
    } finally { setIsSaving(false); }
  }

  async function handleCopy() {
    if (!share?.path) return;
    const url = buildPacketShareUrl(share.path);
    try { await navigator.clipboard.writeText(url); setNotice("Share link copied."); }
    catch { setNotice("Copy was blocked by the browser. Select the link manually."); }
  }

  async function handleRevoke() {
    if (!share?.id) return;
    setIsSaving(true); setError("");
    try { await revokePacketShare(share.id); setShare(null); setNotice("Share revoked immediately."); }
    catch (requestError) { console.error(requestError); setError(requestError.response?.data?.detail ?? "The share could not be revoked."); }
    finally { setIsSaving(false); }
  }

  const shareUrl = share?.path ? buildPacketShareUrl(share.path) : "";

  return (
    <section className="packet-share-panel" aria-label="Private packet sharing">
      <div className="packet-share-heading"><Link2 size={18} /><div><strong>Private packet share</strong><span>Independent of your public Proof Profile</span></div></div>
      {!share ? (
        <>
          <div className="packet-share-grid">
            <label><span>Expires</span><input type="datetime-local" value={expiresAt} onChange={(event) => setExpiresAt(event.target.value)} /></label>
            <label><span>Optional access code</span><input type="password" value={accessCode} onChange={(event) => setAccessCode(event.target.value)} minLength={4} maxLength={64} placeholder="4+ characters" /></label>
          </div>
          <div className="packet-share-checks">
            <label><input type="checkbox" checked={allowDownload} onChange={(event) => setAllowDownload(event.target.checked)} /><span>Allow PDF download</span></label>
            <label><input type="checkbox" checked={includeEvidence} onChange={(event) => setIncludeEvidence(event.target.checked)} /><span>Include evidence references</span></label>
            <label><input type="checkbox" checked={includeNotes} onChange={(event) => setIncludeNotes(event.target.checked)} /><span>Include user-authored notes</span></label>
          </div>
          <p className="packet-share-privacy"><LockKeyhole size={14} /> Evidence and notes stay excluded unless you explicitly enable them. Revoked or expired links fail closed.</p>
          <button className="packet-share-create" type="button" onClick={() => void handleCreate()} disabled={isSaving}>{isSaving ? "Creating private link…" : "Create private share link"}</button>
        </>
      ) : (
        <div className="packet-share-created">
          <div><span>Private link</span><a href={shareUrl} target="_blank" rel="noreferrer">{shareUrl}</a></div>
          <p>{share.requires_access_code ? "Access code required · " : ""}{share.allow_download ? "PDF download allowed · " : "View only · "}{share.include_evidence ? "Evidence included" : "Evidence hidden"}</p>
          <div className="packet-share-actions"><button type="button" onClick={() => void handleCopy()}><Copy size={14} />Copy link</button><button type="button" className="danger" onClick={() => void handleRevoke()} disabled={isSaving}><Trash2 size={14} />Revoke now</button></div>
          <p className="packet-share-privacy"><ShieldOff size={14} /> Revocation takes effect immediately.</p>
        </div>
      )}
      {notice && <p className="packet-share-notice">{notice}</p>}
      {error && <p className="packet-share-error" role="alert">{String(error)}</p>}
    </section>
  );
}

export default PacketSharePanel;
