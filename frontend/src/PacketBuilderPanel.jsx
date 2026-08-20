import {
  ArrowDown,
  ArrowUp,
  BriefcaseBusiness,
  FileStack,
  Palette,
  Pin,
  ShieldCheck,
} from "lucide-react";

import "./PacketBuilderPanel.css";

const CAREER_AREAS = ["", "Healthcare", "Education", "Technology", "Sales", "Operations", "Skilled Trades", "Creative", "Customer Service", "Management", "Government", "Nonprofit", "Student", "Other"];
const PACKET_TYPES = [
  { value: "performance-review", label: "Performance Review Packet" },
  { value: "promotion", label: "Promotion Packet" },
  { value: "interview", label: "Interview Packet" },
  { value: "certification", label: "Certification & Licensure Packet" },
];
const CREDENTIAL_REVIEW_TYPES = ["Certification / Licensure Review", "License Renewal", "Certification Review", "Recertification", "Continuing Education Review", "Competency Review", "Other Credential Review"];
const PERFORMANCE_SECTIONS = [
  ["impact-analytics", "Impact Analytics"],
  ["signature-accomplishments", "Signature Accomplishments"],
  ["measurable-results", "Measurable Results"],
  ["skills-growth", "Skills & Growth"],
  ["contribution-recognition", "Contribution & Verified Recognition"],
  ["impact-receipts", "Impact Receipt appendix"],
  ["evidence-index", "Evidence Index"],
  ["review-summary", "Review Summary & talking points"],
];
const THEMES = [
  ["classic-dossier", "Classic dossier"],
  ["modern-minimal", "Modern minimal"],
  ["executive-report", "Executive annual-report"],
];

