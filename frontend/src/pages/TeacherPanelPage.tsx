import { Edit3, Plus, Trash2, X } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import { AnimatedPage } from "../components/AnimatedPage";
import type { Category, TestDetail, TestItem } from "../types";
import { toast } from "../utils/toast";

interface FormQuestion {
  body: string;
  kind: "single_choice" | "multiple_choice" | "true_false" | "code" | "timed";
  code_snippet: string;
  points: number;
  answers: Array<{ body: string; is_correct: boolean }>;
}

const blankQuestion = (): FormQuestion => ({
  body: "",
  kind: "single_choice",
  code_snippet: "",
  points: 10,
  answers: [
    { body: "", is_correct: true },
    { body: "", is_correct: false },
    { body: "", is_correct: false },
    { body: "", is_correct: false }
  ]
});

export function TeacherPanelPage() {
  const [tests, setTests] = useState<TestItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState(1);
  const [difficulty, setDifficulty] = useState("medium");
  const [mode, setMode] = useState("standard");
  const [questions, setQuestions] = useState<FormQuestion[]>([blankQuestion()]);

  function load() {
    api.get("/tests", { params: { limit: 100 } }).then((response) => setTests(response.data)).catch(() => setTests([]));
    api.get("/tests/categories").then((response) => {
      setCategories(response.data);
      if (response.data[0]) setCategoryId(response.data[0].id);
    }).catch(() => setCategories([]));
  }

  useEffect(load, []);

  function resetForm() {
    setEditingId(null);
    setTitle("");
    setDescription("");
    setDifficulty("medium");
    setMode("standard");
    setQuestions([blankQuestion()]);
    setOpen(true);
  }

  async function edit(testId: number) {
    const response = await api.get<TestDetail>(`/tests/${testId}`);
    const test = response.data;
    setEditingId(test.id);
    setTitle(test.title);
    setDescription(test.description);
    setCategoryId(test.category.id);
    setDifficulty(test.difficulty);
    setMode(test.mode);
    setQuestions(test.questions.map((question) => ({
      body: question.body,
      kind: question.kind,
      code_snippet: question.code_snippet ?? "",
      points: question.points,
      answers: question.answers.map((answer) => ({ body: answer.body, is_correct: Boolean(answer.is_correct) }))
    })));
    setOpen(true);
  }

  async function remove(testId: number) {
    try {
      await api.delete(`/tests/${testId}`);
      toast("Тест удален");
      load();
    } catch {
      toast("Удалять можно только свои тесты");
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const payload = {
      title,
      description,
      category_id: categoryId,
      difficulty,
      mode,
      questions: questions.map((question) => ({
        ...question,
        code_snippet: question.code_snippet.trim() || null,
        answers: question.answers.filter((answer) => answer.body.trim())
      }))
    };
    try {
      if (editingId) {
        await api.put(`/tests/${editingId}`, payload);
        toast("Тест обновлен");
      } else {
        await api.post("/tests", payload);
        toast("Тест создан");
      }
      setOpen(false);
      load();
    } catch {
      toast("Проверь права и заполнение вопросов");
    }
  }

  return (
    <AnimatedPage>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-white">Панель преподавателя</h1>
          <p className="mt-1 text-slate-400">Создание, редактирование и удаление тестов через API.</p>
        </div>
        <button onClick={resetForm} className="flex items-center gap-2 rounded bg-cyan px-4 py-2 text-sm font-medium text-slate-950"><Plus className="h-4 w-4" /> Новый тест</button>
      </div>
      <section className="glass overflow-hidden rounded">
        <div className="grid grid-cols-[1fr_140px_120px_120px] gap-4 border-b border-slate-700 px-5 py-3 text-xs uppercase tracking-wide text-slate-500">
          <span>Тест</span><span>Категория</span><span>Попытки</span><span>Действия</span>
        </div>
        {tests.length ? tests.map((test) => (
          <div key={test.id} className="grid grid-cols-[1fr_140px_120px_120px] gap-4 border-b border-slate-800 px-5 py-4 text-sm last:border-none">
            <div><div className="font-medium text-white">{test.title}</div><div className="text-slate-500">{test.difficulty} · {test.mode}</div></div>
            <div className="text-slate-300">{test.category.name}</div>
            <div className="text-slate-300">{test.attempts_count}</div>
            <div className="flex gap-2">
              <button onClick={() => edit(test.id)} className="rounded border border-slate-700 p-2 text-slate-300" title="Редактировать"><Edit3 className="h-4 w-4" /></button>
              <button onClick={() => remove(test.id)} className="rounded border border-slate-700 p-2 text-rose-300" title="Удалить"><Trash2 className="h-4 w-4" /></button>
            </div>
          </div>
        )) : <div className="px-5 py-10 text-center text-sm text-slate-500">Тестов пока нет.</div>}
      </section>

      {open && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 p-4">
          <form onSubmit={submit} className="glass mx-auto max-w-4xl rounded p-5">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">{editingId ? "Редактирование теста" : "Создание теста"}</h2>
              <button type="button" onClick={() => setOpen(false)} className="rounded border border-slate-700 p-2 text-slate-300"><X className="h-4 w-4" /></button>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <input value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="Название" className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none" />
              <select value={categoryId} onChange={(e) => setCategoryId(Number(e.target.value))} className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none">
                {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
              </select>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none">
                <option value="easy">легкий</option><option value="medium">средний</option><option value="hard">сложный</option>
              </select>
              <select value={mode} onChange={(e) => setMode(e.target.value)} className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none">
                <option value="standard">обычный</option><option value="timed">на время</option><option value="hardcore">хардкор</option><option value="random">случайные вопросы</option><option value="practice">практика</option>
              </select>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)} required placeholder="Описание" className="min-h-20 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none md:col-span-2" />
            </div>
            <div className="mt-5 space-y-4">
              {questions.map((question, qIndex) => (
                <div key={qIndex} className="rounded border border-slate-700 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="font-medium text-white">Вопрос {qIndex + 1}</span>
                    <button type="button" onClick={() => setQuestions((items) => items.filter((_, index) => index !== qIndex))} className="text-sm text-rose-300">Удалить</button>
                  </div>
                  <textarea value={question.body} onChange={(e) => setQuestions(updateQuestion(questions, qIndex, { body: e.target.value }))} required placeholder="Текст вопроса" className="mb-3 w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none" />
                  <div className="mb-3 grid gap-3 md:grid-cols-[180px_1fr_100px]">
                    <select value={question.kind} onChange={(e) => setQuestions(updateQuestion(questions, qIndex, { kind: e.target.value as FormQuestion["kind"] }))} className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none">
                      <option value="single_choice">один ответ</option><option value="multiple_choice">несколько ответов</option><option value="true_false">верно/неверно</option><option value="code">код</option><option value="timed">на время</option>
                    </select>
                    <input value={question.code_snippet} onChange={(e) => setQuestions(updateQuestion(questions, qIndex, { code_snippet: e.target.value }))} placeholder="Фрагмент кода, если нужен" className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none" />
                    <input value={question.points} onChange={(e) => setQuestions(updateQuestion(questions, qIndex, { points: Number(e.target.value) }))} type="number" min={1} className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none" />
                  </div>
                  <div className="grid gap-2">
                    {question.answers.map((answer, aIndex) => (
                      <label key={aIndex} className="grid grid-cols-[24px_1fr] items-center gap-2">
                        <input checked={answer.is_correct} onChange={(e) => setQuestions(updateAnswer(questions, qIndex, aIndex, e.target.checked))} type="checkbox" />
                        <input value={answer.body} onChange={(e) => setQuestions(updateAnswerText(questions, qIndex, aIndex, e.target.value))} required={aIndex < 2} placeholder={`Ответ ${aIndex + 1}`} className="rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none" />
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 flex justify-between">
              <button type="button" onClick={() => setQuestions((items) => [...items, blankQuestion()])} className="rounded border border-slate-700 px-4 py-2 text-sm text-slate-300">Добавить вопрос</button>
              <button className="rounded bg-cyan px-4 py-2 text-sm font-medium text-slate-950">Сохранить</button>
            </div>
          </form>
        </div>
      )}
    </AnimatedPage>
  );
}

function updateQuestion(items: FormQuestion[], index: number, patch: Partial<FormQuestion>) {
  return items.map((item, current) => current === index ? { ...item, ...patch } : item);
}

function updateAnswer(items: FormQuestion[], qIndex: number, aIndex: number, checked: boolean) {
  return items.map((question, current) => current === qIndex ? { ...question, answers: question.answers.map((answer, index) => index === aIndex ? { ...answer, is_correct: checked } : answer) } : question);
}

function updateAnswerText(items: FormQuestion[], qIndex: number, aIndex: number, body: string) {
  return items.map((question, current) => current === qIndex ? { ...question, answers: question.answers.map((answer, index) => index === aIndex ? { ...answer, body } : answer) } : question);
}
