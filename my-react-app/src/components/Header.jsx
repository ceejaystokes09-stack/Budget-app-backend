import "../index.css";
import { useNavigate } from "react-router-dom";

function Header({ isDark, onToggleTheme, user_data }) {
  const navigate = useNavigate();
  return (
    <>
      <div className="top-nav centerX space-between">
        <div>
          <img
            src="/BudgetApp.github.io/logo.svg"
            style={{ border: "none", width: "80px", height: "80px" }}
          />
        </div>
        <div className="center mrg-l-4">
          <button
            type="button"
            className="theme-toggle"
            onClick={onToggleTheme}
            aria-label={
              isDark ? "Switch to light theme" : "Switch to dark theme"
            }
            aria-pressed={isDark}
            title={isDark ? "Switch to light theme" : "Switch to dark theme"}
          >
            <i
              className={`fa-solid ${isDark ? "fa-sun" : "fa-moon"}`}
              aria-hidden="true"
            ></i>
          </button>
          <i className="fa-solid fa-bell" style={{ width: "fit-content" }}></i>
          <button
            type="button"
            className="header-user-button"
            onClick={() => navigate("/login")}
          >
            <span
              className="fa-solid fa-circle-user header-user-icon"
              aria-hidden="true"
            ></span>
            <span className="header-username">
              {user_data?.name && user_data.name !== "Guest"
                ? user_data.name
                : "Sign in"}
            </span>
          </button>
        </div>
      </div>
    </>
  );
}

export default Header;
