import { Activity, Flame, Gauge, Trophy } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { AnimatedPage } from "../components/AnimatedPage";
import { MetricCard } from "../components/MetricCard";
import { ProgressBar } from "../components/ProgressBar";
import { TestCard } from "../components/TestCard";
import { useAuth } from "../store/auth";
import type { DashboardAnalytics, TestItem } from "../types";

export function DashboardPage() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [tests, setTests] = useState<TestItem[]>([]);

  useEffect(() => {
    api.get("/analytics/dashboard").then((response) => setAnalytics(response.data)).catch(() => setAnalytics(null));
    api.get("/tests", { params: { limit: 6 } }).then((response) => setTests(response.data)).catch(() => setTests([]));
  }, []);

  const stats = analytics?.stats;

  return (
    <AnimatedPage>
      <div className="mb-6">
        <h1 className="text-3xl font-semibold text-white">Обзор</h1>
        <p className="mt-1 text-slate-400">Аккаунт: {user?.username}. Здесь отображаются только реальные результаты прохождений.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Trophy} label="XP" value={String(stats?.xp ?? user?.xp ?? 0)} hint="Начисляется после тестов" />
        <MetricCard icon={Gauge} label="Средний результат" value={`${stats?.average_percent ?? 0}%`} hint="По завершенным тестам" />
        <MetricCard icon={Flame} label="Серия" value={String(stats?.streak ?? user?.streak ?? 0)} hint="Растет при результате от 60%" />
        <MetricCard icon={Activity} label="Пройдено" value={String(stats?.tests_completed ?? 0)} hint={`Всего тестов: ${stats?.total_tests ?? tests.length}`} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <section className="glass rounded p-5">
          <h2 className="text-lg font-semibold text-white">Прогресс по категориям</h2>
          <div className="mt-5 space-y-4">
            {analytics?.category_performance.length ? analytics.category_performance.map((item) => (
              <div key={item.category}>
                <div className="mb-2 flex justify-between text-sm"><span className="text-slate-300">{item.category}</span><span className="text-slate-500">{item.mastery}%</span></div>
                <ProgressBar value={item.mastery} />
              </div>
            )) : <Empty text="Пройди первый тест, и здесь появится статистика по категориям." />}
          </div>
        </section>
        <section className="glass rounded p-5">
          <h2 className="text-lg font-semibold text-white">Популярные тесты</h2>
          <div className="mt-4 space-y-3">
            {analytics?.popular_tests.length ? analytics.popular_tests.map((test) => (
              <Link key={test.id} to={`/tests/${test.id}`} className="block rounded border border-slate-700 bg-slate-900/45 px-4 py-3 text-sm hover:border-slate-500">
                <div className="font-medium text-white">{test.title}</div>
                <div className="mt-1 text-slate-500">{test.category} · попыток: {test.attempts} · средний: {test.average_percent}%</div>
              </Link>
            )) : <Empty text="Пока нет попыток по тестам." />}
          </div>
        </section>
      </div>

      <section className="mt-6">
        <h2 className="mb-4 text-lg font-semibold text-white">Доступные тесты</h2>
        {tests.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{tests.map((test) => <TestCard key={test.id} test={test} />)}</div> : <Empty text="Тесты еще не созданы." />}
      </section>
    </AnimatedPage>
  );
}

function Empty({ text }: { text: string }) {
  return <div className="rounded border border-dashed border-slate-700 px-4 py-8 text-center text-sm text-slate-500">{text}</div>;
}
