import type { ReactNode } from 'react';
import { useMotion } from '@/hooks/useMotion';

interface ShinyTextProps {
  children: ReactNode;
  className?: string;
  speed?: number; // duration in seconds
}

/**
 * React Bits Shiny Text:
 * Continuous linear light sweep across typography.
 */
export function ShinyText({
  children,
  className = '',
  speed = 4,
}: ShinyTextProps) {
  const { enabled, systemReduced } = useMotion();

  if (!enabled || systemReduced) {
    return <span className={className}>{children}</span>;
  }

  return (
    <span
      style={{
        animationDuration: `${speed}s`,
      }}
      className={`inline-block bg-[linear-gradient(110deg,#F5F0FF,45%,#C446EF,55%,#F5F0FF)] bg-[length:250%_100%] bg-clip-text text-transparent animate-shiny-sweep ${className}`}
    >
      {children}
    </span>
  );
}
