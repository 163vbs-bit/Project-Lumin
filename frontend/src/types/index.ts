export type RoleName = "student" | "teacher";

export interface Role {
  id: number;
  name: RoleName;
}

export interface User {
  id: number;
  email: string;
  username: string;
  avatar_url?: string;
  xp: number;
  level: number;
  streak: number;
  role: Role;
}

export interface Category {
  id: number;
  name: string;
  description: string;
  color: string;
}

export interface Answer {
  id: number;
  body: string;
  is_correct?: boolean;
}

export interface Question {
  id: number;
  body: string;
  kind: "single_choice" | "multiple_choice" | "true_false" | "code" | "timed";
  code_snippet?: string;
  time_limit_seconds?: number;
  points: number;
  answers: Answer[];
}

export interface TestItem {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  mode: string;
  time_limit_seconds?: number;
  category: Category;
  question_count: number;
  attempts_count: number;
}

export interface TestDetail extends Omit<TestItem, "question_count" | "attempts_count"> {
  questions: Question[];
}

export interface DashboardAnalytics {
  stats: {
    tests_completed: number;
    average_percent: number;
    xp: number;
    level: number;
    streak: number;
    total_tests: number;
  };
  category_performance: Array<{ category: string; mastery: number; attempts: number }>;
  popular_tests: Array<{ id: number; title: string; category: string; attempts: number; average_percent: number }>;
}
