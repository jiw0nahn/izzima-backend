import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

import type { FavoriteKind } from '@/types/home';

export interface FavoriteEntry {
  kind: FavoriteKind;
  id: string;
}

interface FavoritesContextValue {
  favorites: FavoriteEntry[];
  isFavorite: (kind: FavoriteKind, id: string) => boolean;
  toggleFavorite: (kind: FavoriteKind, id: string) => void;
}

const FavoritesContext = createContext<FavoritesContextValue | null>(null);

function favoriteKey(kind: FavoriteKind, id: string): string {
  return `${kind}:${id}`;
}

// In-memory only for now (resets on app restart), same as ThemeContext —
// no persistence layer (AsyncStorage etc.) wired up yet.
export function FavoritesProvider({ children }: { children: ReactNode }) {
  const [favoriteMap, setFavoriteMap] = useState<Map<string, FavoriteEntry>>(new Map());

  const value = useMemo<FavoritesContextValue>(
    () => ({
      favorites: Array.from(favoriteMap.values()),
      isFavorite: (kind, id) => favoriteMap.has(favoriteKey(kind, id)),
      toggleFavorite: (kind, id) => {
        setFavoriteMap((prev) => {
          const next = new Map(prev);
          const key = favoriteKey(kind, id);
          if (next.has(key)) {
            next.delete(key);
          } else {
            next.set(key, { kind, id });
          }
          return next;
        });
      },
    }),
    [favoriteMap],
  );

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>;
}

export function useFavorites(): FavoritesContextValue {
  const context = useContext(FavoritesContext);
  if (!context) {
    throw new Error('useFavorites must be used within a FavoritesProvider');
  }
  return context;
}