function PacketBuilderPanel({ options, onChange, onBuild, isLoading, error, highlights = [] }) {
  const packetType = options.packetType || "performance-review";
  const isPerformance = packetType === "performance-review";
  const isPromotion = packetType === "promotion";
  const isInterview = packetType === "interview";
  const isCertification = packetType === "certification";
  const selectedEntryIds = options.selectedEntryIds ?? [];
  const signatureEntryIds = options.signatureEntryIds ?? [];
  const selectedSections = options.sections ?? PERFORMANCE_SECTIONS.map(([key]) => key);

  function update(name, value) {
    onChange((current) => ({ ...current, [name]: value }));
  }

  function changePacketType(value) {
    onChange((current) => ({
      ...current,
      packetType: value,
      ...(value === "interview" && !(current.selectedEntryIds?.length)
        ? { selectedEntryIds: highlights.slice(0, 5).map((item) => item.entry_id).filter(Boolean) }
        : {}),
    }));
  }

  function toggleList(name, entryId, max = 8) {
    onChange((current) => {
      const selected = current[name] ?? [];
      if (selected.includes(entryId)) return { ...current, [name]: selected.filter((id) => id !== entryId) };
      if (selected.length >= max) return current;
      return { ...current, [name]: [...selected, entryId] };
    });
  }

  function moveSignature(entryId, direction) {
    onChange((current) => {
      const selected = [...(current.signatureEntryIds ?? [])];
      const index = selected.indexOf(entryId);
      const next = index + direction;
      if (index < 0 || next < 0 || next >= selected.length) return current;
      [selected[index], selected[next]] = [selected[next], selected[index]];
      return { ...current, signatureEntryIds: selected };
    });
  }

  function toggleSection(section) {
    onChange((current) => {
      const selected = current.sections ?? PERFORMANCE_SECTIONS.map(([key]) => key);
      return {
        ...current,
        sections: selected.includes(section)
          ? selected.filter((value) => value !== section)
          : PERFORMANCE_SECTIONS.map(([key]) => key).filter((value) => [...selected, section].includes(value)),
      };
    });
  }

  function setItemNote(entryId, note) {
    onChange((current) => ({
      ...current,
      itemNotes: { ...(current.itemNotes ?? {}), [entryId]: note },
    }));
  }

  const title = isPromotion ? "Promotion Packet" : isInterview ? "Interview Packet" : isCertification ? "Certification & Licensure Packet" : "Performance Review Packet";
  const description = isPromotion
    ? "Organize documented impact, increased responsibility, growth, recognition, and supporting evidence into a professional promotion case—without inventing a readiness score."
    : isInterview
      ? "Select the accomplishments you want to talk about, turn them into evidence-backed interview stories, and surface prep questions wherever your record is missing context."
      : isCertification
        ? "Organize credentials, continuing education, demonstrated competencies, experience, and supporting evidence for certification, licensure, renewal, or regulated-career reviews—without calling self-added proof verified."
        : "Build a tailored physical dossier. Pin the work that matters, choose sections, add clearly labeled context, and select a professional print theme without changing the underlying evidence metrics.";

  return (
    <section className="packet-builder-pro" aria-labelledby="packet-builder-title">
      <div className="packet-builder-pro-header">
        <div className="packet-builder-pro-icon"><FileStack size={22} /></div>
        <div><span>BragStack Pro · Premium Artifact</span><h2 id="packet-builder-title">Build {isInterview ? "an" : "a"} {title}</h2><p>{description}</p></div>
      </div>

      <div className="packet-builder-fields">
        <label><span>Packet type</span><select value={packetType} onChange={(event) => changePacketType(event.target.value)}>{PACKET_TYPES.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}</select></label>
        <label><span>Career / work area</span><select value={options.careerArea ?? ""} onChange={(event) => update("careerArea", event.target.value)}>{CAREER_AREAS.map((area) => <option key={area || "neutral"} value={area}>{area || "Career-neutral"}</option>)}</select></label>
        <label><span>Current role title</span><input type="text" value={options.roleTitle ?? ""} onChange={(event) => update("roleTitle", event.target.value)} placeholder="Use profile headline" maxLength={160} /></label>
        <label><span>Organization / team</span><input type="text" value={options.organization ?? ""} onChange={(event) => update("organization", event.target.value)} placeholder="Optional" maxLength={180} /></label>

        {isPromotion && <><label><span>Target role</span><input value={options.targetRole ?? ""} onChange={(event) => update("targetRole", event.target.value)} placeholder="Senior Manager, Lead Teacher, RN II" maxLength={160} /></label><label><span>Target level / progression</span><input value={options.targetLevel ?? ""} onChange={(event) => update("targetLevel", event.target.value)} placeholder="Optional level, grade, or step" maxLength={120} /></label></>}
        {isInterview && <><label><span>Target role</span><input value={options.targetRole ?? ""} onChange={(event) => update("targetRole", event.target.value)} placeholder="Assistant Principal, Store Manager, Designer" maxLength={160} /></label><label><span>Target organization</span><input value={options.targetOrganization ?? ""} onChange={(event) => update("targetOrganization", event.target.value)} placeholder="Optional employer" maxLength={180} /></label></>}
        {isCertification && <><label><span>Credential / license name</span><input value={options.credentialName ?? ""} onChange={(event) => update("credentialName", event.target.value)} placeholder="RN License Renewal, OSHA 30, Teaching Certificate" maxLength={180} /></label><label><span>Issuing / reviewing body</span><input value={options.issuingBody ?? ""} onChange={(event) => update("issuingBody", event.target.value)} placeholder="Board, agency, association, employer..." maxLength={180} /></label><label><span>Review type</span><select value={options.reviewType ?? CREDENTIAL_REVIEW_TYPES[0]} onChange={(event) => update("reviewType", event.target.value)}>{CREDENTIAL_REVIEW_TYPES.map((type) => <option key={type}>{type}</option>)}</select></label><label className="packet-builder-wide-field"><span>Requirements / notes</span><textarea value={options.requirementNotes ?? ""} onChange={(event) => update("requirementNotes", event.target.value)} placeholder="Optional renewal requirements or documents to include." maxLength={1200} rows={3} /></label></>}
      </div>

      {isPerformance && (
        <div className="packet-platform-grid">
          <section className="packet-platform-panel">
            <div className="packet-platform-heading"><Pin size={17} /><div><strong>Pin signature accomplishments</strong><span>Optional · auto-ranking stays the default</span></div></div>
            <p className="packet-platform-help">Select up to 8. The order below becomes the order in preview and PDF; source records are untouched.</p>
            <div className="packet-story-options packet-signature-options">
              {highlights.map((highlight) => {
                const selected = signatureEntryIds.includes(highlight.entry_id);
                const selectedIndex = signatureEntryIds.indexOf(highlight.entry_id);
                return (
                  <div key={highlight.entry_id} className={`packet-signature-option ${selected ? "selected" : ""}`}>
                    <label><input type="checkbox" checked={selected} disabled={!selected && signatureEntryIds.length >= 8} onChange={() => toggleList("signatureEntryIds", highlight.entry_id)} /><span><strong>{highlight.title}</strong><small>{highlight.category || "Accomplishment"}{highlight.result ? ` · ${highlight.result}` : ""}</small></span></label>
                    {selected && <div className="packet-reorder"><button type="button" disabled={selectedIndex === 0} onClick={() => moveSignature(highlight.entry_id, -1)} aria-label="Move up"><ArrowUp size={14} /></button><span>{selectedIndex + 1}</span><button type="button" disabled={selectedIndex === signatureEntryIds.length - 1} onClick={() => moveSignature(highlight.entry_id, 1)} aria-label="Move down"><ArrowDown size={14} /></button></div>}
                  </div>
                );
              })}
            </div>
          </section>

          <section className="packet-platform-panel">
            <div className="packet-platform-heading"><FileStack size={17} /><div><strong>Packet sections</strong><span>Cover + Executive Scorecard always stay</span></div></div>
            <div className="packet-section-checks">{PERFORMANCE_SECTIONS.map(([key, label]) => <label key={key}><input type="checkbox" checked={selectedSections.includes(key)} onChange={() => toggleSection(key)} /><span>{label}</span></label>)}</div>
          </section>

          <section className="packet-platform-panel">
            <div className="packet-platform-heading"><Palette size={17} /><div><strong>Theme & cover branding</strong><span>Presentation only · facts never change</span></div></div>
            <label className="packet-platform-field"><span>Theme</span><select value={options.theme ?? "classic-dossier"} onChange={(event) => update("theme", event.target.value)}>{THEMES.map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
            <div className="packet-platform-two"><label className="packet-platform-field"><span>Cover brand</span><input value={options.brandName ?? ""} onChange={(event) => update("brandName", event.target.value)} placeholder="Optional organization name" maxLength={120} /></label><label className="packet-platform-field"><span>Department / team</span><input value={options.departmentLabel ?? ""} onChange={(event) => update("departmentLabel", event.target.value)} placeholder="Optional" maxLength={120} /></label><label className="packet-platform-field"><span>Reviewer</span><input value={options.reviewerName ?? ""} onChange={(event) => update("reviewerName", event.target.value)} placeholder="Optional" maxLength={120} /></label><label className="packet-platform-field"><span>Review cycle</span><input value={options.reviewCycleLabel ?? ""} onChange={(event) => update("reviewCycleLabel", event.target.value)} placeholder="2026 Annual Review" maxLength={120} /></label></div>
          </section>

          <section className="packet-platform-panel">
            <div className="packet-platform-heading"><ShieldCheck size={17} /><div><strong>Manager-ready annotations</strong><span>User-authored context · never counted as evidence</span></div></div>
            <label className="packet-platform-field"><span>Packet context note</span><textarea rows={3} maxLength={1500} value={options.packetNote ?? ""} onChange={(event) => update("packetNote", event.target.value)} placeholder="Constraints, scope changes, next-step goals, or context for the review conversation." /></label>
            {signatureEntryIds.length > 0 && <div className="packet-item-notes">{signatureEntryIds.map((entryId) => { const item = highlights.find((highlight) => highlight.entry_id === entryId); return <label className="packet-platform-field" key={entryId}><span>{item?.title || "Selected accomplishment"}</span><input maxLength={800} value={options.itemNotes?.[entryId] ?? ""} onChange={(event) => setItemNote(entryId, event.target.value)} placeholder="Optional packet-only context" /></label>; })}</div>}
            <label className="packet-evidence-export-toggle"><input type="checkbox" checked={options.includeNotes !== false} onChange={(event) => update("includeNotes", event.target.checked)} /><span>Include annotations in preview/PDF<small>Turn off to keep all user-authored context out of the exported packet.</small></span></label>
          </section>
        </div>
      )}

      {isInterview && <section className="packet-story-picker" aria-label="Interview story selection"><div className="packet-story-picker-heading"><div><span>Choose your interview stories</span><strong>{selectedEntryIds.length} of 8 selected</strong></div><p>Pick the accomplishments you actually want to discuss. BragStack will not invent missing story details.</p></div>{highlights.length ? <div className="packet-story-options">{highlights.map((highlight) => { const checked = selectedEntryIds.includes(highlight.entry_id); return <label key={highlight.entry_id} className={checked ? "selected" : ""}><input type="checkbox" checked={checked} disabled={!checked && selectedEntryIds.length >= 8} onChange={() => toggleList("selectedEntryIds", highlight.entry_id)} /><span><strong>{highlight.title}</strong><small>{highlight.category || "Accomplishment"}{highlight.result ? ` · ${highlight.result}` : ""}</small></span></label>; })}</div> : <p className="packet-story-empty">Add accomplishments to choose interview stories.</p>}<label className="packet-evidence-export-toggle"><input type="checkbox" checked={options.includeEvidenceReferences === true} onChange={(event) => update("includeEvidenceReferences", event.target.checked)} /><span>Include evidence references in this packet<small>Off by default so private proof stays private unless you explicitly export it.</small></span></label></section>}

      <div className="packet-builder-pro-footer">
        <label className="packet-confidential-toggle"><input type="checkbox" checked={options.confidential !== false} onChange={(event) => update("confidential", event.target.checked)} /><span><ShieldCheck size={16} />Mark packet confidential</span></label>
        <div className="packet-builder-pro-action"><div><BriefcaseBusiness size={16} />Uses the currently selected report period</div><button type="button" onClick={onBuild} disabled={isLoading || (isInterview && selectedEntryIds.length === 0)}>{isLoading ? "Building packet…" : `Build ${isCertification ? "certification" : isPromotion ? "promotion" : isInterview ? "interview" : "performance"} packet`}</button></div>
      </div>
      {error && <p className="packet-builder-pro-error">{String(error)}</p>}
    </section>
  );
}

export default PacketBuilderPanel;
