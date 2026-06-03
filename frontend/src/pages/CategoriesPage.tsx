import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { AnimatedPage } from "../components/AnimatedPage";
import { TestCard } from "../components/TestCard";
import type { Category, TestItem } from "../types";

export function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [tests, setTests] = useState<TestItem[]>([]);
  const [active, setActive] = useState<string>("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get("/tests/categories").then((response) => setCategories(response.data)).catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    api.get("/tests", { params: { category: active || undefined, search: search || undefined, limit: 60 } })
      .then((response) => setTests(response.data))
      .catch(() => setTests([]));
  }, [active, search]);

  const counts = useMemo(() => {
    const map = new Map<string, number>();
    tests.forEach((test) => map.set(test.category.name, (map.get(test.category.name) ?? 0) + 1));
    return map;
  }, [tests]);

  return (
    <AnimatedPage>
      <div className="mb-6">
        <h1 className="text-3xl font-semibold text-white">Тесты</h1>
        <p className="mt-1 text-slate-400">Выбери категорию слева или найди тест по названию.</p>
      </div>
      <div className="grid gap-5 lg:grid-cols-[260px_1fr]">
        <aside className="glass rounded p-3">
          <button onClick={() => setActive("")} className={`mb-2 w-full rounded px-3 py-2 text-left text-sm ${active === "" ? "bg-slate-700 text-white" : "text-slate-400 hover:bg-slate-800"}`}>Все категории</button>
          <div className="space-y-1">
            {categories.map((category) => (
              <button key={category.id} onClick={() => setActive(category.name)} className={`flex w-full items-center justify-between rounded px-3 py-2 text-left text-sm ${active === category.name ? "bg-slate-700 text-white" : "text-slate-400 hover:bg-slate-800"}`}>
                <span>{category.name}</span>
                <span className="text-xs text-slate-500">{active ? "" : counts.get(category.name) ?? 0}</span>
              </button>
            ))}
          </div>
        </aside>
        <section>
          <label className="glass mb-4 flex items-center gap-2 rounded px-3 py-2">
            <Search className="h-4 w-4 text-slate-500" />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Поиск тестов" className="w-full bg-transparent text-sm outline-none" />
          </label>
          {tests.length ? (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {tests.map((test) => <TestCard key={test.id} test={test} />)}
            </div>
          ) : (
            <div className="glass rounded px-4 py-12 text-center text-sm text-slate-500">По этому фильтру тестов нет.</div>
          )}
        </section>
      </div>
    </AnimatedPage>
  );
}
