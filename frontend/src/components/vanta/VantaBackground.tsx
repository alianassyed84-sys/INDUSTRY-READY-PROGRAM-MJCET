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
  particleCount = 85,
  maxDistance = 190,
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

    let mouseX = 0;
    let mouseY = 0;
    let targetMouseX = 0;
    let targetMouseY = 0;
    let isHovered = false;
    let isVisible = true;
    let animFrameId: number;

    const colors = [
      'rgba(192, 132, 252, ', // Neon lavender
      'rgba(147, 51, 234, ',  // Electric violet
      'rgba(244, 114, 182, ', // Hot magenta
      'rgba(45, 212, 191, ',  // Radiant turquoise
      'rgba(96, 165, 250, ',  // Electric cyan/blue
    ];

    // Initialize 3D points with balanced density
    const points: VantaPoint[] = [];
    const count = Math.max(65, Math.min(particleCount, Math.floor((width * height) / 9500)));

    for (let i = 0; i < count; i++) {
      points.push({
        x: (Math.random() - 0.5) * width * 1.25,
        y: (Math.random() - 0.5) * height * 1.25,
        z: Math.random() * 400 - 200,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        vz: (Math.random() - 0.5) * 0.35,
        baseRadius: Math.random() * 1.8 + 2.2,
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
      mouseX += (targetMouseX - mouseX) * 0.07;
      mouseY += (targetMouseY - mouseY) * 0.07;

      const mRealX = mouseX + width / 2;
      const mRealY = mouseY + height / 2;

      // Vivid interactive cursor energy wave
      if (isHovered) {
        const aura = ctx.createRadialGradient(mRealX, mRealY, 0, mRealX, mRealY, 220);
        aura.addColorStop(0, 'rgba(192, 132, 252, 0.24)');
        aura.addColorStop(0.35, 'rgba(147, 51, 234, 0.12)');
        aura.addColorStop(0.7, 'rgba(45, 212, 191, 0.05)');
        aura.addColorStop(1, 'rgba(10, 7, 17, 0)');
        ctx.fillStyle = aura;
        ctx.beginPath();
        ctx.arc(mRealX, mRealY, 220, 0, Math.PI * 2);
        ctx.fill();
      }

      const tiltX = (mouseY / height) * 0.24;
      const tiltY = (mouseX / width) * 0.24;
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
        const boundX = (width * 1.25) / 2;
        const boundY = (height * 1.25) / 2;
        if (p.x < -boundX) p.x = boundX;
        if (p.x > boundX) p.x = -boundX;
        if (p.y < -boundY) p.y = boundY;
        if (p.y > boundY) p.y = -boundY;
        if (p.z < -200) p.z = 200;
        if (p.z > 200) p.z = -200;

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

        // Dynamic cursor repulsion wave
        if (mouseRepulsion && isHovered) {
          const dx = px - mRealX;
          const dy = py - mRealY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 180 && dist > 0) {
            const force = (1 - dist / 180) * 32;
            px += (dx / dist) * force;
            py += (dy / dist) * force;
          }
        }

        const alpha = Math.max(0.4, Math.min(1, (scale - 0.45) * 1.5));
        projected.push({ px, py, scale, alpha, color: p.color, radius: p.baseRadius * scale });
      }

      // Draw subtle holographic 3D triangular wireframe faces
      for (let i = 0; i < projected.length; i++) {
        const p1 = projected[i];
        for (let j = i + 1; j < projected.length; j++) {
          const p2 = projected[j];
          const d12 = Math.hypot(p1.px - p2.px, p1.py - p2.py);
          if (d12 > maxDistance * 0.7) continue;
          for (let k = j + 1; k < projected.length; k++) {
            const p3 = projected[k];
            const d23 = Math.hypot(p2.px - p3.px, p2.py - p3.py);
            const d31 = Math.hypot(p3.px - p1.px, p3.py - p1.py);
            if (d23 < maxDistance * 0.7 && d31 < maxDistance * 0.7) {
              ctx.beginPath();
              ctx.moveTo(p1.px, p1.py);
              ctx.lineTo(p2.px, p2.py);
              ctx.lineTo(p3.px, p3.py);
              ctx.closePath();
              ctx.fillStyle = 'rgba(168, 85, 247, 0.045)';
              ctx.fill();
            }
          }
        }
      }

      // Draw luminous connecting filaments
      for (let i = 0; i < projected.length; i++) {
        const p1 = projected[i];
        for (let j = i + 1; j < projected.length; j++) {
          const p2 = projected[j];
          const dx = p1.px - p2.px;
          const dy = p1.py - p2.py;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < maxDistance) {
            const lineAlpha = (1 - dist / maxDistance) * 0.65 * Math.min(p1.alpha, p2.alpha);
            ctx.beginPath();
            ctx.moveTo(p1.px, p1.py);
            ctx.lineTo(p2.px, p2.py);
            ctx.strokeStyle = `rgba(192, 132, 252, ${lineAlpha})`;
            ctx.lineWidth = Math.max(0.75, (1 - dist / maxDistance) * 2.2);
            ctx.stroke();
          }
        }
      }

      // Draw glowing nodes with vibrant outer corolla
      for (let i = 0; i < projected.length; i++) {
        const { px, py, alpha, color, radius } = projected[i];

        // Radiant outer glowing halo
        ctx.beginPath();
        ctx.arc(px, py, radius * 3.4, 0, Math.PI * 2);
        ctx.fillStyle = `${color}${alpha * 0.35})`;
        ctx.fill();

        // Solid luminous core
        ctx.beginPath();
        ctx.arc(px, py, Math.max(1.8, radius), 0, Math.PI * 2);
        ctx.fillStyle = `${color}${Math.min(1, alpha * 1.25)})`;
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
