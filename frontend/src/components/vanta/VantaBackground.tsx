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
}

interface VantaBackgroundProps {
  className?: string;
  particleCount?: number;
  maxDistance?: number;
  mouseRepulsion?: boolean;
}

/**
 * High-performance 3D Geometric Mesh Background inspired by Vanta.js NET.
 * Features 3D coordinate projection, interactive cursor repulsion & parallax tilt,
 * and seamless theme-integrated neon filaments.
 */
export default function VantaBackground({
  className = '',
  particleCount = 45,
  maxDistance = 140,
  mouseRepulsion = true,
}: VantaBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { enabled, systemReduced } = useMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    // Check jsdom or reduced motion
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

    // Initialize 3D points
    const points: VantaPoint[] = [];
    const count = Math.min(particleCount, Math.floor((width * height) / 18000));

    for (let i = 0; i < count; i++) {
      points.push({
        x: (Math.random() - 0.5) * width * 1.2,
        y: (Math.random() - 0.5) * height * 1.2,
        z: Math.random() * 400 - 200,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        vz: (Math.random() - 0.5) * 0.35,
        baseRadius: Math.random() * 1.6 + 1.2,
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

    // 3D Perspective settings
    const fov = 350;

    const render = () => {
      if (!isVisible || document.hidden || !enabled) {
        animFrameId = requestAnimationFrame(render);
        return;
      }

      ctx.clearRect(0, 0, width, height);

      // Smooth mouse interpolation (inertia)
      mouseX += (targetMouseX - mouseX) * 0.045;
      mouseY += (targetMouseY - mouseY) * 0.045;

      const tiltX = (mouseY / height) * 0.22;
      const tiltY = (mouseX / width) * 0.22;
      const cosX = Math.cos(tiltX);
      const sinX = Math.sin(tiltX);
      const cosY = Math.cos(tiltY);
      const sinY = Math.sin(tiltY);

      // Project points to 2D
      const projected: { px: number; py: number; scale: number; alpha: number }[] = [];

      for (let i = 0; i < points.length; i++) {
        const p = points[i];

        // Natural movement
        p.x += p.vx;
        p.y += p.vy;
        p.z += p.vz;

        // Boundaries wrap
        const boundX = (width * 1.2) / 2;
        const boundY = (height * 1.2) / 2;
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

        // Interactive cursor repulsion
        if (mouseRepulsion && isHovered) {
          const mRealX = mouseX + width / 2;
          const mRealY = mouseY + height / 2;
          const dx = px - mRealX;
          const dy = py - mRealY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 130 && dist > 0) {
            const force = (1 - dist / 130) * 18;
            px += (dx / dist) * force;
            py += (dy / dist) * force;
          }
        }

        const alpha = Math.max(0.12, Math.min(0.85, (scale - 0.5) * 1.2));
        projected.push({ px, py, scale, alpha });
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
            const lineAlpha = (1 - dist / maxDistance) * 0.28 * Math.min(p1.alpha, p2.alpha);
            ctx.beginPath();
            ctx.moveTo(p1.px, p1.py);
            ctx.lineTo(p2.px, p2.py);
            // ReviewPulse violet / electric-blue filament
            ctx.strokeStyle = `rgba(167, 139, 250, ${lineAlpha})`;
            ctx.lineWidth = Math.max(0.6, (1 - dist / maxDistance) * 1.4);
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      for (let i = 0; i < projected.length; i++) {
        const { px, py, scale, alpha } = projected[i];
        const radius = Math.max(1, scale * 2.2);

        ctx.beginPath();
        ctx.arc(px, py, radius, 0, Math.PI * 2);
        // Gradient node color with cyan and magenta accents
        ctx.fillStyle = i % 3 === 0 ? `rgba(125, 45, 225, ${alpha})` : `rgba(191, 137, 255, ${alpha})`;
        ctx.fill();

        // Node glow
        if (radius > 1.8) {
          ctx.beginPath();
          ctx.arc(px, py, radius * 2.2, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(125, 45, 225, ${alpha * 0.22})`;
          ctx.fill();
        }
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
      <canvas ref={canvasRef} className="w-full h-full block opacity-60" />
    </div>
  );
}
