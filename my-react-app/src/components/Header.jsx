import '../index.css'

function Header({ isDark, onToggleTheme }) {
  return (
    <>
        <div className="top-nav centerX space-between">
            <div>
                <img src="/BudgetApp.github.io/logo.svg" style={{border:"none", width:"80px", height:"80px",}} />
            </div>
            <div className='center mrg-l-4'>
              <button
                type="button"
                className="theme-toggle"
                onClick={onToggleTheme}
                aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
                aria-pressed={isDark}
                title={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
              >
                <i className={`fa-solid ${isDark ? 'fa-sun' : 'fa-moon'}`} aria-hidden="true"></i>
              </button>
                <i className="fa-solid fa-bell" style={{width: "fit-content"}} ></i>
                <i><span className="fa-solid fa-circle-user"></span><span className='cut'>Sign in</span></i>
            </div>

        </div>
    </>
  )
}

export default Header
