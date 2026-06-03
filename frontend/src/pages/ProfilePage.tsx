import { Award, Clock, Flame } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { AnimatedPage } from "../components/AnimatedPage";
import { MetricCard } from "../components/MetricCard";
import { useAuth } from "../store/auth";

interface HistoryItem {
  id: number;
  title: string;
  category: string;
  percent: number;
  score: number;
  max_score: number;
  created_at: string;
}

export function ProfilePage() {
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    api.get("/users/me/history").then((response) => setHistory(response.data)).catch(() => setHistory([]));
  }, []);

  const average = history.length ? Math.round(history.reduce((sum, item) => sum + item.percent, 0) / history.length) : 0;

  return (
    <AnimatedPage>
      <section className="glass rounded p-6">
        <div className="flex flex-col gap-5 md:flex-row md:items-center">
          <img src={user?.avatar_url ?? "https://api.dicebear.com/8.x/identicon/svg?seed=lumin"} className="h-20 w-20 rounded border border-slate-700 bg-slate-900" />
          <div className="flex-1">
            <h1 className="text-3xl font-semibold text-white">{user?.username}</h1>
            <p className="mt-1 text-slate-400">{user?.role.name === "teacher" ? "преподаватель" : "студент"} · уровень {user?.level ?? 1} · {user?.xp ?? 0} XP</p>
          </div>
        </div>
      </section>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <MetricCard icon={Award} label="Средний результат" value={`${average}%`} hint="По истории прохождений" />
        <MetricCard icon={Flame} label="Серия" value={`${user?.streak ?? 0}`} hint="Реальная серия пользователя" />
        <MetricCard icon={Clock} label="Попытки" value={String(history.length)} hint="Сохраненные прохождения" />
      </div>
      <section className="glass mt-6 rounded p-5">
        <h2 className="text-lg font-semibold text-white">История прохождений</h2>
        <div className="mt-4 space-y-3">
          {history.length ? history.map((item) => (
            <div key={item.id} className="grid gap-2 rounded border border-slate-700 bg-slate-900/35 px-4 py-3 text-sm md:grid-cols-[1fr_140px_100px]">
              <div><div className="font-medium text-white">{item.title}</div><div className="text-slate-500">{item.category}</div></div>
              <div className="text-slate-300">{item.score}/{item.max_score}</div>
              <div className="text-slate-300">{item.percent}%</div>
            </div>
          )) : <div className="rounded border border-dashed border-slate-700 px-4 py-10 text-center text-sm text-slate-500">История пустая. Пройди тест, чтобы здесь появились данные.</div>}
        </div>
      </section>
    </AnimatedPage>
  );
}
