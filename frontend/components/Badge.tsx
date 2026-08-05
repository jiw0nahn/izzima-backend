import { StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';
import type { BadgeVariant } from '@/types/home';

const VARIANT_STYLES: Record<BadgeVariant, { backgroundColor: string; color: string }> = {
  danger: { backgroundColor: '#EF4444', color: '#FFFFFF' },
  info: { backgroundColor: '#DBEAFE', color: '#2563EB' },
};

export function Badge({ label, variant }: { label: string; variant: BadgeVariant }) {
  const { backgroundColor, color } = VARIANT_STYLES[variant];
  return (
    <View style={[styles.badge, { backgroundColor }]}>
      <Text weight="bold" style={[styles.label, { color }]}>
        {label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
  },
  label: {
    fontSize: 12,
  },
});
