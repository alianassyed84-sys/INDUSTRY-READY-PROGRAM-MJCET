import { useMotion } from '@/hooks/useMotion';

interface HorizonLineProps {
  className?: string;
  glowColor?: string;
}

/**
 * Otherworldly Laser Horizon Divider with traveling neon photon pulse.
 */
export function LaserHorizon({
  className = '',
  glowColor = '#BF89FF',
}: HorizonLineProps) {
  const { enabled, systemReduced } = useMotion();

  return (
    <div
      aria-hidden="true"
      className={`relative w-full py-12 flex items-center justify-center overflow-hidden pointer-events-none select-none ${className}`}
    >
      {/* Central Thin Laser Beam */}
      <div className="relative w-full max-w-5xl h-px bg-gradient-to-r from-transparent via-rp-primary/50 to-transparent">
        {/* Ambient Glow */}
        <div
          style={{ background: glowColor }}
          className="absolute inset-0 blur-sm opacity-50"
        />

        {/* Moving Photon Pulse */}
        {enabled && !systemReduced && (
          <div className="absolute top-1/2 -translate-y-1/2 w-32 h-1 bg-gradient-to-r from-transparent via-white to-transparent blur-[1px] animate-photon-travel" />
        )}
      </div>
    </div>
  );
}

/**
 * Deep Space Celestial Nebulae for atmospheric depth.
 */
export function CosmicAura() {
  return (
    <div
      aria-hidden="true"
      className="fixed inset-0 pointer-events-none overflow-hidden select-none z-0"
    >
      {/* Upper Violet Celestial Cloud */}
      <div className="absolute -top-[15%] left-[5%] w-[65vw] h-[65vh] rounded-full bg-rp-action/20 blur-[130px] animate-cosmic-drift" />

      {/* Middle Magenta Pulse Nebula */}
      <div className="absolute top-[35%] -right-[10%] w-[55vw] h-[55vh] rounded-full bg-rp-magenta/16 blur-[140px] animate-cosmic-drift-reverse" />

      {/* Lower Cyan Deep Space Glow */}
      <div className="absolute -bottom-[10%] left-[15%] w-[55vw] h-[55vh] rounded-full bg-cyan-500/12 blur-[150px] animate-cosmic-drift" />
    </div>
  );
}
