import { Clock, Layers } from "lucide-react";
import { Link } from "react-router-dom";
import type { TestItem } from "../types";

export function TestCard({ test }: { test: TestItem }) {
  return (
    <Link to={`/tests/${test.id}`} className="glass group block rounded p-5 transition hover:border-slate-500">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-cyan">{test.category.name}</div>
          <h3 className="mt-2 text-lg font-semibold text-white">{test.title}</h3>
        </div>
      </div>
      <p className="mt-3 line-clamp-2 text-sm text-slate-400">{test.description}</p>
      <div className="mt-5 flex flex-wrap gap-2 text-xs text-slate-300">
        <span className="rounded bg-slate-800 px-2 py-1">{difficultyLabel(test.difficulty)}</span>
        <span className="rounded bg-slate-800 px-2 py-1">{modeLabel(test.mode)}</span>
        <span className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1"><Layers className="h-3 w-3" />{test.question_count} вопр.</span>
        <span className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1"><Clock className="h-3 w-3" />{test.time_limit_seconds ? `${Math.round(test.time_limit_seconds / 60)} мин` : "без таймера"}</span>
      </div>
    </Link>
  );
}

function difficultyLabel(value: string) {
  return ({ easy: "легкий", medium: "средний", hard: "сложный" } as Record<string, string>)[value] ?? value;
}

function modeLabel(value: string) {
  return ({ standard: "обычный", timed: "на время", hardcore: "хардкор", random: "случайный", practice: "практика" } as Record<string, string>)[value] ?? value;
}
