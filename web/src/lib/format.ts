const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});
const currencyCents = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const compact = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 1,
});

export const formatCurrency = (value: number) => currency.format(value);
export const formatCurrencyCents = (value: number) => currencyCents.format(value);
export const formatCompactCurrency = (value: number) => compact.format(value);
export const formatNumber = (value: number) => value.toLocaleString("en-US");

export type Trend = "up" | "down" | "flat";

export function formatChange(pct: number | null): { label: string; trend: Trend } {
  if (pct === null) return { label: "no previous day", trend: "flat" };
  if (Math.abs(pct) < 0.05) return { label: "0.0% vs previous day", trend: "flat" };
  const trend: Trend = pct > 0 ? "up" : "down";
  const sign = pct > 0 ? "+" : "−";
  return { label: `${sign}${Math.abs(pct).toFixed(1)}% vs previous day`, trend };
}

// Dates are formatted by hand (not toLocaleDateString) so output is identical on
// every machine and Node version — ICU data differs, e.g. "Sep" vs "Sept".
const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const parts = (isoDate: string) => {
  const d = new Date(`${isoDate}T00:00:00Z`); // UTC, so the day never shifts
  return {
    day: DAYS[d.getUTCDay()],
    date: d.getUTCDate(),
    month: MONTHS[d.getUTCMonth()],
    year: d.getUTCFullYear(),
  };
};

/** "2026-09-25" -> "Fri 25 Sep" */
export function formatShortDate(isoDate: string): string {
  const p = parts(isoDate);
  return `${p.day.slice(0, 3)} ${p.date} ${p.month.slice(0, 3)}`;
}

/** "2026-09-25" -> "Friday 25 September 2026" */
export function formatLongDate(isoDate: string): string {
  const p = parts(isoDate);
  return `${p.day} ${p.date} ${p.month} ${p.year}`;
}

export function share(part: number, total: number): string {
  if (total === 0) return "0%";
  return `${((part / total) * 100).toFixed(0)}%`;
}
