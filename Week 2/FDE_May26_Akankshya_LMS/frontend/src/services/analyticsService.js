import api from "../api";

const analyticsService = {
  getSummary: ()        => api.get("/analytics/summary"),
  getMostBorrowed: (n)  => api.get(`/analytics/most-borrowed?limit=${n ?? 10}`),
  getCategoryStats: ()  => api.get("/analytics/category-stats"),
  getMonthlyTrends: ()  => api.get("/analytics/monthly-trends"),
  getOverdue: ()        => api.get("/analytics/overdue"),
  getEtlStatus: ()      => api.get("/analytics/etl-status"),
};

export default analyticsService;
