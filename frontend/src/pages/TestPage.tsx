import { CheckCircle2, Clock, Code2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import { AnimatedPage } from "../components/AnimatedPage";
import { ProgressBar } from "../components/ProgressBar";
import type { Question, TestDetail } from "../types";
import { toast } from "../utils/toast";

export function TestPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState<TestDetail | null>(null);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number[]>>({});

  useEffect(() => {
    api.get(`/tests/${id}`).then((response) => setTest(response.data)).catch(() => setTest(null));
  }, [id]);

  if (!test) {
    return <AnimatedPage><div className="glass rounded p-8 text-slate-400">Загрузка теста...</div></AnimatedPage>;
  }

  const activeTest = test;
  const question = activeTest.questions[current];

  function toggleAnswer(question: Question, answerId: number) {
    setAnswers((state) => {
      const selected = state[question.id] ?? [];
      if (question.kind === "multiple_choice") {
        return { ...state, [question.id]: selected.includes(answerId) ? selected.filter((id) => id !== answerId) : [...selected, answerId] };
      }
      return { ...state, [question.id]: [answerId] };
    });
  }

  async function finish() {
    const review = activeTest.questions.map((item) => {
      const selected = answers[item.id] ?? [];
      const correct = item.answers.filter((answer) => answer.is_correct).map((answer) => answer.id);
      const isCorrect = selected.length === correct.length && selected.every((answerId) => correct.includes(answerId));
      return {
        question: item.body,
        code_snippet: item.code_snippet,
        selected,
        correct,
        answers: item.answers,
        isCorrect
      };
    });
    const correctCount = review.filter((item) => item.isCorrect).length;
    const percent = Math.round((correctCount / activeTest.questions.length) * 100);
    try {
      await api.post(`/tests/${activeTest.id}/attempts`, { answers, duration_seconds: 0, mode: activeTest.mode });
    } catch {
      toast("Не удалось сохранить попытку на сервере");
    }
    sessionStorage.setItem("lumin_last_result", JSON.stringify({ title: activeTest.title, correct: correctCount, total: activeTest.questions.length, percent, review }));
    navigate(`/results/${activeTest.id}`);
  }

  return (
    <AnimatedPage>
      <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <div className="text-sm uppercase tracking-wide text-cyan">{activeTest.category.name}</div>
          <h1 className="mt-2 text-3xl font-semibold text-white">{activeTest.title}</h1>
        </div>
        <div className="flex gap-2 text-sm text-slate-300">
          <span className="glass flex items-center gap-2 rounded px-3 py-2"><Clock className="h-4 w-4 text-cyan" /> {modeLabel(activeTest.mode)}</span>
          <span className="glass flex items-center gap-2 rounded px-3 py-2"><CheckCircle2 className="h-4 w-4 text-slate-400" /> {current + 1}/{activeTest.questions.length}</span>
        </div>
      </div>
      <ProgressBar value={((current + 1) / activeTest.questions.length) * 100} />
      <section className="glass mt-6 rounded p-6">
        <div className="mb-4 text-sm text-slate-500">Вопрос {current + 1}</div>
        <h2 className="text-xl font-semibold leading-8 text-white">{question.body}</h2>
        {question.code_snippet && (
          <pre className="code-block mt-5 overflow-x-auto rounded p-4 text-sm text-slate-200"><Code2 className="mb-3 h-4 w-4 text-cyan" />{question.code_snippet}</pre>
        )}
        <div className="mt-6 grid gap-3">
          {question.answers.map((answer) => {
            const selected = (answers[question.id] ?? []).includes(answer.id);
            return (
              <button key={answer.id} onClick={() => toggleAnswer(question, answer.id)} className={`rounded border px-4 py-3 text-left text-sm transition ${selected ? "border-cyan bg-sky-950/40 text-white" : "border-slate-700 bg-slate-900/35 text-slate-300 hover:border-slate-500"}`}>
                {answer.body}
              </button>
            );
          })}
        </div>
        <div className="mt-6 flex justify-between">
          <button disabled={current === 0} onClick={() => setCurrent((value) => Math.max(0, value - 1))} className="rounded border border-slate-700 px-4 py-2 text-sm text-slate-300 disabled:opacity-40">Назад</button>
          {current === activeTest.questions.length - 1 ? (
            <button onClick={finish} className="rounded bg-cyan px-4 py-2 text-sm font-medium text-slate-950">Завершить</button>
          ) : (
            <button onClick={() => setCurrent((value) => value + 1)} className="rounded bg-cyan px-4 py-2 text-sm font-medium text-slate-950">Далее</button>
          )}
        </div>
      </section>
    </AnimatedPage>
  );
}

function modeLabel(value: string) {
  return ({ standard: "обычный", timed: "на время", hardcore: "хардкор", random: "случайный", practice: "практика" } as Record<string, string>)[value] ?? value;
}
