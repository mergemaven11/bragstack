import {
  BadgeCheck,
  BookOpenCheck,
  CheckCircle2,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  Target,
} from "lucide-react";

import "./PerformancePacketPages.css";
import "./InterviewPacketPages.css";

function formatShortDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(`${value}T12:00:00`));
}

function chunk(items, size) {
  const pages = [];
  for (let index = 0; index < items.length; index += size) {
    pages.push(items.slice(index, index + size));
  }
  return pages.length ? pages : [[]];
}

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

function StoryCard({ story, number }) {
  return (
    <article className="interview-story-card">
      <div className="interview-story-topline">
        <span>Story {String(number).padStart(2, "0")}</span>
        <span>{story.category || "Accomplishment"}</span>
        {story.verified && (
          <span className="packet-verified-chip"><BadgeCheck size={12} /> Confirmed</span>
        )}
      </div>
      <h3>{story.title}</h3>
      {story.entry_date && <p className="interview-story-date">{formatShortDate(story.entry_date)}</p>}

      <div className="interview-story-grid">
        <div>
          <span>Contribution</span>
          <p>{story.contribution || "Not documented yet — use the prep prompt below."}</p>
        </div>
        <div>
          <span>Result</span>
          <p>{story.result || "Not documented yet — use the prep prompt below."}</p>
        </div>
      </div>

      <div className="packet-record-tags">
        {story.skills?.slice(0, 6).map((skill) => <span key={skill}>{skill}</span>)}
      </div>

      <div className="interview-proofline">
        <ShieldCheck size={14} />
        <strong>{story.proof_status}</strong>
        <span>{story.evidence_count ?? 0} evidence item{story.evidence_count === 1 ? "" : "s"}</span>
      </div>

      {story.prep_prompts?.length > 0 && (
        <div className="interview-prep-box">
          <span><MessageSquareText size={14} /> Prep questions</span>
          <ul>
            {story.prep_prompts.map((prompt) => <li key={prompt}>{prompt}</li>)}
          </ul>
        </div>
      )}
    </article>
  );
}

function InterviewPacketPages({ packet }) {
  const stories = packet?.interview_stories ?? [];
  const storyPages = chunk(stories, 2);
  const scorecard = packet?.scorecard ?? {};
  const skills = packet?.skill_details ?? [];
  const target = packet?.target ?? {};
  const storyStartPage = 3;
  const skillsPage = storyStartPage + storyPages.length;
  const prepPage = skillsPage + 1;

  const prompts = [];
  stories.forEach((story) => {
    story.prep_prompts?.forEach((prompt) => {
      if (!prompts.includes(prompt)) prompts.push(prompt);
    });
  });

  return (
    <>
      {storyPages.map((items, pageIndex) => (
        <section key={`interview-story-page-${pageIndex}`} className="packet-sheet packet-document-page">
          <PacketHeader
            index={2}
            eyebrow="Selected Interview Stories"
            title={pageIndex === 0 ? "Examples to bring into the room" : "Selected stories · continued"}
          />
          <p className="packet-page-lead">
            These examples come directly from selected BragStack accomplishments. Missing details remain visibly missing so you can prepare them in your own words.
          </p>
          {items.length ? (
            <div className="interview-story-stack">
              {items.map((story, index) => (
                <StoryCard
                  key={story.entry_id}
                  story={story}
                  number={pageIndex * 2 + index + 1}
                />
              ))}
            </div>
          ) : (
            <EmptyState>Select at least one accomplishment to build interview stories.</EmptyState>
          )}
          <PacketFooter page={storyStartPage + pageIndex} />
        </section>
      ))}

      <section className="packet-sheet packet-document-page">
        <PacketHeader index={3} eyebrow="Skills & Outcomes" title="What your selected work demonstrates" />

        <div className="packet-kpi-ribbon">
          <div><strong>{scorecard.accomplishments ?? 0}</strong><span>Selected stories</span></div>
          <div><strong>{scorecard.quantified_result_coverage_percent ?? 0}%</strong><span>Measurable result coverage</span></div>
          <div><strong>{scorecard.verification_coverage_percent ?? 0}%</strong><span>Confirmed story coverage</span></div>
        </div>

        <div className="interview-target-card">
          <Target size={22} />
          <div>
            <span>Interview target</span>
            <strong>{target.role || "General interview preparation"}</strong>
            {target.organization && <p>{target.organization}</p>}
          </div>
        </div>

        {skills.length ? (
          <div className="packet-skill-evidence-list">
            {skills.slice(0, 12).map((item, index) => (
              <article key={item.skill}>
                <div className="packet-skill-rank">{index + 1}</div>
                <div className="packet-skill-main">
                  <div><strong>{item.skill}</strong><span>{item.count} selected stor{item.count === 1 ? "y" : "ies"}</span></div>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState>Add skills to the selected accomplishments to make capability themes visible.</EmptyState>
        )}

        <PacketFooter page={skillsPage} />
      </section>

      <section className="packet-sheet packet-document-page packet-summary-page">
        <PacketHeader index={4} eyebrow="Interview Prep" title="Questions worth answering before the call" />

        <div className="interview-prep-hero">
          <Sparkles size={22} />
          <p>
            BragStack does not fill gaps with invented STAR details. These prompts point to what is missing from the record so you can prepare truthful context.
          </p>
        </div>

        {prompts.length ? (
          <ol className="interview-question-list">
            {prompts.slice(0, 12).map((prompt) => (
              <li key={prompt}>{prompt}</li>
            ))}
          </ol>
        ) : (
          <EmptyState>Your selected stories already contain contribution, results, and skills. Practice saying each one concisely.</EmptyState>
        )}

        <section className="packet-summary-narrative interview-summary-narrative">
          <CheckCircle2 size={26} />
          <div>
            <p className="packet-section-kicker">Evidence-backed interview summary</p>
            <p>{packet?.interview_summary}</p>
          </div>
        </section>

        <PacketFooter page={prepPage} />
      </section>
    </>
  );
}

export default InterviewPacketPages;
