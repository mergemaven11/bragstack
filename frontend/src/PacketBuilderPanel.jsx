import { BriefcaseBusiness, FileStack, ShieldCheck } from "lucide-react";

import "./PacketBuilderPanel.css";

const CAREER_AREAS = [
  "",
  "Healthcare",
  "Education",
  "Technology",
  "Sales",
  "Operations",
  "Skilled Trades",
  "Creative",
  "Customer Service",
  "Management",
  "Government",
  "Nonprofit",
  "Student",
  "Other",
];

const PACKET_TYPES = [
  {
    value: "performance-review",
    label: "Performance Review Packet",
  },
  {
    value: "promotion",
    label: "Promotion Packet",
  },
  {
    value: "interview",
    label: "Interview Packet",
  },
];

function PacketBuilderPanel({
  options,
  onChange,
  onBuild,
  isLoading,
  error,
  highlights = [],
}) {
  const packetType = options.packetType || "performance-review";
  const isPromotion = packetType === "promotion";
  const isInterview = packetType === "interview";
  const selectedEntryIds = options.selectedEntryIds ?? [];

  function update(name, value) {
    onChange((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function changePacketType(value) {
    onChange((current) => ({
      ...current,
      packetType: value,
      ...(value === "interview" && !(current.selectedEntryIds?.length)
        ? {
            selectedEntryIds: highlights
              .slice(0, 5)
              .map((item) => item.entry_id)
              .filter(Boolean),
          }
        : {}),
    }));
  }

  function toggleInterviewStory(entryId) {
    onChange((current) => {
      const selected = current.selectedEntryIds ?? [];
      if (selected.includes(entryId)) {
        return {
          ...current,
          selectedEntryIds: selected.filter((id) => id !== entryId),
        };
      }

      if (selected.length >= 8) return current;
      return {
        ...current,
        selectedEntryIds: [...selected, entryId],
      };
    });
  }

  const title = isPromotion
    ? "Promotion Packet"
    : isInterview
      ? "Interview Packet"
      : "Performance Review Packet";

  const description = isPromotion
    ? "Organize documented impact, increased responsibility, growth, recognition, and supporting evidence into a professional promotion case—without inventing a readiness score."
    : isInterview
      ? "Select the accomplishments you want to talk about, turn them into evidence-backed interview stories, and surface prep questions wherever your record is missing context."
      : "Create a physical-style career dossier with analytics, measurable results, skills, contribution records, Impact Receipts, and an evidence index. The language stays useful across any profession.";

  return (
    <section className="packet-builder-pro" aria-labelledby="packet-builder-title">
      <div className="packet-builder-pro-header">
        <div className="packet-builder-pro-icon">
          <FileStack size={22} />
        </div>
        <div>
          <span>BragStack Pro · Premium Artifact</span>
          <h2 id="packet-builder-title">Build an {isInterview ? "Interview Packet" : title}</h2>
          <p>{description}</p>
        </div>
      </div>

      <div className="packet-builder-fields">
        <label>
          <span>Packet type</span>
          <select
            value={packetType}
            onChange={(event) => changePacketType(event.target.value)}
          >
            {PACKET_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Career / work area</span>
          <select
            value={options.careerArea ?? ""}
            onChange={(event) => update("careerArea", event.target.value)}
          >
            {CAREER_AREAS.map((area) => (
              <option key={area || "neutral"} value={area}>
                {area || "Career-neutral"}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Current role title</span>
          <input
            type="text"
            value={options.roleTitle ?? ""}
            onChange={(event) => update("roleTitle", event.target.value)}
            placeholder="Use profile headline"
            maxLength={160}
          />
        </label>

        <label>
          <span>Organization / team</span>
          <input
            type="text"
            value={options.organization ?? ""}
            onChange={(event) => update("organization", event.target.value)}
            placeholder="Optional"
            maxLength={180}
          />
        </label>

        {isPromotion && (
          <>
            <label>
              <span>Target role</span>
              <input
                type="text"
                value={options.targetRole ?? ""}
                onChange={(event) => update("targetRole", event.target.value)}
                placeholder="Example: Senior Manager, Lead Teacher, RN II"
                maxLength={160}
              />
            </label>

            <label>
              <span>Target level / progression</span>
              <input
                type="text"
                value={options.targetLevel ?? ""}
                onChange={(event) => update("targetLevel", event.target.value)}
                placeholder="Optional level, grade, title, or progression step"
                maxLength={120}
              />
            </label>
          </>
        )}

        {isInterview && (
          <>
            <label>
              <span>Target role</span>
              <input
                type="text"
                value={options.targetRole ?? ""}
                onChange={(event) => update("targetRole", event.target.value)}
                placeholder="Example: Assistant Principal, Store Manager, Designer"
                maxLength={160}
              />
            </label>

            <label>
              <span>Target organization</span>
              <input
                type="text"
                value={options.targetOrganization ?? ""}
                onChange={(event) => update("targetOrganization", event.target.value)}
                placeholder="Optional employer or organization"
                maxLength={180}
              />
            </label>
          </>
        )}
      </div>

      {isInterview && (
        <section className="packet-story-picker" aria-label="Interview story selection">
          <div className="packet-story-picker-heading">
            <div>
              <span>Choose your interview stories</span>
              <strong>{selectedEntryIds.length} of 8 selected</strong>
            </div>
            <p>
              Pick the accomplishments you actually want to discuss. BragStack will not invent missing story details.
            </p>
          </div>

          {highlights.length ? (
            <div className="packet-story-options">
              {highlights.map((highlight) => {
                const checked = selectedEntryIds.includes(highlight.entry_id);
                const disabled = !checked && selectedEntryIds.length >= 8;
                return (
                  <label key={highlight.entry_id} className={checked ? "selected" : ""}>
                    <input
                      type="checkbox"
                      checked={checked}
                      disabled={disabled}
                      onChange={() => toggleInterviewStory(highlight.entry_id)}
                    />
                    <span>
                      <strong>{highlight.title}</strong>
                      <small>
                        {highlight.category || "Accomplishment"}
                        {highlight.result ? ` · ${highlight.result}` : ""}
                      </small>
                    </span>
                  </label>
                );
              })}
            </div>
          ) : (
            <p className="packet-story-empty">Add accomplishments to choose interview stories.</p>
          )}

          <label className="packet-evidence-export-toggle">
            <input
              type="checkbox"
              checked={options.includeEvidenceReferences === true}
              onChange={(event) => update("includeEvidenceReferences", event.target.checked)}
            />
            <span>
              Include evidence references in this packet
              <small>Off by default so private proof stays private unless you explicitly export it.</small>
            </span>
          </label>
        </section>
      )}

      <div className="packet-builder-pro-footer">
        <label className="packet-confidential-toggle">
          <input
            type="checkbox"
            checked={options.confidential !== false}
            onChange={(event) => update("confidential", event.target.checked)}
          />
          <span>
            <ShieldCheck size={16} />
            Mark packet confidential
          </span>
        </label>

        <div className="packet-builder-pro-action">
          <div>
            <BriefcaseBusiness size={16} />
            Uses the currently selected report period
          </div>
          <button
            type="button"
            onClick={onBuild}
            disabled={isLoading || (isInterview && selectedEntryIds.length === 0)}
          >
            {isLoading
              ? "Building packet…"
              : isPromotion
                ? "Build promotion packet"
                : isInterview
                  ? "Build interview packet"
                  : "Build performance packet"}
          </button>
        </div>
      </div>

      {error && <p className="packet-builder-pro-error">{String(error)}</p>}
    </section>
  );
}

export default PacketBuilderPanel;
