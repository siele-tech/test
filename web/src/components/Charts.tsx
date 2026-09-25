"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatCompactCurrency, formatCurrency, formatShortDate } from "@/lib/format";
import type { Breakdown, DailyPoint } from "@/lib/types";

const ACCENT = "var(--accent)";
const SERIES = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)", "var(--s5)"];
const axis = { fontSize: 12, fill: "var(--muted)" };
const tooltipStyle = {
  background: "var(--card)",
  border: "1px solid var(--line)",
  borderRadius: 10,
  color: "var(--ink)",
};

const money = (v: unknown) => formatCurrency(Number(v));

export function RevenueTrend({ data }: { data: DailyPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={ACCENT} stopOpacity={0.35} />
            <stop offset="100%" stopColor={ACCENT} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="var(--line)" vertical={false} />
        <XAxis dataKey="date" tick={axis} tickFormatter={formatShortDate} minTickGap={28} />
        <YAxis tick={axis} tickFormatter={formatCompactCurrency} width={60} />
        <Tooltip
          contentStyle={tooltipStyle}
          labelFormatter={(l) => formatShortDate(String(l))}
          formatter={(v) => [money(v), "Revenue"]}
        />
        <Area
          isAnimationActive={false}
          type="monotone"
          dataKey="revenue"
          stroke={ACCENT}
          strokeWidth={2}
          fill="url(#rev)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function HorizontalBars({ data }: { data: Breakdown[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="var(--line)" horizontal={false} />
        <XAxis type="number" tick={axis} tickFormatter={formatCompactCurrency} />
        <YAxis type="category" dataKey="name" tick={axis} width={120} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v) => [money(v), "Revenue"]}
          cursor={{ fill: "var(--hover)" }}
        />
        <Bar
          isAnimationActive={false}
          dataKey="revenue"
          fill={ACCENT}
          radius={[0, 6, 6, 0]}
          barSize={22}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function Donut({ data }: { data: Breakdown[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Tooltip contentStyle={tooltipStyle} formatter={(v, n) => [money(v), String(n)]} />
        <Pie
          isAnimationActive={false}
          data={data}
          dataKey="revenue"
          nameKey="name"
          innerRadius="55%"
          outerRadius="85%"
          paddingAngle={2}
          stroke="var(--card)"
        >
          {data.map((d, i) => (
            <Cell key={d.name} fill={SERIES[i % SERIES.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}

export function Legend({ data }: { data: Breakdown[] }) {
  const total = data.reduce((sum, d) => sum + d.revenue, 0);
  return (
    <ul className="legend">
      {data.map((d, i) => (
        <li key={d.name}>
          <span className="swatch" style={{ background: SERIES[i % SERIES.length] }} />
          <span className="legend-name">{d.name}</span>
          <span className="legend-value">
            {formatCompactCurrency(d.revenue)} · {((d.revenue / total) * 100).toFixed(0)}%
          </span>
        </li>
      ))}
    </ul>
  );
}
