import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppLayout } from "../layouts/AppLayout";
import { AnalyticsPage } from "../pages/AnalyticsPage";
import { CategoriesPage } from "../pages/CategoriesPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LandingPage } from "../pages/LandingPage";
import { LeaderboardPage } from "../pages/LeaderboardPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ResultsPage } from "../pages/ResultsPage";
import { TeacherPanelPage } from "../pages/TeacherPanelPage";
import { TestPage } from "../pages/TestPage";

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { path: "dashboard", element: <DashboardPage /> },
      { path: "categories", element: <CategoriesPage /> },
      { path: "tests/:id", element: <TestPage /> },
      { path: "results/:id", element: <ResultsPage /> },
      { path: "profile", element: <ProfilePage /> },
      { path: "teacher", element: <TeacherPanelPage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "leaderboard", element: <LeaderboardPage /> }
    ]
  },
  { path: "*", element: <Navigate to="/" /> }
]);
