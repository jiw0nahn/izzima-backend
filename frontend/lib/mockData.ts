import { addDays, toLocalISODate } from '@/lib/date';
import type { Category, CategoryItem, ExpiringItem, User } from '@/types/home';

// Mock data shared across screens until a real backend API is wired up.
// Shape mirrors what the future API responses should look like.

// No auth yet, so there's exactly one (mock) signed-in user.
export const CURRENT_USER: User = {
  nickname: '이태경',
};

export const CATEGORIES: Category[] = [
  { id: '1', name: '공부·시험', count: 24 },
  { id: '2', name: '쿠폰', count: 86 },
  { id: '3', name: '영수증', count: 58 },
  { id: '4', name: '예약·티켓', count: 17 },
  { id: '5', name: '맛집', count: 41 },
  { id: '6', name: '반려동물', count: 12 },
];

// Stand-in for the AI pipeline's category guess on a freshly uploaded
// screenshot. Round-robins through the real category list so the review
// screen has a mix of categories to demo correcting, deterministic on
// upload order rather than random so a given session stays stable.
export function classifyUpload(index: number): Category {
  return CATEGORIES[index % CATEGORIES.length];
}

function buildCategoryItems(categoryId: string, categoryName: string, count: number): CategoryItem[] {
  return Array.from({ length: count }, (_, index) => ({
    id: `${categoryId}-${index}`,
    categoryId,
    categoryName,
    status: index % 4 === 0 ? 'used' : index % 7 === 3 ? 'expiring' : 'active',
    title: `${categoryName} ${index + 1}`,
    tags: [`#${categoryName}`, '#자동분류'],
    savedAtLabel: `6월 ${(index % 28) + 1}일 저장됨`,
    scheduleDetected: false,
  }));
}

export const CATEGORY_ITEMS: CategoryItem[] = CATEGORIES.flatMap((category) =>
  buildCategoryItems(category.id, category.name, category.count),
);

// Every "thing with a deadline" the app has recognized, soonest first. This
// is the one array behind: the home screen's "만료 임박" row, the /expiring
// full-list + detail screens, and the calendar tab's event list/dots.
// `daysLeft` is relative to "today" (computed at module load) rather than a
// frozen date, so this stays correct no matter when the app is opened.
const today = new Date();

interface DeadlineSeed {
  category: string;
  title: string;
  subtitle: string;
  daysLeft: number;
  tags: string[];
  location?: string;
}

const DEADLINE_SEEDS: DeadlineSeed[] = [
  {
    category: '예약·티켓',
    title: '콘서트 티켓',
    subtitle: '내일 오후 7:00',
    daysLeft: 1,
    tags: ['#콘서트', '#QR티켓', '#올림픽홀'],
    location: '올림픽홀',
  },
  {
    category: '쿠폰',
    title: '쿠폰 1',
    subtitle: '2일 후 만료',
    daysLeft: 2,
    tags: ['#쿠폰', '#할인쿠폰'],
  },
  {
    category: '쿠폰',
    title: '배달 20% 쿠폰',
    subtitle: '7월 4일 만료',
    daysLeft: 3,
    tags: ['#배달', '#할인쿠폰'],
  },
  {
    category: '쿠폰',
    title: '쿠폰 4',
    subtitle: '5일 후 만료',
    daysLeft: 5,
    tags: ['#쿠폰', '#할인쿠폰'],
  },
  {
    category: '예약·티켓',
    title: '제주행 비행기',
    subtitle: '7월 8일 오전 9:20',
    daysLeft: 6,
    tags: ['#항공권', '#여행'],
    location: '제주국제공항',
  },
  {
    category: '쿠폰',
    title: '쿠폰 7',
    subtitle: '8일 후 만료',
    daysLeft: 8,
    tags: ['#쿠폰', '#할인쿠폰'],
  },
  // Further-out items: still show up on the calendar, but are past the
  // "만료 임박" window so they don't appear in the home/full-list screens.
  { category: '쿠폰', title: '쿠폰 8', subtitle: '10일 후 만료', daysLeft: 10, tags: ['#쿠폰'] },
  { category: '쿠폰', title: '쿠폰 9', subtitle: '12일 후 만료', daysLeft: 12, tags: ['#쿠폰'] },
  { category: '쿠폰', title: '쿠폰 10', subtitle: '15일 후 만료', daysLeft: 15, tags: ['#쿠폰'] },
  { category: '쿠폰', title: '쿠폰 11', subtitle: '18일 후 만료', daysLeft: 18, tags: ['#쿠폰'] },
  { category: '쿠폰', title: '쿠폰 12', subtitle: '21일 후 만료', daysLeft: 21, tags: ['#쿠폰'] },
  { category: '쿠폰', title: '쿠폰 13', subtitle: '25일 후 만료', daysLeft: 25, tags: ['#쿠폰'] },
];

export const DEADLINE_ITEMS: ExpiringItem[] = DEADLINE_SEEDS.map((seed, index) => ({
  id: `deadline-${index}`,
  category: seed.category,
  title: seed.title,
  subtitle: seed.subtitle,
  daysLeft: seed.daysLeft,
  date: toLocalISODate(addDays(today, seed.daysLeft)),
  tags: seed.tags,
  location: seed.location,
}));

// "만료 임박" (expiring soon) window used by the home screen and /expiring —
// only the soonest items, not every recognized calendar event.
const EXPIRING_SOON_WINDOW_DAYS = 8;

export const EXPIRING_ITEMS: ExpiringItem[] = DEADLINE_ITEMS.filter(
  (item) => item.daysLeft <= EXPIRING_SOON_WINDOW_DAYS,
);

// The calendar tab shows every recognized event, not just the urgent ones.
export const CALENDAR_EVENTS: ExpiringItem[] = DEADLINE_ITEMS;
