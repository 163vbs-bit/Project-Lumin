import { Trophy } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { AnimatedPage } from "../components/AnimatedPage";
import type { User } from "../types";

export function LeaderboardPage() {
  const [leaders, setLeaders] = useState<User[]>([]);

  useEffect(() => {
    api.get("/users/leaderboard").then((response) => setLeaders(response.data)).catch(() => setLeaders([]));
  }, []);

  return (
    <AnimatedPage>
      <div className="mb-6">
        <h1 className="text-3xl font-semibold text-white">Рейтинг</h1>
        <p className="mt-1 text-slate-400">Только реальные пользователи из базы, отсортированные по XP.</p>
      </div>
      <section className="glass rounded overflow-hidden">
        <div className="grid grid-cols-[70px_1fr_120px_120px] border-b border-slate-700 px-5 py-3 text-xs uppercase tracking-wide text-slate-500">
          <span>#</span><span>Пользователь</span><span>Уровень</span><span>XP</span>
        </div>
        {leaders.length ? leaders.map((user, index) => (
          <div key={user.id} className="grid grid-cols-[70px_1fr_120px_120px] border-b border-slate-800 px-5 py-4 text-sm last:border-none">
            <div className="flex items-center gap-2 text-slate-400">{index === 0 && <Trophy className="h-4 w-4 text-cyan" />}{index + 1}</div>
            <div className="font-medium text-white">{user.username}</div>
            <div className="text-slate-300">{user.level}</div>
            <div className="text-slate-300">{user.xp}</div>
          </div>
        )) : <div className="px-5 py-10 text-center text-sm text-slate-500">Пока нет пользователей в рейтинге.</div>}
      </section>
    </AnimatedPage>
  );
}
