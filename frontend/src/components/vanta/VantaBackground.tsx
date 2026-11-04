import { useEffect, useRef } from 'react';
import { useMotion } from '@/hooks/useMotion';

interface VantaPoint {
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
  baseRadius: number;
  color: string;
}

interface VantaBackgroundProps {
  className?: string;
  particleCount?: number;
  maxDistance?: number;
  mouseRepulsion?: boolean;
}

/**
 * Vivid, high-performance 3D Geometric Mesh Background inspired by Vanta.js NET.
 * Features 3D coordinate projection, luminous neon filaments, glowing nodes,
 * and an interactive cursor energy wave.
 */
export default function VantaBackground({
  className = '',
  particleCount = 65,
  maxDistance = 175,
  mouseRepulsion = true,
}: VantaBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { enabled, systemReduced } = useMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx || systemReduced) return;

    let width = (canvas.width = container.clientWidth);
    let height = (canvas.height = container.clientHeight);

    let mouseX = width / 2;
    let mouseY = height / 2;
    let targetMouseX = width / 2;
    let targetMouseY = height / 2;
    let isHovered = false;
    let isVisible = true;
    let animFrameId: number;

    const colors = [
      'rgba(191, 137, 255, ', // Primary neon lavender
      'rgba(125, 45, 225, ',  // Deep action violet
      'rgba(224, 99, 239, ',  // Magenta pulse
      'rgba(70, 221, 189, ',  // Emerald cyan
      'rgba(135, 187, 255, ', // Electric blue
    ];

    // Initialize 3D points
    const points: VantaPoint[] = [];
    const count = Math.min(particleCount, Math.floor((width * height) / 14000));

    for (let i = 0; i < count; i++) {
      points.push({
        x: (Math.random() - 0.5) * width * 1.3,
        y: (Math.random() - 0.5) * height * 1.3,
        z: Math.random() * 450 - 225,
        vx: (Math.random() - 0.5) * 0.55,
        vy: (Math.random() - 0.5) * 0.55,
        vz: (Math.random() - 0.5) * 0.4,
        baseRadius: Math.random() * 2 + 1.8,
        color: colors[i % colors.length],
      });
    }

    const onResize = () => {
      if (!container || !canvas) return;
      width = canvas.width = container.clientWidth;
      height = canvas.height = container.clientHeight;
    };
    window.addEventListener('resize', onResize);

    const onMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      targetMouseX = e.clientX - rect.left - width / 2;
      targetMouseY = e.clientY - rect.top - height / 2;
      isHovered = true;
    };

    const onMouseLeave = () => {
      isHovered = false;
      targetMouseX = 0;
      targetMouseY = 0;
    };

    window.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseleave', onMouseLeave);

    const observer = new IntersectionObserver(
      ([entry]) => {
        isVisible = entry.isIntersecting;
      },
      { threshold: 0.05 }
    );
    observer.observe(container);

    const fov = 380;

    const render = () => {
      if (!isVisible || document.hidden || !enabled) {
        animFrameId = requestAnimationFrame(render);
        return;
      }

      ctx.clearRect(0, 0, width, height);

      // Smooth mouse interpolation
      mouseX += (targetMouseX - mouseX) * 0.06;
      mouseY += (targetMouseY - mouseY) * 0.06;

      const mRealX = mouseX + width / 2;
      const mRealY = mouseY + height / 2;

      // Interactive cursor glow wave in background
      if (isHovered) {
        const aura = ctx.createRadialGradient(mRealX, mRealY, 0, mRealX, mRealY, 180);
        aura.addColorStop(0, 'rgba(191, 137, 255, 0.16)');
        aura.addColorStop(0.4, 'rgba(125, 45, 225, 0.07)');
        aura.addColorStop(1, 'rgba(10, 7, 17, 0)');
        ctx.fillStyle = aura;
        ctx.beginPath();
        ctx.arc(mRealX, mRealY, 180, 0, Math.PI * 2);
        ctx.fill();
      }

      const tiltX = (mouseY / height) * 0.28;
      const tiltY = (mouseX / width) * 0.28;
      const cosX = Math.cos(tiltX);
      const sinX = Math.sin(tiltX);
      const cosY = Math.cos(tiltY);
      const sinY = Math.sin(tiltY);

      // Project points to 2D
      const projected: { px: number; py: number; scale: number; alpha: number; color: string; radius: number }[] = [];

      for (let i = 0; i < points.length; i++) {
        const p = points[i];

        // Motion drift
        p.x += p.vx;
        p.y += p.vy;
        p.z += p.vz;

        // Toroidal boundary wrap
        const boundX = (width * 1.3) / 2;
        const boundY = (height * 1.3) / 2;
        if (p.x < -boundX) p.x = boundX;
        if (p.x > boundX) p.x = -boundX;
        if (p.y < -boundY) p.y = boundY;
        if (p.y > boundY) p.y = -boundY;
        if (p.z < -225) p.z = 225;
        if (p.z > 225) p.z = -225;

        // 3D rotation based on mouse tilt
        const rotY_x = p.x * cosY + p.z * sinY;
        const rotY_z = -p.x * sinY + p.z * cosY;

        const rotX_y = p.y * cosX - rotY_z * sinX;
        const rotX_z = p.y * sinX + rotY_z * cosX;

        const depth = rotX_z + fov;
        if (depth <= 10) continue;

        const scale = fov / depth;
        let px = rotY_x * scale + width / 2;
        let py = rotX_y * scale + height / 2;

        // Interactive cursor repulsion
        if (mouseRepulsion && isHovered) {
          const dx = px - mRealX;
          const dy = py - mRealY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 160 && dist > 0) {
            const force = (1 - dist / 160) * 26;
            px += (dx / dist) * force;
            py += (dy / dist) * force;
          }
        }

        const alpha = Math.max(0.25, Math.min(0.95, (scale - 0.4) * 1.35));
        projected.push({ px, py, scale, alpha, color: p.color, radius: p.baseRadius * scale });
      }

      // Draw Vanta-style connecting filaments
      for (let i = 0; i < projected.length; i++) {
        const p1 = projected[i];
        for (let j = i + 1; j < projected.length; j++) {
          const p2 = projected[j];
          const dx = p1.px - p2.px;
          const dy = p1.py - p2.py;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < maxDistance) {
            const lineAlpha = (1 - dist / maxDistance) * 0.45 * Math.min(p1.alpha, p2.alpha);
            ctx.beginPath();
            ctx.moveTo(p1.px, p1.py);
            ctx.lineTo(p2.px, p2.py);
            ctx.strokeStyle = `rgba(180, 140, 255, ${lineAlpha})`;
            ctx.lineWidth = Math.max(0.7, (1 - dist / maxDistance) * 1.8);
            ctx.stroke();
          }
        }
      }

      // Draw glowing nodes
      for (let i = 0; i < projected.length; i++) {
        const { px, py, alpha, color, radius } = projected[i];

        // Outer glow
        ctx.beginPath();
        ctx.arc(px, py, radius * 2.4, 0, Math.PI * 2);
        ctx.fillStyle = `${color}${alpha * 0.25})`;
        ctx.fill();

        // Inner solid core
        ctx.beginPath();
        ctx.arc(px, py, radius, 0, Math.PI * 2);
        ctx.fillStyle = `${color}${alpha})`;
        ctx.fill();
      }

      animFrameId = requestAnimationFrame(render);
    };

    animFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animFrameId);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseleave', onMouseLeave);
      observer.disconnect();
    };
  }, [enabled, systemReduced, particleCount, maxDistance, mouseRepulsion]);

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      className={`absolute inset-0 pointer-events-none overflow-hidden select-none ${className}`}
    >
      <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
}
