import { useState } from "react";
import { Lock, Mail, Sparkles, UserPlus } from "lucide-react";
import "./AuthPage.css";

function AuthPage({ mode = "login", onLogin, onRegister }) {
  const isRegister = mode === "register";

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setErrorMessage("");

    try {
      if (isRegister) {
        await onRegister(formData);
      } else {
        await onLogin({
          email: formData.email,
          password: formData.password,
        });
      }
    } catch (error) {
      console.error(error);
      setErrorMessage(
        isRegister
          ? "Could not create your account. Try again."
          : "Could not log you in. Check your email and password."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-shell">
        <div className="auth-copy">
          <p className="mini-label">BragStack</p>

          <h1>
            Save your wins before
            <span> they disappear.</span>
          </h1>

          <p>
            Track technical work, turn progress into resume bullets, and build a
            private career proof system you can reuse for reviews, interviews,
            raises, and job searches.
          </p>

          <div className="auth-proof-list">
            <span>Private by default</span>
            <span>Resume-ready proof</span>
            <span>Weekly summaries</span>
          </div>
        </div>

        <form className="auth-card" onSubmit={handleSubmit}>
          <div className="auth-icon">
            {isRegister ? <UserPlus size={24} /> : <Sparkles size={24} />}
          </div>

          <p className="mini-label">
            {isRegister ? "Create account" : "Welcome back"}
          </p>

          <h2>{isRegister ? "Start your BragStack" : "Log in to BragStack"}</h2>

          <p className="auth-muted">
            {isRegister
              ? "Create your private workspace for career proof."
              : "Open your dashboard and keep building your proof."}
          </p>

          {errorMessage && <div className="auth-error">{errorMessage}</div>}

          {isRegister && (
            <label className="auth-field">
              Name
              <div>
                <UserPlus size={17} />
                <input
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Tee"
                  required
                />
              </div>
            </label>
          )}

          <label className="auth-field">
            Email
            <div>
              <Mail size={17} />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                required
              />
            </div>
          </label>

          <label className="auth-field">
            Password
            <div>
              <Lock size={17} />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                minLength={8}
                required
              />
            </div>
          </label>

          <button className="btn primary auth-submit" disabled={isSubmitting}>
            {isSubmitting
              ? "Working..."
              : isRegister
              ? "Create account"
              : "Log in"}
          </button>

          <p className="auth-switch">
            {isRegister ? "Already have an account?" : "New to BragStack?"}{" "}
            <a href={isRegister ? "/login" : "/register"}>
              {isRegister ? "Log in" : "Create one"}
            </a>
          </p>
        </form>
      </section>
    </main>
  );
}

export default AuthPage;