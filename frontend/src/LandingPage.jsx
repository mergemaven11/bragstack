import {
  ArrowRight,
  Briefcase,
  Check,
  FileText,
  GraduationCap,
  MessageSquare,
  Sparkles,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";

import "./LandingPage.css";

const useCases = [
  {
    icon: TrendingUp,
    title: "Promotions",
    description:
      "Walk into promotion conversations with organized proof of your impact, growth, and added responsibilities.",
  },
  {
    icon: MessageSquare,
    title: "Interviews",
    description:
      "Turn real accomplishments into confident interview stories instead of trying to remember examples under pressure.",
  },
  {
    icon: FileText,
    title: "Performance reviews",
    description:
      "Build your review throughout the year instead of reconstructing twelve months of work the night before.",
  },
  {
    icon: Users,
    title: "1:1 meetings",
    description:
      "Bring wins, blockers, lessons, and progress into every conversation with your manager.",
  },
  {
    icon: Target,
    title: "Trainers and clients",
    description:
      "Document milestones, progress, completed goals, and measurable results over time.",
  },
  {
    icon: Briefcase,
    title: "Freelancers and consultants",
    description:
      "Turn completed projects into client updates, case studies, testimonials, and proof of value.",
  },
  {
    icon: GraduationCap,
    title: "Students and career changers",
    description:
      "Track projects, certifications, new skills, and portfolio evidence as your career develops.",
  },
  {
    icon: Sparkles,
    title: "Creators and founders",
    description:
      "Capture launches, experiments, customer wins, audience growth, and business milestones.",
  },
];

const workflowSteps = [
  {
    number: "01",
    title: "Capture",
    description:
      "Record the situation, action, impact, lesson, and skills while the details are still fresh.",
  },
  {
    number: "02",
    title: "Organize",
    description:
      "Keep accomplishments searchable by category, date, role, entry type, and skill.",
  },
  {
    number: "03",
    title: "Reuse",
    description:
      "Use your proof for interviews, reviews, promotions, résumés, portfolios, clients, and 1:1s.",
  },
];

const freeFeatures = [
  "Up to 30 proof entries",
  "Five public entries",
  "Basic skill tracking",
  "Weekly progress summary",
];

const proFeatures = [
  "Unlimited proof entries",
  "Unlimited public entries",
  "Advanced reports",
  "Custom public profile",
  "Export and résumé tools",
];

function LandingPage() {
  return (
    <main className="landing-page">
      <header className="landing-nav">
        <a className="landing-logo" href="/">
          BragStack
        </a>

        <nav className="landing-nav-links" aria-label="Main navigation">
          <a href="#use-cases">Use cases</a>
          <a href="#how-it-works">How it works</a>
          <a href="#pricing">Pricing</a>
        </nav>

        <div className="landing-nav-actions">
          <a className="landing-login-link" href="/login">
            Log in
          </a>

          <a className="landing-btn landing-btn-small" href="/register">
            Start free
          </a>
        </div>
      </header>

      <section className="landing-hero">
        <div className="landing-hero-copy">
          <div className="landing-eyebrow">
            <Sparkles size={15} />
            Career proof, organized
          </div>

          <h1>
            Your work deserves
            <span> receipts.</span>
          </h1>

          <p className="landing-hero-description">
            BragStack turns everyday wins, progress, and results into organized
            proof you can use for promotions, interviews, performance reviews,
            1:1s, client updates, and more.
          </p>

          <div className="landing-hero-actions">
            <a className="landing-btn" href="/register">
              Start building proof
              <ArrowRight size={18} />
            </a>

            <a
              className="landing-btn landing-btn-secondary"
              href="#how-it-works"
            >
              See how it works
            </a>
          </div>

          <p className="landing-trust-line">
            Free to start
            <span>•</span>
            No credit card required
            <span>•</span>
            Private by default
          </p>
        </div>

        <div className="landing-proof-preview">
          <div className="preview-glow" />

          <article className="proof-preview-card">
            <div className="proof-preview-header">
              <div>
                <p>Recent proof</p>
                <span>Public entry</span>
              </div>

              <div className="proof-preview-avatar">T</div>
            </div>

            <div className="proof-preview-meta">
              Docker Support · July 2026
            </div>

            <h2>Reduced customer setup time by 35%</h2>

            <p>
              Created a repeatable troubleshooting workflow that helped
              customers identify container networking problems faster.
            </p>

            <div className="proof-preview-result">
              <span>Impact</span>
              <strong>
                Faster resolutions and a reusable process for the support team.
              </strong>
            </div>

            <div className="proof-preview-tags">
              <span>Docker</span>
              <span>Networking</span>
              <span>Support</span>
            </div>
          </article>

          <div className="floating-proof-card floating-proof-top">
            <span>Weekly proof</span>
            <strong>7 wins captured</strong>
          </div>

          <div className="floating-proof-card floating-proof-bottom">
            <span>Top skill</span>
            <strong>Problem solving</strong>
          </div>
        </div>
      </section>

      <section className="landing-use-strip" aria-label="Popular use cases">
        <span>Promotions</span>
        <span>Interviews</span>
        <span>1:1s</span>
        <span>Reviews</span>
        <span>Clients</span>
        <span>Coaching</span>
        <span>Portfolios</span>
      </section>

      <section className="landing-problem-section">
        <div className="landing-section-heading">
          <p>THE PROBLEM</p>
          <h2>Great work is surprisingly easy to forget.</h2>
          <span>
            Projects move on, tickets close, meetings end, and months later
            you’re expected to explain everything you accomplished.
          </span>
        </div>

        <div className="problem-card-grid">
          <article className="problem-card">
            <span>01</span>
            <h3>“I know I did a lot…”</h3>
            <p>
              The work happened, but the details and measurable results are
              already fading.
            </p>
          </article>

          <article className="problem-card">
            <span>02</span>
            <h3>“My résumé sounds generic.”</h3>
            <p>
              Your strongest examples are scattered across tickets, messages,
              notes, and memory.
            </p>
          </article>

          <article className="problem-card">
            <span>03</span>
            <h3>“My review is next week.”</h3>
            <p>
              Now you’re rebuilding an entire year of accomplishments in one
              stressful sitting.
            </p>
          </article>
        </div>
      </section>

      <section className="landing-use-cases" id="use-cases">
        <div className="landing-section-heading">
          <p>BUILT FOR REAL LIFE</p>
          <h2>Useful whenever progress needs to be proven.</h2>
          <span>
            BragStack is not only for job searches. It helps people document
            growth, value, outcomes, and momentum.
          </span>
        </div>

        <div className="use-case-grid">
          {useCases.map(({ icon: Icon, title, description }) => (
            <article className="use-case-card" key={title}>
              <div className="use-case-icon">
                <Icon size={21} />
              </div>

              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-workflow" id="how-it-works">
        <div className="landing-section-heading">
          <p>HOW IT WORKS</p>
          <h2>From daily work to reusable proof.</h2>
          <span>
            A lightweight habit today becomes an advantage when the next
            opportunity appears.
          </span>
        </div>

        <div className="workflow-grid">
          {workflowSteps.map((step) => (
            <article className="workflow-card" key={step.number}>
              <span className="workflow-number">{step.number}</span>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-feature-section">
        <div className="landing-feature-copy">
          <p className="landing-mini-label">YOUR PROOF LIBRARY</p>

          <h2>Remember what you did — and why it mattered.</h2>

          <p>
            BragStack helps you capture more than a task title. Each entry
            records the context, your action, the impact, what you learned, and
            the skills you demonstrated.
          </p>

          <div className="landing-feature-list">
            <div>
              <Check size={17} />
              Structured accomplishment entries
            </div>

            <div>
              <Check size={17} />
              Résumé-ready impact statements
            </div>

            <div>
              <Check size={17} />
              Public or private visibility controls
            </div>

            <div>
              <Check size={17} />
              Skill and progress tracking
            </div>
          </div>
        </div>

        <div className="feature-dashboard-preview">
          <div className="feature-preview-header">
            <div>
              <span>Weekly entries</span>
              <strong>12</strong>
            </div>

            <div>
              <span>Skills tracked</span>
              <strong>18</strong>
            </div>
          </div>

          <div className="feature-preview-entry">
            <div>
              <span className="feature-preview-badge">Public</span>
              <small>Customer Support · Current Job</small>
            </div>

            <h3>Improved escalation response process</h3>

            <p>
              Reduced repeated troubleshooting and gave the team a clearer path
              for complex customer cases.
            </p>

            <div className="feature-preview-tags">
              <span>Leadership</span>
              <span>Communication</span>
              <span>Process</span>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-pricing" id="pricing">
        <div className="landing-section-heading">
          <p>SIMPLE PRICING</p>
          <h2>Start free. Upgrade when your proof grows.</h2>
          <span>
            Build the habit first, then unlock more tools when you need them.
          </span>
        </div>

        <div className="pricing-grid">
          <article className="pricing-card">
            <div className="pricing-card-header">
              <div>
                <p>Free</p>
                <h3>$0</h3>
              </div>

              <span>Build your proof</span>
            </div>

            <ul>
              {freeFeatures.map((feature) => (
                <li key={feature}>
                  <Check size={17} />
                  {feature}
                </li>
              ))}
            </ul>

            <a
              className="landing-btn landing-btn-secondary pricing-button"
              href="/register"
            >
              Start free
            </a>
          </article>

          <article className="pricing-card pricing-card-featured">
            <div className="pricing-popular-label">Founding plan</div>

            <div className="pricing-card-header">
              <div>
                <p>Pro</p>

                <h3>
                  $6
                  <span>/month</span>
                </h3>
              </div>

              <span>Use your proof everywhere</span>
            </div>

            <ul>
              {proFeatures.map((feature) => (
                <li key={feature}>
                  <Check size={17} />
                  {feature}
                </li>
              ))}
            </ul>

            <a className="landing-btn pricing-button" href="/register">
              Start with Pro
              <ArrowRight size={17} />
            </a>
          </article>
        </div>
      </section>

      <section className="landing-final-cta">
        <div>
          <p>YOUR NEXT OPPORTUNITY WILL ASK WHAT YOU’VE DONE.</p>
          <h2>Make sure you have the proof.</h2>
          <span>
            Start capturing the wins, growth, and results that deserve to be
            remembered.
          </span>
        </div>

        <a className="landing-btn landing-final-button" href="/register">
          Build my BragStack
          <ArrowRight size={18} />
        </a>
      </section>

      <footer className="landing-footer">
        <a className="landing-logo" href="/">
          BragStack
        </a>

        <p>Turn everyday progress into undeniable proof.</p>

        <div>
          <a href="/login">Log in</a>
          <a href="/register">Create account</a>
        </div>
      </footer>
    </main>
  );
}

export default LandingPage;