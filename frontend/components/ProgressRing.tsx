import { View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';

export function ProgressRing({
  progress,
  size = 88,
  strokeWidth = 6,
  color = '#2F6FED',
  trackColor = '#E5E7EB',
}: {
  /** 0 to 1 */
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  trackColor?: string;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - Math.min(Math.max(progress, 0), 1));

  return (
    <View style={{ width: size, height: size }}>
      <Svg width={size} height={size}>
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={trackColor}
          strokeWidth={strokeWidth}
          fill="none"
        />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          rotation={-90}
          origin={`${size / 2}, ${size / 2}`}
        />
      </Svg>
    </View>
  );
}
