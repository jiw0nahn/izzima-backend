import { StyleSheet, View } from 'react-native';

import { Text } from '@/components/Text';

export default function UploadScreen() {
  return (
    <View style={styles.container}>
      <Text>업로드</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
