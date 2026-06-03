import { AxiosError } from "axios";
import { motion } from "framer-motion";
import { ArrowRight, Brain, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";
import type { RoleName } from "../types";
import { toast } from "../utils/toast";

export function LandingPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [role, setRole] = useState<RoleName>("student");
  const { login, register, loading } = useAuth();
  const navigate = useNavigate();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      if (mode === "login") {
        await login(String(form.get("username")), String(form.get("password")));
      } else {
        await register({
          email: String(form.get("email")),
          username: String(form.get("username")),
          password: String(form.get("password")),
          role
        });
      }
      toast("Вход выполнен");
      navigate("/dashboard");
    } catch (error) {
      toast(errorMessage(error));
    }
  }

  return (
    <main className="min-h-screen overflow-hidden bg-radial-grid px-4 py-6">
      <div className="mx-auto grid min-h-[calc(100vh-48px)] max-w-7xl items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <motion.section initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="mb-7 inline-flex items-center rounded border border-slate-700 bg-slate-800 px-3 py-1 text-sm text-slate-300">
            Платформа тестирования по программированию
          </div>
          <h1 className="max-w-3xl text-6xl font-semibold leading-[0.95] text-white md:text-8xl">Lumin</h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
            Студенты проходят тесты и видят реальные результаты. Преподаватели создают задания, редактируют тесты и смотрят аналитику.
          </p>
          <div className="mt-10 grid max-w-2xl gap-4 sm:grid-cols-3">
            {[
              ["50+", "готовых тестов"],
              ["10", "категорий"],
              ["5", "режимов"]
            ].map(([value, label]) => (
              <div key={label} className="glass rounded p-4">
                <div className="text-2xl font-semibold text-white">{value}</div>
                <div className="mt-1 text-sm text-slate-400">{label}</div>
              </div>
            ))}
          </div>
        </motion.section>

        <motion.section initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.45, delay: 0.12 }} className="glass rounded p-6">
          <div className="flex rounded bg-slate-950/60 p-1">
            {(["login", "register"] as const).map((item) => (
              <button key={item} type="button" onClick={() => setMode(item)} className={`flex-1 rounded px-4 py-2 text-sm transition ${mode === item ? "bg-cyan text-slate-950" : "text-slate-400 hover:text-white"}`}>
                {item === "login" ? "Вход" : "Регистрация"}
              </button>
            ))}
          </div>
          <form onSubmit={submit} className="mt-6 space-y-4">
            {mode === "register" && <input name="email" required type="email" placeholder="Почта" className="w-full rounded border border-slate-700 bg-slate-950/55 px-4 py-3 text-sm outline-none focus:border-cyan" />}
            <input name="username" required placeholder="Логин или почта" defaultValue={mode === "login" ? "demo_student" : ""} className="w-full rounded border border-slate-700 bg-slate-950/55 px-4 py-3 text-sm outline-none focus:border-cyan" />
            <input name="password" required type="password" minLength={8} defaultValue={mode === "login" ? "password123" : ""} placeholder="Пароль" className="w-full rounded border border-slate-700 bg-slate-950/55 px-4 py-3 text-sm outline-none focus:border-cyan" />
            {mode === "register" && (
              <div className="grid grid-cols-2 gap-2">
                {(["student", "teacher"] as RoleName[]).map((item) => (
                  <button key={item} type="button" onClick={() => setRole(item)} className={`rounded border px-4 py-3 text-sm transition ${role === item ? "border-cyan bg-cyan/10 text-cyan" : "border-slate-700 text-slate-400 hover:text-white"}`}>
                    {item === "student" ? "Студент" : "Преподаватель"}
                  </button>
                ))}
              </div>
            )}
            <button disabled={loading} className="flex w-full items-center justify-center gap-2 rounded bg-cyan px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan/90 disabled:opacity-60">
              {loading ? "Подождите..." : "Продолжить"} <ArrowRight className="h-4 w-4" />
            </button>
          </form>
          <div className="mt-6 grid gap-3 text-sm text-slate-400">
            <div className="flex items-center gap-3"><ShieldCheck className="h-4 w-4 text-cyan" /> Демо-студент: demo_student / password123</div>
            <div className="flex items-center gap-3"><Brain className="h-4 w-4 text-violet" /> Демо-преподаватель: demo_teacher / password123</div>
          </div>
        </motion.section>
      </div>
    </main>
  );
}

function errorMessage(error: unknown) {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
  }
  return "Не удалось выполнить действие. Проверьте логин, пароль или используйте другую почту.";
}
