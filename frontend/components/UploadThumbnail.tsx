import { Ionicons } from '@expo/vector-icons';
import { useMemo } from 'react';
import { Image, StyleSheet, View } from 'react-native';

import type { ThemeColors } from '@/constants/colors';
import { useTheme } from '@/contexts/ThemeContext';

export type UploadThumbnailStatus = 'pending' | 'processing' | 'done';

export function UploadThumbnail({ uri, status }: { uri?: string; status: UploadThumbnailStatus }) {
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={[styles.thumbnail, status === 'processing' && styles.thumbnailProcessing]}>
      {uri && <Image source={{ uri }} style={styles.image} />}
      {status === 'done' && (
        <View style={styles.badge}>
          <Ionicons name="checkmark" size={11} color="#fff" />
        </View>
      )}
    </View>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    thumbnail: {
      width: '100%',
      aspectRatio: 1,
      borderRadius: 12,
      backgroundColor: colors.surface,
      overflow: 'hidden',
    },
    thumbnailProcessing: {
      borderWidth: 1.5,
      borderColor: '#2F6FED',
    },
    image: {
      width: '100%',
      height: '100%',
    },
    badge: {
      position: 'absolute',
      right: 6,
      bottom: 6,
      width: 16,
      height: 16,
      borderRadius: 8,
      backgroundColor: '#22C55E',
      alignItems: 'center',
      justifyContent: 'center',
    },
  });
