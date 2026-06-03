import { Activity, Brain, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { AnimatedPage } from "../components/AnimatedPage";
import { MetricCard } from "../components/MetricCard";
import { ProgressBar } from "../components/ProgressBar";
import type { DashboardAnalytics } from "../types";

export function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);

  useEffect(() => {
    api.get("/analytics/dashboard").then((response) => setAnalytics(response.data)).catch(() => setAnalytics(null));
  }, []);

  const stats = analytics?.stats;

  return (
    <AnimatedPage>
      <div className="mb-6">
        <h1 className="text-3xl font-semibold text-white">Аналитика</h1>
        <p className="mt-1 text-slate-400">Реальная аналитика по твоим попыткам и прогрессу.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard icon={Users} label="Пройдено" value={String(stats?.tests_completed ?? 0)} hint="Только завершенные попытки" />
        <MetricCard icon={Brain} label="Средний результат" value={`${stats?.average_percent ?? 0}%`} hint="По всем попыткам" />
        <MetricCard icon={Activity} label="Всего тестов" value={String(stats?.total_tests ?? 0)} hint="Опубликовано в системе" />
      </div>
      <section className="glass mt-6 rounded p-5">
        <h2 className="text-lg font-semibold text-white">Категории</h2>
        <div className="mt-5 space-y-4">
          {analytics?.category_performance.length ? analytics.category_performance.map((item) => (
            <div key={item.category}>
              <div className="mb-2 flex justify-between text-sm text-slate-300"><span>{item.category}</span><span>{item.mastery}% · попыток: {item.attempts}</span></div>
              <ProgressBar value={item.mastery} />
            </div>
          )) : <div className="rounded border border-dashed border-slate-700 px-4 py-10 text-center text-sm text-slate-500">Данных пока нет.</div>}
        </div>
      </section>
    </AnimatedPage>
  );
}
