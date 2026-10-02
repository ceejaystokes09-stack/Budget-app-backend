import { useState } from "react";
import { Link } from "react-router-dom";
import "../index.css";
import "../auth.css";

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [message, setMessage] = useState("");

  function changeMode(nextIsLogin) {
    setIsLogin(nextIsLogin);
    setMessage("");
  }

  function handleLogin() {
    console.log("later");
  }

  function handleCreate(event) {
    event.preventDefault();
    fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        name: document.getElementById("auth-name"),
        email: document.getElementById("auth-email"),
        password: document.getElementById("auth-password"),
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
      })
      .catch((err) => console.error("Error during authentication flow:", err));
    setMessage(
      "Authentication is not connected yet. Your details have not been sent.",
    );
  }

  return (
    <main className="auth-page">
      <aside className="auth-aside">
        <Link className="auth-brand" to="/" aria-label="Finance Solutions home">
          <span className="auth-brand-mark" aria-hidden="true">
            F
          </span>
          <span>Finance Solutions</span>
        </Link>
        <div className="auth-aside-copy">
          <p className="auth-kicker">A CLEARER WAY TO PLAN</p>
          <h1>Give every goal a place.</h1>
          <p>Keep your plans, priorities, and spending moving together.</p>
        </div>
        <p className="auth-aside-note">Make a little room for what matters.</p>
      </aside>

      <section className="auth-panel" aria-labelledby="auth-title">
        <div className="auth-form-wrap">
          <p className="auth-kicker auth-panel-kicker">
            YOUR FINANCES, IN FOCUS
          </p>
          <div
            className="auth-mode-switch"
            role="group"
            aria-label="Choose sign-in or sign-up"
          >
            <button
              type="button"
              className={isLogin ? "is-selected" : ""}
              aria-pressed={isLogin}
              onClick={() => changeMode(true)}
            >
              Sign in
            </button>
            <button
              type="button"
              className={!isLogin ? "is-selected" : ""}
              aria-pressed={!isLogin}
              onClick={() => changeMode(false)}
            >
              Create account
            </button>
          </div>

          <h2 id="auth-title">
            {isLogin ? "Welcome back" : "Start with a plan"}
          </h2>
          <p className="auth-description">
            {isLogin
              ? "Sign in to pick up where you left off."
              : "Create an account to organize your next goal."}
          </p>

          <form
            className="auth-form"
            onSubmit={isLogin ? handleLogin : handleCreate}
          >
            {!isLogin && (
              <label className="auth-field" htmlFor="auth-name">
                <span>Your name</span>
                <input
                  id="auth-name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  placeholder="Jamie Lee"
                  required
                />
              </label>
            )}
            <label className="auth-field" htmlFor="auth-email">
              <span>Email address</span>
              <input
                id="auth-email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                required
              />
            </label>
            <label className="auth-field" htmlFor="auth-password">
              <span>Password</span>
              <input
                id="auth-password"
                name="password"
                type="password"
                autoComplete={isLogin ? "current-password" : "new-password"}
                placeholder="At least 8 characters"
                minLength={8}
                required
              />
            </label>
            <button className="auth-submit" type="submit">
              {isLogin ? "Sign in" : "Create account"}
              <span aria-hidden="true">→</span>
            </button>
            {message && (
              <p className="auth-message" role="status">
                {message}
              </p>
            )}
          </form>

          <Link className="auth-back-link" to="/">
            ← Back to your budget
          </Link>
        </div>
      </section>
    </main>
  );
}
