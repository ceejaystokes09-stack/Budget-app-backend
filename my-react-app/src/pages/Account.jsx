import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header.jsx";
import { apiRequest } from "../api.js";

export default function Account() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let isCurrent = true;

    async function loadAccount() {
      try {
        const account = await apiRequest("/api/details/user-details");
        if (!isCurrent) return;
        if (!account.isAuthenticated) {
          navigate("/login", { replace: true });
          return;
        }
        setUser(account);
      } catch (loadError) {
        console.error("Could not load account details.", loadError);
        if (isCurrent) {
          setError(loadError.message || "Could not load account details.");
        }
      }
    }

    loadAccount();
    return () => {
      isCurrent = false;
    };
  }, [navigate]);

  return (
    <>
      <Header user_data={user} />
      <main className="workspace account-page">
        <section className="workspace-intro">
          <div>
            <p className="eyebrow">YOUR PROFILE</p>
            <h1>Account</h1>
            <p className="workspace-subtitle">
              View the account details connected to your budget.
            </p>
          </div>
        </section>

        {error && (
          <div className="error-conc" role="alert">
            <p>{error}</p>
          </div>
        )}
        {!user && !error ? (
          <p role="status">Loading your account...</p>
        ) : (
          user && (
            <section className="account-card" aria-label="Account details">
              <div className="account-detail">
                <span>Name</span>
                <strong>{user.name}</strong>
              </div>
              <div className="account-detail">
                <span>Email address</span>
                <strong>{user.email}</strong>
              </div>
              <Link className="account-back-link" to="/">
                Back to your budget
              </Link>
            </section>
          )
        )}
      </main>
    </>
  );
}