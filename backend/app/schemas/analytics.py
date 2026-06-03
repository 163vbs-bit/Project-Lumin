from pydantic import BaseModel


class DashboardStats(BaseModel):
    tests_completed: int
    average_percent: float
    xp: int
    level: int
    streak: int
    total_tests: int


class CategoryPerformance(BaseModel):
    category: str
    mastery: float
    attempts: int


class PopularTest(BaseModel):
    id: int
    title: str
    category: str
    attempts: int
    average_percent: float


class AnalyticsOut(BaseModel):
    stats: DashboardStats
    category_performance: list[CategoryPerformance]
    popular_tests: list[PopularTest]
