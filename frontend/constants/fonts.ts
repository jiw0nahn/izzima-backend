// Pretendard ships one static font file per weight (not a single variable font),
// so weight must be selected via `fontFamily`, not React Native's `fontWeight`.
export const fontFamily = {
  regular: 'Pretendard-Regular',
  semiBold: 'Pretendard-SemiBold',
  bold: 'Pretendard-Bold',
  extraBold: 'Pretendard-ExtraBold',
} as const;

export type FontWeightToken = keyof typeof fontFamily;
