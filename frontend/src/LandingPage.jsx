import {
  ArrowRight,
  BarChart3,
  Briefcase,
  Check,
  FileText,
  GraduationCap,
  LockKeyhole,
  MessageSquare,
  ReceiptText,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

import "./LandingPage.css";
import "./LandingPageMonetization.css";

const useCases = [
  { icon: TrendingUp, title: "Promotions", description: "Walk into promotion conversations with organized proof of impact, growth, and added responsibility." },
  { icon: MessageSquare, title: "Interviews", description: "Turn real accomplishments into confident stories instead of trying to remember examples under pressure." },
  { icon: FileText, title: "Performance reviews", description: "Build your review throughout the year instead of reconstructing twelve months of work the night before." },
  { icon: Users, title: "1:1 meetings", description: "Bring wins, blockers, lessons, and progress into every conversation with your manager." },
  { icon: Target, title: "Clients and coaching", description: "Document milestones, completed goals, measurable results, and evidence over time." },
  { icon: Briefcase, title: "Freelancers", description: "Turn completed projects into client updates, case studies, testimonials, and proof of value." },
  { icon: GraduationCap, title: "Career changers", description: "Track projects, certifications, new skills, and portfolio evidence as your career develops." },
  { icon: Sparkles, title: "Creators and founders", description: "Capture launches, experiments, customer wins, audience growth, and business milestones." },
];

const workflowSteps = [
  { number: "01", title: "Capture the win", description: "Save the situation, your action, the result, lessons, and skills while the details are still fresh." },
  { number: "02", title: "Turn it into proof", description: "Create Impact Receipts with contribution, result, evidence, skills, credit, and optional public visibility." },
  { number: "03", title: "See your career patterns", description: "Watch skills, categories, evidence coverage, and accomplishment activity build into a career analytics story." },
  { number: "04", title: "Package the evidence", description: "Use your history for performance reviews, promotion packets, résumé bullets, interview stories, and public proof." },
  { number: "05", title: "Walk in prepared", description: "Stop rebuilding your career from memory. Bring organized evidence into the conversations that affect your next move." },
];

const plans = [
  {
    name: "Free",
    price: "$0",
    tagline: "Prove the habit works",
    features: ["5 proof entries", "1 Impact Receipt", "Basic reports", "Basic public proof profile", "Skill tracking"],
    cta: "Start free",
    href: "/register",
  },
  {
    name: "Pro",
    price: "$9",
    suffix: "/month",
    tagline: "Turn your work history into leverage",
    featured: true,
    badge: "Best for your career",
    features: ["Unlimited proof + Impact Receipts", "Advanced career analytics", "Performance Review Builder", "Promotion Packet", "PDF and career exports", "Integrations and advanced public profile"],
    cta: "Unlock BragStack Pro",
    href: "/register",
  },
  {
    name: "Team",
    price: "$15",
    suffix: "/user / month",
    tagline: "Help teams document growth without surveillance",
    badge: "Coming soon",
    features: ["Everything in Pro", "Shared review templates", "Optional manager verification", "Review-cycle packets", "Organization analytics", "Centralized billing"],
    cta: "Join Team waitlist",
    href: "mailto:hello@bragstack.app?subject=BragStack%20Team%20waitlist",
  },
  {
    name: "Enterprise",
    price: "Custom",
    tagline: "Security and governance for larger organizations",
    features: ["Everything in Team", "SSO / SCIM", "Audit logs", "Retention controls", "Advanced admin policies", "Custom integrations and support"],
    cta: "Contact us",
    href: "mailto:hello@bragstack.app?subject=BragStack%20Enterprise",
  },
];

function LandingPage() {
  return (
    <main className="landing-page">
      <header className="landing-nav">
        <a className="landing-logo" href="/">BragStack</a>
        <nav className="landing-nav-links" aria-label="Main navigation">
          <a href="#use-cases">Use cases</a>
          <a href="#how-it-works">How it works</a>
          <a href="#pricing">Pricing</a>
        </nav>
        <div className="landing-nav-actions">
          <a className="landing-login-link" href="/login">Log in</a>
          <a className="landing-btn landing-btn-small" href="/register">Start free</a>
        </div>
      </header>

      <section className="landing-hero">
        <div className="landing-hero-copy">
          <div className="landing-eyebrow"><Sparkles size={15} />Career proof, organized</div>
          <h1>Your work deserves<span> receipts.</span></h1>
          <p className="landing-hero-description">
            BragStack turns everyday wins into career evidence you can actually use — for promotions, reviews, interviews, résumés, public proof, and the next opportunity you have not even planned for yet.
          </p>
          <div className="landing-hero-actions">
            <a className="landing-btn" href="/register">Start building proof <ArrowRight size={18} /></a>
            <a className="landing-btn landing-btn-secondary" href="#how-it-works">See the career system</a>
          </div>
          <p className="landing-trust-line">Free to start <span>•</span> No credit card required <span>•</span> Private by default</p>
        </div>

        <div className="landing-proof-preview">
          <div className="preview-glow" />
          <article className="proof-preview-card">
            <div className="proof-preview-header"><div><p>Impact Receipt</p><span>Evidence-linked</span></div><div className="proof-preview-avatar">T</div></div>
            <div className="proof-preview-meta">Platform Engineering · August 2026</div>
            <h2>Reduced repeat Docker escalations by 30%</h2>
            <p>Identified common networking failure patterns, documented diagnostics, and standardized the troubleshooting path.</p>
            <div className="proof-preview-result"><span>Result</span><strong>Faster resolution paths and less repeated escalation work.</strong></div>
            <div className="proof-preview-tags"><span>Docker</span><span>Reliability</span><span>Leadership</span></div>
          </article>
          <div className="floating-proof-card floating-proof-top"><span>Evidence coverage</span><strong>84%</strong></div>
          <div className="floating-proof-card floating-proof-bottom"><span>Career signal</span><strong>Platform ownership ↑</strong></div>
        </div>
      </section>

      <section className="landing-use-strip" aria-label="Popular use cases">
        <span>Promotions</span><span>Interviews</span><span>1:1s</span><span>Reviews</span><span>Clients</span><span>Portfolios</span><span>Career analytics</span>
      </section>

      <section className="landing-problem-section">
        <div className="landing-section-heading">
          <p>THE PROBLEM</p><h2>Your career is happening faster than your memory can track it.</h2>
          <span>Tickets close. Projects ship. Praise disappears into Slack. Six months later, someone asks what you accomplished — and your strongest evidence is scattered everywhere.</span>
        </div>
        <div className="problem-card-grid">
          <article className="problem-card"><span>01</span><h3>“I know I did a lot…”</h3><p>The work happened, but the details, numbers, and context are already fading.</p></article>
          <article className="problem-card"><span>02</span><h3>“My résumé sounds generic.”</h3><p>Your strongest examples are trapped across tickets, notes, messages, and memory.</p></article>
          <article className="problem-card"><span>03</span><h3>“My review is next week.”</h3><p>Now you are rebuilding an entire year of impact in one stressful sitting.</p></article>
        </div>
      </section>

      <section className="landing-use-cases" id="use-cases">
        <div className="landing-section-heading"><p>BUILT FOR REAL LIFE</p><h2>Useful whenever progress needs to be proven.</h2><span>BragStack is not a diary. It is an evidence system for the moments when your work needs to speak clearly.</span></div>
        <div className="use-case-grid">{useCases.map(({ icon: Icon, title, description }) => <article className="use-case-card" key={title}><div className="use-case-icon"><Icon size={21} /></div><h3>{title}</h3><p>{description}</p></article>)}</div>
      </section>

      <section className="landing-workflow premium-workflow" id="how-it-works">
        <div className="landing-section-heading"><p>HOW IT WORKS</p><h2>Capture once. Turn it into career leverage again and again.</h2><span>BragStack connects the daily work you are already doing to the career artifacts you usually scramble to create later.</span></div>

        <div className="career-flow" aria-label="BragStack career proof workflow">
          <span>Daily work</span><ArrowRight size={18} /><span>Proof entries</span><ArrowRight size={18} /><span>Impact Receipts</span><ArrowRight size={18} /><span>Career analytics</span><ArrowRight size={18} /><span>Reviews · promotions · interviews</span>
        </div>

        <div className="premium-workflow-grid">{workflowSteps.map((step) => <article className="workflow-card premium-workflow-card" key={step.number}><span className="workflow-number">{step.number}</span><h3>{step.title}</h3><p>{step.description}</p></article>)}</div>

        <div className="career-intelligence-demo">
          <div className="career-intelligence-copy">
            <p className="landing-mini-label">CAREER INTELLIGENCE</p>
            <h2>Your accomplishments become a story you can see.</h2>
            <p>Instead of a flat list of tasks, BragStack can surface patterns in the proof you have already captured: where your impact is concentrated, which skills keep showing up, and how much of your work has evidence behind it.</p>
            <div className="career-output-list">
              <span><BarChart3 size={18} /> Career activity and skill trends</span>
              <span><ReceiptText size={18} /> Evidence and Impact Receipt coverage</span>
              <span><FileText size={18} /> Review and promotion-ready packaging</span>
              <span><ShieldCheck size={18} /> Private-by-default visibility controls</span>
            </div>
          </div>
          <div className="mock-analytics-panel">
            <div className="mock-analytics-header"><span>Illustrative career dashboard</span><strong>Last 6 months</strong></div>
            <div className="mock-stat-row"><div><span>Proof captured</span><strong>38</strong></div><div><span>Impact Receipts</span><strong>24</strong></div><div><span>Skills demonstrated</span><strong>17</strong></div></div>
            <div className="mock-chart">
              {[38, 55, 46, 72, 64, 92].map((height, index) => <div key={height + index}><span style={{ height: `${height}%` }} /><small>{["Mar", "Apr", "May", "Jun", "Jul", "Aug"][index]}</small></div>)}
            </div>
            <div className="mock-signal"><span>Strongest documented signal</span><strong>Platform ownership</strong><em>Based on your captured proof</em></div>
          </div>
        </div>

        <div className="pro-output-grid">
          <article><LockKeyhole size={20} /><small>PRO</small><h3>Performance Review Builder</h3><p>Turn months of entries into a structured review without starting from a blank page.</p></article>
          <article><LockKeyhole size={20} /><small>PRO</small><h3>Promotion Packet</h3><p>Organize evidence around ownership, impact, leadership, execution, and growth.</p></article>
          <article><LockKeyhole size={20} /><small>PRO</small><h3>Advanced Analytics</h3><p>See accomplishment activity, category strength, skills, and evidence coverage over time.</p></article>
          <article><LockKeyhole size={20} /><small>PRO</small><h3>Integrations</h3><p>Bring work signals from tools like GitHub into BragStack as suggestions you control.</p></article>
        </div>
      </section>

      <section className="landing-feature-section">
        <div className="landing-feature-copy"><p className="landing-mini-label">YOUR PROOF LIBRARY</p><h2>Remember what you did — and why it mattered.</h2><p>Each entry captures context, action, impact, lessons, and skills. Important accomplishments can become richer Impact Receipts with evidence, shared credit, and trust signals.</p><div className="landing-feature-list"><div><Check size={17} /> Structured accomplishment entries</div><div><Check size={17} /> Evidence-backed Impact Receipts</div><div><Check size={17} /> Public or private visibility controls</div><div><Check size={17} /> Skill and progress analytics</div></div></div>
        <div className="feature-dashboard-preview"><div className="feature-preview-header"><div><span>Entries this quarter</span><strong>12</strong></div><div><span>Evidence coverage</span><strong>83%</strong></div></div><div className="feature-preview-entry"><div><span className="feature-preview-badge">Impact Receipt</span><small>Reliability · Current Job</small></div><h3>Improved escalation response process</h3><p>Reduced repeated troubleshooting and gave the team a clearer path for complex customer cases.</p><div className="feature-preview-tags"><span>Leadership</span><span>Communication</span><span>Process</span></div></div></div>
      </section>

      <section className="landing-pricing" id="pricing">
        <div className="landing-section-heading"><p>PRICING</p><h2>Start with proof. Upgrade when you want leverage.</h2><span>Free lets you experience the workflow. Pro unlocks the tools designed to turn a growing work history into reviews, promotion evidence, analytics, exports, and integrations.</span></div>
        <div className="pricing-grid pricing-grid-four">{plans.map((plan) => <article className={`pricing-card ${plan.featured ? "pricing-card-featured pricing-card-pro" : ""}`} key={plan.name}>{plan.badge && <div className="pricing-popular-label">{plan.badge}</div>}<div className="pricing-card-header"><div><p>{plan.name}</p><h3>{plan.price}{plan.suffix && <span>{plan.suffix}</span>}</h3></div></div><p className="pricing-tagline">{plan.tagline}</p><ul>{plan.features.map((feature) => <li key={feature}><Check size={17} />{feature}</li>)}</ul><a className={`landing-btn pricing-button ${plan.featured ? "" : "landing-btn-secondary"}`} href={plan.href}>{plan.cta}{plan.featured && <ArrowRight size={17} />}</a></article>)}</div>
        <div className="pricing-conversion-note"><Zap size={20} /><div><strong>Free proves the habit. Pro turns the habit into a career system.</strong><span>Your existing proof stays yours. Upgrade when you are ready to do more with it.</span></div></div>
      </section>

      <section className="landing-final-cta"><div><p>YOUR NEXT OPPORTUNITY WILL ASK WHAT YOU HAVE DONE.</p><h2>Make sure you have the proof — not just the memory.</h2><span>Start capturing the work now. When review season, an interview, a promotion conversation, or an unexpected opportunity arrives, your evidence is already waiting.</span></div><a className="landing-btn landing-final-button" href="/register">Build my BragStack <ArrowRight size={18} /></a></section>

      <footer className="mega-footer">
        <div className="mega-footer-brand"><a className="landing-logo" href="/">BragStack</a><p>Turn everyday work into career proof you can use when it matters.</p><a className="footer-cta" href="/register">Start building proof <ArrowRight size={15} /></a></div>
        <div className="mega-footer-columns">
          <div><h3>Product</h3><a href="#how-it-works">Impact Receipts</a><a href="#how-it-works">Career Analytics</a><a href="#how-it-works">Reports</a><a href="#how-it-works">Public Proof Profiles</a><a href="#pricing">Pricing</a></div>
          <div><h3>Solutions</h3><a href="#use-cases">Performance Reviews</a><a href="#use-cases">Promotions</a><a href="#use-cases">Interviews</a><a href="#use-cases">Freelancers</a><a href="#pricing">Teams</a></div>
          <div><h3>Resources</h3><a href="#how-it-works">How it works</a><a href="#use-cases">Use cases</a><a href="/login">Sign in</a><a href="/register">Create account</a><span>Docs · coming soon</span></div>
          <div><h3>Company</h3><a href="mailto:hello@bragstack.app">Contact</a><a href="mailto:hello@bragstack.app?subject=BragStack%20Team%20waitlist">Team waitlist</a><a href="mailto:hello@bragstack.app?subject=BragStack%20Enterprise">Enterprise</a><span>Changelog · coming soon</span><span>Security · coming soon</span></div>
        </div>
        <div className="mega-footer-bottom"><span>© 2026 BragStack</span><span>Private by default · Your proof stays yours.</span><div><a href="/login">Log in</a><a href="/register">Start free</a></div></div>
      </footer>
    </main>
  );
}

export default LandingPage;
