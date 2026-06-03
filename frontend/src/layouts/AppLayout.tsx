import { BarChart3, BookOpen, Brain, LogOut, Trophy, UserRound } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

const links = [
  { to: "/dashboard", label: "Обзор", icon: BarChart3 },
  { to: "/categories", label: "Тесты", icon: BookOpen },
  { to: "/leaderboard", label: "Рейтинг", icon: Trophy },
  { to: "/profile", label: "Профиль", icon: UserRound },
  { to: "/analytics", label: "Аналитика", icon: Brain }
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-radial-grid">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-700/70 bg-ink p-5 lg:block">
        <NavLink to="/dashboard" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded bg-slate-700 text-cyan">Lu</div>
          <div>
            <div className="text-xl font-semibold text-white">Lumin</div>
            <div className="text-xs text-slate-500">знания в коде</div>
          </div>
        </NavLink>
        <nav className="mt-10 space-y-2">
          {links.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `flex items-center gap-3 rounded px-3 py-2.5 text-sm transition ${isActive ? "bg-slate-700 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"}`}>
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
          {user?.role.name === "teacher" && (
            <NavLink to="/teacher" className={({ isActive }) => `flex items-center gap-3 rounded px-3 py-2.5 text-sm transition ${isActive ? "bg-slate-700 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"}`}>
              <Brain className="h-4 w-4" />
              Панель преподавателя
            </NavLink>
          )}
        </nav>
        <button
          onClick={() => {
            logout();
            navigate("/");
          }}
          className="absolute bottom-5 left-5 right-5 flex items-center justify-center gap-2 rounded border border-slate-700 px-4 py-2.5 text-sm text-slate-300 transition hover:bg-slate-800"
        >
          <LogOut className="h-4 w-4" />
          Выйти
        </button>
      </aside>
      <main className="px-4 py-5 lg:ml-64 lg:px-8">
        <header className="mb-6 flex items-center justify-between lg:hidden">
          <NavLink to="/dashboard" className="text-2xl font-semibold text-white">Lumin</NavLink>
          <div className="text-sm text-slate-400">{user?.username}</div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
