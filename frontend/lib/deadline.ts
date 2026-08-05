import type { BadgeVariant } from '@/types/home';

// Single source of truth for "how urgent is this deadline" — was previously
// duplicated (as a hardcoded `dDay`/`badgeVariant` pair on mock items, and
// again as a local threshold constant in the calendar screen), which is how
// the home screen's and calendar's expiring-item lists drifted out of sync
// with each other. Derive both the label and the color from `daysLeft`.
export const URGENT_THRESHOLD_DAYS = 2;

export function isUrgent(daysLeft: number): boolean {
  return daysLeft <= URGENT_THRESHOLD_DAYS;
}

export function getDDayLabel(daysLeft: number): string {
  return `D-${daysLeft}`;
}

export function getBadgeVariant(daysLeft: number): BadgeVariant {
  return isUrgent(daysLeft) ? 'danger' : 'info';
}
