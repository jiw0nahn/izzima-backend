// Local-date ISO formatting (YYYY-MM-DD) without going through `toISOString()`,
// which converts to UTC and can shift the date by a day depending on the
// device's timezone. Calendar day math must stay in local time.
export function toLocalISODate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function addDays(base: Date, days: number): Date {
  const result = new Date(base);
  result.setDate(result.getDate() + days);
  return result;
}
