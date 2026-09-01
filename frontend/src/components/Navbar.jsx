import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-md">
      <nav className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-display text-xl tracking-tight hover:text-route transition-colors">
          <span className="bg-gradient-to-br from-route to-route/80 text-white px-3 py-1.5 rounded-lg font-semibold">
            CB
          </span>
          <span>
            Course<span className="text-route">Builder</span>
          </span>
        </Link>

        <div className="flex items-center gap-2 sm:gap-4 text-sm font-medium">
          {user ? (
            <>
              <Link to="/dashboard" className="hidden sm:inline-block px-4 py-2 rounded-lg hover:bg-slate-100 hover:text-route transition-all">
                Dashboard
              </Link>
              <Link to="/courses/new" className="hidden sm:inline-block px-4 py-2 rounded-lg hover:bg-slate-100 hover:text-route transition-all">
                New Course
              </Link>
              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                className="px-4 py-2.5 rounded-lg border-2 border-slate-200 hover:border-route hover:text-route transition-all font-medium"
              >
                Log out
              </button>
              {/* Mobile menu */}
              <div className="sm:hidden flex gap-2">
                <Link to="/dashboard" className="p-2 rounded-lg hover:bg-slate-100 text-route font-bold text-lg">
                  📊
                </Link>
                <Link to="/courses/new" className="p-2 rounded-lg hover:bg-slate-100 text-route font-bold text-lg">
                  ➕
                </Link>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="hidden sm:inline-block px-4 py-2 rounded-lg hover:bg-slate-100 hover:text-route transition-all">
                Log in
              </Link>
              <Link
                to="/register"
                className="btn-primary text-sm"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
