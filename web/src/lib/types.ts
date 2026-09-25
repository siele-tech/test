/** Data contract produced by the Python pipeline (`sales-pipeline export`). */
export interface Breakdown {
  name: string;
  revenue: number;
  units: number;
}

export interface DailyPoint {
  date: string;
  revenue: number;
  orders: number;
}

export interface DashboardData {
  schemaVersion: number;
  generatedAt: string;
  build: { commit: string; runNumber: string | null; runUrl: string | null };
  quality: { status: "passed"; files: number; rows: number };
  range: { from: string; to: string; days: number };
  kpis: {
    date: string;
    revenue: number;
    orders: number;
    avgOrderValue: number;
    revenueChangePct: number | null;
    ordersChangePct: number | null;
    avgOrderValueChangePct: number | null;
  };
  totals: { revenue: number; orders: number; units: number };
  daily: DailyPoint[];
  topProducts: Breakdown[];
  regions: Breakdown[];
  categories: Breakdown[];
}
