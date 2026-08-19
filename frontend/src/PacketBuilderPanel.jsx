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
];

function PacketBuilderPanel({
  options,
  onChange,
  onBuild,
  isLoading,
  error,
}) {
  const isPromotion = options.packetType === "promotion";

  function update(name, value) {
    onChange((current) => ({
      ...current,
      [name]: value,
    }));
  }

  return (
    <section className="packet-builder-pro" aria-labelledby="packet-builder-title">
      <div className="packet-builder-pro-header">
        <div className="packet-builder-pro-icon">
          <FileStack size={22} />
        </div>
        <div>
          <span>BragStack Pro · Premium Artifact</span>
          <h2 id="packet-builder-title">
            Build a {isPromotion ? "Promotion Packet" : "Performance Review Packet"}
          </h2>
          <p>
            {isPromotion
              ? "Organize documented impact, increased responsibility, growth, recognition, and supporting evidence into a professional promotion case—without inventing a readiness score."
              : "Create a physical-style career dossier with analytics, measurable results, skills, contribution records, Impact Receipts, and an evidence index. The language stays useful across any profession."}
          </p>
        </div>
      </div>

      <div className="packet-builder-fields">
        <label>
          <span>Packet type</span>
          <select
            value={options.packetType}
            onChange={(event) => update("packetType", event.target.value)}
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
            value={options.careerArea}
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
            value={options.roleTitle}
            onChange={(event) => update("roleTitle", event.target.value)}
            placeholder="Use profile headline"
            maxLength={160}
          />
        </label>

        <label>
          <span>Organization / team</span>
          <input
            type="text"
            value={options.organization}
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
                value={options.targetRole}
                onChange={(event) => update("targetRole", event.target.value)}
                placeholder="Example: Senior Manager, Lead Teacher, RN II"
                maxLength={160}
              />
            </label>

            <label>
              <span>Target level / progression</span>
              <input
                type="text"
                value={options.targetLevel}
                onChange={(event) => update("targetLevel", event.target.value)}
                placeholder="Optional level, grade, title, or progression step"
                maxLength={120}
              />
            </label>
          </>
        )}
      </div>

      <div className="packet-builder-pro-footer">
        <label className="packet-confidential-toggle">
          <input
            type="checkbox"
            checked={options.confidential}
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
          <button type="button" onClick={onBuild} disabled={isLoading}>
            {isLoading
              ? "Building packet…"
              : isPromotion
                ? "Build promotion packet"
                : "Build performance packet"}
          </button>
        </div>
      </div>

      {error && <p className="packet-builder-pro-error">{String(error)}</p>}
    </section>
  );
}

export default PacketBuilderPanel;
