import { CheckCircle2, RotateCcw, XCircle } from "lucide-react";
import { Link } from "react-router-dom";
import { AnimatedPage } from "../components/AnimatedPage";
import { ProgressBar } from "../components/ProgressBar";

export function ResultsPage() {
  const result = JSON.parse(sessionStorage.getItem("lumin_last_result") ?? "{\"title\":\"Нет результата\",\"correct\":0,\"total\":0,\"percent\":0,\"review\":[]}");
  return (
    <AnimatedPage>
      <section className="glass mx-auto max-w-4xl rounded p-8">
        <h1 className="text-3xl font-semibold text-white">{result.title}</h1>
        <p className="mt-2 text-slate-400">Результат сохранен. Ниже разбор каждого вопроса.</p>
        <div className="mt-8 max-w-md">
          <div className="mb-3 flex justify-between text-sm text-slate-300"><span>{result.correct} из {result.total}</span><span>{result.percent}%</span></div>
          <ProgressBar value={result.percent} />
        </div>
        <div className="mt-8 space-y-4">
          {result.review.map((item: any, index: number) => (
            <div key={index} className="rounded border border-slate-700 bg-slate-900/35 p-4">
              <div className="flex items-start gap-3">
                {item.isCorrect ? <CheckCircle2 className="mt-1 h-5 w-5 text-emerald-400" /> : <XCircle className="mt-1 h-5 w-5 text-rose-400" />}
                <div className="flex-1">
                  <div className="font-medium text-white">{index + 1}. {item.question}</div>
                  {item.code_snippet && <pre className="code-block mt-3 overflow-x-auto rounded p-3 text-xs text-slate-200">{item.code_snippet}</pre>}
                  <div className="mt-3 grid gap-2">
                    {item.answers.map((answer: any) => {
                      const selected = item.selected.includes(answer.id);
                      const correct = item.correct.includes(answer.id);
                      return (
                        <div key={answer.id} className={`rounded border px-3 py-2 text-sm ${correct ? "border-emerald-500/50 bg-emerald-950/30 text-emerald-100" : selected ? "border-rose-500/50 bg-rose-950/30 text-rose-100" : "border-slate-700 text-slate-400"}`}>
                          {answer.body}{correct ? " — правильный" : selected ? " — выбран" : ""}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          <Link to="/categories" className="flex items-center justify-center gap-2 rounded border border-slate-700 px-4 py-3 text-sm text-slate-300"><RotateCcw className="h-4 w-4" /> Еще тесты</Link>
          <Link to="/dashboard" className="flex items-center justify-center gap-2 rounded bg-cyan px-4 py-3 text-sm font-medium text-slate-950"><CheckCircle2 className="h-4 w-4" /> В обзор</Link>
        </div>
      </section>
    </AnimatedPage>
  );
}
