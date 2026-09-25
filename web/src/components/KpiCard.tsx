import { formatChange } from "@/lib/format";

interface KpiCardProps {
  label: string;
  value: string;
  changePct?: number | null;
  note?: string;
}

export function KpiCard({ label, value, changePct, note }: KpiCardProps) {
  const change = changePct === undefined ? null : formatChange(changePct);
  return (
    <div className="card kpi">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {change ? (
        <div className={`kpi-delta ${change.trend}`}>
          {change.trend === "up" ? "▲ " : change.trend === "down" ? "▼ " : ""}
          {change.label}
        </div>
      ) : (
        <div className="kpi-delta flat">{note}</div>
      )}
    </div>
  );
}
