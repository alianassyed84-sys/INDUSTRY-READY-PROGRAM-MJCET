import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { prefersReducedMotion } from '@/lib/motion';

/**
 * Decorative 3D hero: a glossy violet core ringed by a pulse-line torus and
 * orbiting "star" beads. Purely illustrative, with no data. Falls back to a CSS orb.
 */
export default function ThreeHero() {
  const host = useRef<HTMLDivElement>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const el = host.current;
    if (!el) return;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    } catch {
      setFailed(true);
      return;
    }
    const reduce = prefersReducedMotion();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    renderer.domElement.setAttribute('aria-hidden', 'true');
    el.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 0, 13.5);

    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(4, 5, 6); scene.add(key);
    const rim = new THREE.PointLight(0xf36b57, 40, 30); rim.position.set(-5, -2, 3); scene.add(rim);
    const glow = new THREE.PointLight(0x7138f5, 60, 30); glow.position.set(3, -4, 4); scene.add(glow);

    const group = new THREE.Group();
    scene.add(group);

    const core = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.7, 24),
      new THREE.MeshPhysicalMaterial({ color: 0x7138f5, roughness: 0.18, metalness: 0.1, clearcoat: 1, clearcoatRoughness: 0.15, sheen: 1, sheenColor: new THREE.Color(0xe5d8ff) }),
    );
    const base = (core.geometry.attributes.position as THREE.BufferAttribute).array.slice() as Float32Array;
    group.add(core);

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(2.7, 0.045, 24, 220),
      new THREE.MeshStandardMaterial({ color: 0x171b50, roughness: 0.3, metalness: 0.6 }),
    );
    ring.rotation.x = Math.PI / 2.4;
    group.add(ring);

    const ring2 = ring.clone();
    ring2.scale.setScalar(1.28);
    ring2.rotation.set(Math.PI / 3.1, 0.5, 0);
    ring2.material = new THREE.MeshStandardMaterial({ color: 0xb79bfa, roughness: 0.35, metalness: 0.4 });
    group.add(ring2);

    // orbiting beads (rating "stars")
    const beadGeo = new THREE.OctahedronGeometry(0.17, 0);
    const beads: { m: THREE.Mesh; r: number; s: number; o: number; t: number }[] = [];
    for (let i = 0; i < 14; i++) {
      const warm = i % 5 === 0;
      const m = new THREE.Mesh(beadGeo, new THREE.MeshStandardMaterial({ color: warm ? 0xf36b57 : 0xffffff, roughness: 0.25, metalness: 0.35 }));
      const b = { m, r: 2.7 + (i % 3) * 0.35, s: 0.25 + (i % 4) * 0.06, o: (i / 14) * Math.PI * 2, t: (i % 5) * 0.35 - 0.7 };
      beads.push(b); group.add(m);
    }

    const resize = () => {
      const w = el.clientWidth || 1; const h = el.clientHeight || 1;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.position.z = w < 420 ? 17 : 13.5;
      camera.updateProjectionMatrix();
    };
    resize();
    const ro = new ResizeObserver(resize); ro.observe(el);

    const target = { x: 0, y: 0 };
    const onMove = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      target.x = ((e.clientX - r.left) / r.width - 0.5) * 2;
      target.y = ((e.clientY - r.top) / r.height - 0.5) * 2;
    };
    if (!reduce) window.addEventListener('pointermove', onMove, { passive: true });

    let visible = true;
    const io = new IntersectionObserver(([en]) => { visible = en.isIntersecting; }, { threshold: 0.01 });
    io.observe(el);

    const pos = core.geometry.attributes.position as THREE.BufferAttribute;
    const v = new THREE.Vector3();
    const clock = new THREE.Clock();
    let raf = 0;

    const frame = () => {
      raf = requestAnimationFrame(frame);
      if (!visible && !reduce) return;
      const t = clock.getElapsedTime();
      if (!reduce) {
        // soft organic "pulse" displacement
        for (let i = 0; i < pos.count; i++) {
          v.set(base[i * 3], base[i * 3 + 1], base[i * 3 + 2]);
          const n = Math.sin(v.x * 1.6 + t * 1.3) * Math.cos(v.y * 1.4 + t * 1.1) * 0.07 + Math.sin(v.z * 2 + t * 1.7) * 0.03;
          v.normalize().multiplyScalar(1.7 + n + Math.max(0, Math.sin(t * 2.2)) * 0.04);
          pos.setXYZ(i, v.x, v.y, v.z);
        }
        pos.needsUpdate = true;
        core.geometry.computeVertexNormals();
        ring.rotation.z = t * 0.25; ring2.rotation.z = -t * 0.18;
        beads.forEach((b) => {
          const a = b.o + t * b.s;
          b.m.position.set(Math.cos(a) * b.r, b.t + Math.sin(a * 1.5) * 0.25, Math.sin(a) * b.r);
          b.m.rotation.x = t; b.m.rotation.y = t * 0.8;
        });
        group.rotation.y += (target.x * 0.5 - group.rotation.y) * 0.05;
        group.rotation.x += (target.y * 0.3 - group.rotation.x) * 0.05;
        group.position.y = Math.sin(t * 0.9) * 0.12;
      } else {
        beads.forEach((b) => b.m.position.set(Math.cos(b.o) * b.r, b.t, Math.sin(b.o) * b.r));
        group.rotation.set(0.25, -0.35, 0);
      }
      renderer.render(scene, camera);
      if (reduce) { cancelAnimationFrame(raf); }
    };
    frame();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('pointermove', onMove);
      ro.disconnect(); io.disconnect();
      scene.traverse((o) => {
        const m = o as THREE.Mesh;
        if (m.geometry) m.geometry.dispose();
        const mat = m.material as THREE.Material | THREE.Material[] | undefined;
        if (Array.isArray(mat)) mat.forEach((x) => x.dispose()); else mat?.dispose();
      });
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  if (failed) {
    return <div aria-hidden className="mx-auto aspect-square w-3/4 rounded-full bg-[radial-gradient(circle_at_30%_30%,#b79bfa,#7138F5_55%,#171B50)] shadow-lift" />;
  }
  return <div ref={host} className="h-full w-full [&>canvas]:h-full [&>canvas]:w-full" />;
}
