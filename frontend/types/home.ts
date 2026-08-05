export type BadgeVariant = 'danger' | 'info';

// A single "thing with a deadline" — powers the home screen's "만료 임박"
// section, the /expiring list + detail screens, and the calendar's event
// list/dots. One shared type instead of separate near-duplicate shapes per
// screen, since those drifted out of sync with each other before.
export interface ExpiringItem {
  id: string;
  category: string;
  title: string;
  subtitle: string;
  date: string; // local ISO date, e.g. '2026-07-22', used for calendar dot placement
  daysLeft: number; // D-day and urgency color are derived from this via lib/deadline.ts
  tags: string[];
  location?: string;
}

export interface Category {
  id: string;
  name: string;
  count: number;
}

export type CategoryItemStatus = 'active' | 'expiring' | 'used';

export interface CategoryItem {
  id: string;
  categoryId: string;
  categoryName: string;
  status: CategoryItemStatus;
  title: string;
  tags: string[];
  savedAtLabel: string;
  scheduleDetected: boolean;
}

export type CategoryFilter = 'all' | 'expiring' | 'used';

// One uploaded screenshot going through the post-upload classification
// review step — `categoryId` starts as whatever the (mock) AI pipeline
// guessed and can be corrected by the user before confirming.
export interface UploadReviewItem {
  id: string;
  uri: string;
  categoryId: string;
}

export interface User {
  nickname: string;
}

// The star toggle appears on two unrelated detail screens backed by two
// different mock arrays (ExpiringItem vs CategoryItem) — `kind` says which
// one a favorited id belongs to so the favorites screen knows where to look
// it up and which route to push when it's tapped.
export type FavoriteKind = 'expiring' | 'category-item';
