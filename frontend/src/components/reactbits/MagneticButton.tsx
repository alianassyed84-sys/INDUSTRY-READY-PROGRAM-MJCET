import { useRef, type MouseEvent, type ReactNode } from 'react';
import { useMotion } from '@/hooks/useMotion';
import { gsap } from '@/lib/motion';

interface MagneticButtonProps {
  children: ReactNode;
  className?: string;
  strength?: number;
}

/**
 * React Bits Magnetic Button:
 * Magnetically draws towards the mouse cursor on hover using GSAP physics,
 * snapping back with an elastic bounce on mouse leave.
 */
export function MagneticButton({
  children,
  className = '',
  strength = 0.35,
}: MagneticButtonProps) {
  const ref = useRef<HTMLDivElement | null>(null);
  const { enabled, systemReduced } = useMotion();

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!enabled || systemReduced || !ref.current) return;

    const { clientX, clientY } = e;
    const { left, top, width, height } = ref.current.getBoundingClientRect();
    const x = (clientX - (left + width / 2)) * strength;
    const y = (clientY - (top + height / 2)) * strength;

    gsap.to(ref.current, {
      x,
      y,
      duration: 0.3,
      ease: 'power2.out',
    });
  };

  const handleMouseLeave = () => {
    if (!enabled || systemReduced || !ref.current) return;

    gsap.to(ref.current, {
      x: 0,
      y: 0,
      duration: 0.7,
      ease: 'elastic.out(1, 0.4)',
    });
  };

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`inline-block ${className}`}
    >
      {children}
    </div>
  );
}
