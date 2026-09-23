/**
 * EarthScene — Full cinematic 3D scene container.
 *
 * Camera: slightly above and angled (matches Dribbble reference composition)
 *   - Earth slightly right-of-center, camera angled top-right to bottom-left
 *   - Satellites have natural depth as they pass behind/in front
 *
 * Lighting: single dominant directional "sun" + dim ambient fill
 *
 * Suspense: shows a subtle wireframe loading sphere until textures resolve
 */

import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Stars, AdaptiveDpr } from '@react-three/drei';
import * as THREE from 'three';
import EarthCanvas from './EarthCanvas';
import SatelliteLayer from './SatelliteLayer';

/* ── Lighting ──────────────────────────────────────────────────── */
function SceneLighting() {
  return (
    <>
      {/* Near-black ambient — only the shader's sun drives surface light */}
      <ambientLight intensity={0.04} color="#0d1a30" />

      {/* Primary sun — warm-white, from top-right */}
      <directionalLight
        position={[8, 4, 6]}
        intensity={3.2}
        color="#fffaf0"
      />

      {/* Dim earth-shine fill from opposite side */}
      <directionalLight
        position={[-5, -2, -4]}
        intensity={0.06}
        color="#1a3066"
      />
    </>
  );
}

/* ── Loading placeholder ───────────────────────────────────────── */
function EarthShell() {
  return (
    <mesh>
      <sphereGeometry args={[2.0, 24, 24]} />
      <meshBasicMaterial color="#0a1a35" wireframe opacity={0.18} transparent />
    </mesh>
  );
}

/* ── EarthScene ────────────────────────────────────────────────── */
export default function EarthScene() {
  return (
    <div className="earth-scene-container" aria-hidden="true">
      <Canvas
        camera={{
          position: [1.2, 2.2, 7.8],   // slightly high + right → angled view
          fov: 38,
          near: 0.1,
          far: 2000,
        }}
        dpr={[1, 2]}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance',
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.1,
        }}
        style={{ background: 'transparent' }}
      >
        <AdaptiveDpr pixelated />

        {/* Starfield — deep, subtle */}
        <Stars
          radius={300}
          depth={80}
          count={5500}
          factor={3.5}
          saturation={0.15}
          fade
          speed={0.2}
        />

        <SceneLighting />

        <Suspense fallback={<EarthShell />}>
          <EarthCanvas />
          <SatelliteLayer />
        </Suspense>
      </Canvas>

      {/* Soft radial vignette — darkens the extreme edges */}
      <div className="earth-vignette" />
    </div>
  );
}

