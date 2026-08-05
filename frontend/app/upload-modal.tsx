import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { router } from "expo-router";
import { useEffect, useMemo, useState } from "react";
import { Alert, FlatList, Pressable, StyleSheet, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { ProgressRing } from "@/components/ProgressRing";
import { Text } from "@/components/Text";
import {
  UploadThumbnail,
  type UploadThumbnailStatus,
} from "@/components/UploadThumbnail";
import type { ThemeColors } from "@/constants/colors";
import { useTheme } from "@/contexts/ThemeContext";
import { uploadImage } from "@/lib/api";
import { goBack } from "@/lib/navigation";

export default function UploadModalScreen() {
  const [uris, setUris] = useState<string[]>([]);
  const [completed, setCompleted] = useState(0);
  const { colors } = useTheme();
  const styles = useMemo(() => createStyles(colors), [colors]);

  const totalScreenshots = uris.length;
  const hasStarted = totalScreenshots > 0;
  const isDone = hasStarted && completed >= totalScreenshots;

  // Simulates the AI pipeline processing screenshots one by one. Once the
  // real backend/ai pipeline is wired up, this should track actual upload +
  // analysis progress instead of a timer.
  useEffect(() => {
    if (!hasStarted) return;
    let cancelled = false;

    (async () => {
      for (let i = 0; i < uris.length; i++) {
        if (cancelled) return;
        try {
          await uploadImage(uris[i]);
        } catch (err) {
          console.warn("업로드 실패", uris[i], err);
          // 실패한 항목을 어떻게 표시할지는 UploadThumbnailStatus에 'error' 상태를
          // 추가할지 말지 포함해서 정하시면 돼요 — 지금은 일단 넘어가는 것도 방법
        }
        if (!cancelled) setCompleted((prev) => prev + 1);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [hasStarted]);

  const handlePickFromGallery = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert(
        "갤러리 접근 권한이 필요해요",
        "설정에서 사진 보관함 접근을 허용해주세요.",
      );
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      allowsMultipleSelection: true,
      quality: 0.8,
    });
    if (result.canceled || result.assets.length === 0) return;

    setCompleted(0);
    setUris(result.assets.map((asset) => asset.uri));
  };

  const progress = hasStarted ? completed / totalScreenshots : 0;
  const percent = Math.round(progress * 100);

  const thumbnails = uris.map((uri, index) => {
    const status: UploadThumbnailStatus =
      index < completed
        ? "done"
        : index === completed && !isDone
          ? "processing"
          : "pending";
    return { id: `upload-${index}`, uri, status };
  });

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <View style={styles.header}>
        <Pressable onPress={() => goBack()} hitSlop={8}>
          <Text style={styles.cancelLabel}>취소</Text>
        </Pressable>
        <Text weight="semiBold" style={styles.headerTitle}>
          가져오기
        </Text>
        <Pressable
          disabled={!isDone}
          onPress={() =>
            router.push({
              pathname: "/upload-review",
              params: { uris: JSON.stringify(uris) },
            })
          }
          hitSlop={8}
        >
          <Text
            weight="semiBold"
            style={[styles.doneLabel, !isDone && styles.doneLabelDisabled]}
          >
            완료
          </Text>
        </Pressable>
      </View>

      {!hasStarted ? (
        <View style={styles.pickerSection}>
          <View style={styles.pickerIconWrapper}>
            <Ionicons name="images-outline" size={40} color="#2F6FED" />
          </View>
          <Text weight="bold" style={styles.pickerTitle}>
            갤러리에서 스크린샷을 가져와보세요
          </Text>
          <Text style={styles.pickerSubtitle}>
            쿠폰, 티켓, 영수증 등을 자동으로{"\n"}인식하고 정리해드려요
          </Text>
          <Pressable
            style={styles.pickerButton}
            onPress={handlePickFromGallery}
          >
            <Ionicons name="images" size={18} color="#fff" />
            <Text weight="semiBold" style={styles.pickerButtonLabel}>
              갤러리에서 선택
            </Text>
          </Pressable>
        </View>
      ) : (
        <>
          <View style={styles.statusSection}>
            <ProgressRing progress={progress} />
            <Text weight="bold" style={styles.statusTitle}>
              {isDone ? "분석 완료!" : "분석 중..."}
            </Text>
            {!isDone && (
              <Text style={styles.statusSubtitle}>
                텍스트 인식 · 카테고리 분류{"\n"}만료일 추출 중
              </Text>
            )}
          </View>

          <View style={styles.progressBarTrack}>
            <View style={[styles.progressBarFill, { width: `${percent}%` }]} />
          </View>
          <View style={styles.progressStatsRow}>
            <Text style={styles.progressStatsLabel}>
              {completed} / {totalScreenshots}장 완료
            </Text>
            <Text style={styles.progressStatsLabel}>{percent}%</Text>
          </View>

          <FlatList
            data={thumbnails}
            keyExtractor={(item) => item.id}
            numColumns={4}
            columnWrapperStyle={styles.row}
            contentContainerStyle={styles.grid}
            renderItem={({ item }) => (
              <View style={styles.thumbnailWrapper}>
                <UploadThumbnail uri={item.uri} status={item.status} />
              </View>
            )}
          />
        </>
      )}
    </SafeAreaView>
  );
}

const createStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      paddingHorizontal: 20,
      marginTop: 12,
      paddingBottom: 8,
    },
    cancelLabel: {
      fontSize: 16,
      color: "#2F6FED",
    },
    headerTitle: {
      fontSize: 16,
      color: colors.text,
    },
    doneLabel: {
      fontSize: 16,
      color: "#2F6FED",
    },
    doneLabelDisabled: {
      color: colors.textPlaceholder,
    },
    pickerSection: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      paddingHorizontal: 32,
      marginTop: -40,
    },
    pickerIconWrapper: {
      width: 88,
      height: 88,
      borderRadius: 44,
      backgroundColor: "#DBEAFE",
      alignItems: "center",
      justifyContent: "center",
      marginBottom: 20,
    },
    pickerTitle: {
      fontSize: 18,
      color: colors.text,
      textAlign: "center",
    },
    pickerSubtitle: {
      fontSize: 13,
      color: colors.textMuted,
      textAlign: "center",
      marginTop: 8,
      lineHeight: 18,
    },
    pickerButton: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      backgroundColor: "#2F6FED",
      borderRadius: 14,
      paddingVertical: 16,
      paddingHorizontal: 28,
      marginTop: 28,
    },
    pickerButtonLabel: {
      fontSize: 16,
      color: "#FFFFFF",
    },
    statusSection: {
      alignItems: "center",
      marginTop: 24,
      marginBottom: 24,
    },
    statusTitle: {
      fontSize: 18,
      color: colors.text,
      marginTop: 16,
    },
    statusSubtitle: {
      fontSize: 13,
      color: colors.textMuted,
      textAlign: "center",
      marginTop: 6,
      lineHeight: 18,
    },
    progressBarTrack: {
      height: 6,
      borderRadius: 3,
      backgroundColor: colors.surface,
      marginHorizontal: 20,
      overflow: "hidden",
    },
    progressBarFill: {
      height: "100%",
      borderRadius: 3,
      backgroundColor: "#2F6FED",
    },
    progressStatsRow: {
      flexDirection: "row",
      justifyContent: "space-between",
      paddingHorizontal: 20,
      marginTop: 8,
      marginBottom: 16,
    },
    progressStatsLabel: {
      fontSize: 13,
      color: colors.textMuted,
    },
    grid: {
      paddingHorizontal: 20,
      paddingBottom: 32,
    },
    row: {
      justifyContent: "flex-start",
      gap: 10,
      marginBottom: 10,
    },
    thumbnailWrapper: {
      width: "22%",
    },
  });
