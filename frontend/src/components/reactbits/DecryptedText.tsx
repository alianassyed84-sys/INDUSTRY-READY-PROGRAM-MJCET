import { useEffect, useRef, useState } from 'react';
import { useMotion } from '@/hooks/useMotion';

interface DecryptedTextProps {
  text: string;
  speed?: number;
  maxIterations?: number;
  characters?: string;
  className?: string;
  parentClassName?: string;
  animateOn?: 'view' | 'hover';
}

const GLYPHS = 'ABCDEF0123456789!@#$%^&*~<>{}[]=/+';

/**
 * React Bits Decrypted Text:
 * Cybernetic text decryption effect where random glyphs progressively
 * resolve into the target string.
 */
export function DecryptedText({
  text,
  speed = 40,
  maxIterations = 10,
  characters = GLYPHS,
  className = '',
  parentClassName = '',
  animateOn = 'view',
}: DecryptedTextProps) {
  const [displayText, setDisplayText] = useState(text);
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef<HTMLSpanElement | null>(null);
  const { enabled, systemReduced } = useMotion();

  useEffect(() => {
    // If reduced motion is requested or in testing environment, display final text directly
    if (!enabled || systemReduced) {
      setDisplayText(text);
      return;
    }

    if (animateOn === 'hover' && !isHovered) {
      setDisplayText(text);
      return;
    }

    let iteration = 0;
    let intervalId: NodeJS.Timeout;

    const startDecryption = () => {
      intervalId = setInterval(() => {
        setDisplayText(
          text
            .split('')
            .map((char, index) => {
              if (char === ' ') return ' ';
              if (index < iteration) return text[index];
              return characters[Math.floor(Math.random() * characters.length)];
            })
            .join('')
        );

        if (iteration >= text.length) {
          clearInterval(intervalId);
          setDisplayText(text);
        }

        iteration += 1 / (maxIterations / text.length);
      }, speed);
    };

    if (animateOn === 'view') {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            startDecryption();
            observer.disconnect();
          }
        },
        { threshold: 0.1 }
      );
      if (containerRef.current) observer.observe(containerRef.current);
      return () => {
        observer.disconnect();
        clearInterval(intervalId);
      };
    } else {
      startDecryption();
      return () => clearInterval(intervalId);
    }
  }, [text, speed, maxIterations, characters, enabled, systemReduced, isHovered, animateOn]);

  return (
    <span
      ref={containerRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      aria-label={text}
      className={`inline-block font-mono ${parentClassName}`}
    >
      <span className={className}>{displayText}</span>
    </span>
  );
}
