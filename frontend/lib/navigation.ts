import { router } from 'expo-router';

// Wraps router.back() with a fallback for when there's nothing to go back to
// — e.g. a Fast Refresh reset the nav stack while a pushed screen was open,
// or the screen was opened directly via a deep link. Calling router.back()
// in that state throws "GO_BACK was not handled by any navigator" instead of
// silently no-op-ing, so every back button needs this guard rather than
// calling router.back() directly.
export function goBack(fallbackHref: string = '/') {
  if (router.canGoBack()) {
    router.back();
  } else {
    router.replace(fallbackHref);
  }
}
