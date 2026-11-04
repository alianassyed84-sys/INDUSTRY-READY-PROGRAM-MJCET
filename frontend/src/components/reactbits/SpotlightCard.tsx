import { useRef, useState, type MouseEvent, type ReactNode } from 'react';
import { useMotion } from '@/hooks/useMotion';

interface SpotlightCardProps {
  children: ReactNode;
  className?: string;
  spotlightColor?: string;
  borderGlowColor?: string;
}

/**
 * React Bits Spotlight Card:
 * Smoothly tracks mouse coordinates to cast an ambient radial spotlight
 * across the card surface and high-contrast border refraction.
 */
export function SpotlightCard({
  children,
  className = '',
  spotlightColor = 'rgba(191, 137, 255, 0.18)',
  borderGlowColor = 'rgba(191, 137, 255, 0.45)',
}: SpotlightCardProps) {
  const cardRef = useRef<HTMLDivElement | null>(null);
  const [position, setPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const { enabled } = useMotion();

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!enabled || !cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setPosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative overflow-hidden rounded-2xl border border-rp-border bg-rp-surface transition-all duration-300 shadow-xl ${className}`}
    >
      {/* React Bits Ambient Spotlight Glow */}
      {enabled && isHovered && (
        <>
          <div
            className="pointer-events-none absolute -inset-px transition-opacity duration-300 z-10"
            style={{
              opacity: isHovered ? 1 : 0,
              background: `radial-gradient(420px circle at ${position.x}px ${position.y}px, ${borderGlowColor}, transparent 70%)`,
            }}
          />
          <div
            className="pointer-events-none absolute inset-0 transition-opacity duration-300 z-10"
            style={{
              opacity: isHovered ? 1 : 0,
              background: `radial-gradient(380px circle at ${position.x}px ${position.y}px, ${spotlightColor}, transparent 80%)`,
            }}
          />
        </>
      )}

      {/* Card Content */}
      <div className="relative z-20">{children}</div>
    </div>
  );
}
