import { Donut, HorizontalBars, Legend, RevenueTrend } from "@/components/Charts";
import { KpiCard } from "@/components/KpiCard";
import { PipelineStatus } from "@/components/PipelineStatus";
import dashboard from "@/data/dashboard.json";
import {
  formatCurrency,
  formatCurrencyCents,
  formatLongDate,
  formatNumber,
  formatShortDate,
} from "@/lib/format";
import { buildInsights } from "@/lib/insights";
import type { DashboardData } from "@/lib/types";

const data = dashboard as DashboardData;

export default function Home() {
  const { kpis, totals, range } = data;
  const insights = buildInsights(data);

  return (
    <main className="wrap">
      <header className="top">
        <div>
          <h1>
            Sales <span>Pulse</span>
          </h1>
          <p className="sub">
            Latest day: <strong>{formatLongDate(kpis.date)}</strong> · {range.days} days of data (
            {formatShortDate(range.from)} – {formatShortDate(range.to)})
          </p>
        </div>
        <span className="badge">✓ Data quality checks passed</span>
      </header>

      <section className="kpis">
        <KpiCard
          label="Revenue (latest day)"
          value={formatCurrency(kpis.revenue)}
          changePct={kpis.revenueChangePct}
        />
        <KpiCard
          label="Orders (latest day)"
          value={formatNumber(kpis.orders)}
          changePct={kpis.ordersChangePct}
        />
        <KpiCard
          label="Avg order value"
          value={formatCurrencyCents(kpis.avgOrderValue)}
          changePct={kpis.avgOrderValueChangePct}
        />
        <KpiCard
          label="Total revenue"
          value={formatCurrency(totals.revenue)}
          note={`${formatNumber(totals.orders)} orders · last ${range.days} days`}
        />
      </section>

      <section className="grid">
        <div className="card wide">
          <h2>Daily revenue</h2>
          <RevenueTrend data={data.daily} />
        </div>

        <div className="card">
          <h2>Top 5 products</h2>
          <HorizontalBars data={data.topProducts} />
        </div>

        <div className="card">
          <h2>Revenue by region</h2>
          <div className="split">
            <Donut data={data.regions} />
            <Legend data={data.regions} />
          </div>
        </div>

        <div className="card">
          <h2>Revenue by category</h2>
          <HorizontalBars data={data.categories} />
        </div>

        <div className="card">
          <h2>Key insights</h2>
          <ul className="insights">
            {insights.map((text) => (
              <li key={text}>{text}</li>
            ))}
          </ul>
        </div>

        <div className="wide">
          <PipelineStatus data={data} />
        </div>
      </section>
    </main>
  );
}
