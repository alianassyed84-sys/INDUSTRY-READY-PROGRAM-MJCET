import { useMotion } from '@/hooks/useMotion';

interface BorderBeamProps {
  className?: string;
  duration?: number;
  colorFrom?: string;
  colorTo?: string;
  size?: number;
  borderWidth?: number;
}

/**
 * React Bits Border Beam:
 * High-velocity luminous beam orbiting continuously along the card perimeter.
 */
export function BorderBeam({
  className = '',
  duration = 6,
  colorFrom = '#BF89FF',
  colorTo = '#7D2DE1',
}: BorderBeamProps) {
  const { enabled, systemReduced } = useMotion();

  if (!enabled || systemReduced) return null;

  return (
    <div
      aria-hidden="true"
      className={`pointer-events-none absolute -inset-[1.5px] rounded-[inherit] overflow-hidden ${className}`}
    >
      <div
        style={{
          animationDuration: `${duration}s`,
          background: `conic-gradient(from 0deg, transparent 0deg, transparent 260deg, ${colorTo} 310deg, ${colorFrom} 360deg)`,
        }}
        className="absolute -inset-[200%] animate-spin-beam opacity-90"
      />
    </div>
  );
}
