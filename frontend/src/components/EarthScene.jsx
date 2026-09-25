/**
 * EarthScene — Cinematic 3D space scene container.
 *
 * Includes:
 *   - EarthCanvas (photorealistic Earth with dynamic day/night terminator)
 *   - CelestialSunAndMoon (animated 3D Sun and Moon that rise and set according to theme)
 *   - SatelliteLayer (satellites orbiting with telemetry callouts)
 *   - Stars (deep space starfield, fades smoothly in day mode)
 *   - Dynamic lighting tracking the celestial positions
 */

import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Stars, AdaptiveDpr } from '@react-three/drei';
import * as THREE from 'three';
import EarthCanvas from './EarthCanvas';
import SatelliteLayer from './SatelliteLayer';
import CelestialSunAndMoon from './CelestialSunAndMoon';

/* ── Dynamic Scene Lighting ─────────────────────────────────────── */
function SceneLighting({ isLightMode }) {
  const ambientRef = useRef();
  const dirLightRef = useRef();
  const fillLightRef = useRef();
  const progressRef = useRef(isLightMode ? 1.0 : 0.0);

  useFrame((state, delta) => {
    const target = isLightMode ? 1.0 : 0.0;
    progressRef.current = THREE.MathUtils.damp(progressRef.current, target, 3.0, delta);
    const p = progressRef.current;

    // Ambient light: soft cosmic fill in night, crisp clean illumination in day
    if (ambientRef.current) {
      ambientRef.current.intensity = THREE.MathUtils.lerp(0.12, 1.25, p);
      ambientRef.current.color.lerpColors(
        new THREE.Color("#0d1a30"),
        new THREE.Color("#ffffff"),
        p
      );
    }

    // Directional sunlight: positions dynamically with the sun arc
    if (dirLightRef.current) {
      const sunX = THREE.MathUtils.lerp(6.0, 4.5, p);
      const sunY = THREE.MathUtils.lerp(2.0, 3.2, p);
      const sunZ = THREE.MathUtils.lerp(4.0, 3.0, p);
      dirLightRef.current.position.set(sunX, sunY, sunZ);
      dirLightRef.current.intensity = THREE.MathUtils.lerp(2.6, 4.4, p);
    }

    // Fill light
    if (fillLightRef.current) {
      fillLightRef.current.intensity = THREE.MathUtils.lerp(0.08, 0.45, p);
    }
  });

  return (
    <>
      <ambientLight ref={ambientRef} intensity={isLightMode ? 1.25 : 0.12} />
      <directionalLight
        ref={dirLightRef}
        position={[7, 5, 5]}
        intensity={isLightMode ? 4.4 : 2.6}
        color="#fffaf0"
      />
      <directionalLight
        ref={fillLightRef}
        position={[-5, -2, -4]}
        intensity={isLightMode ? 0.45 : 0.08}
        color="#fed7aa"
      />
    </>
  );
}

/* ── Starfield with Smooth Day/Night Fade ───────────────────────── */
function Starfield({ isLightMode }) {
  const starsGroupRef = useRef();
  const progressRef = useRef(isLightMode ? 1.0 : 0.0);

  useFrame((state, delta) => {
    const target = isLightMode ? 1.0 : 0.0;
    progressRef.current = THREE.MathUtils.damp(progressRef.current, target, 3.0, delta);
    const p = progressRef.current;

    if (starsGroupRef.current) {
      // Fade stars out in daytime light mode
      const scale = THREE.MathUtils.lerp(1.0, 0.001, p);
      starsGroupRef.current.scale.setScalar(scale);
      starsGroupRef.current.visible = p < 0.95;
    }
  });

  return (
    <group ref={starsGroupRef}>
      <Stars
        radius={300}
        depth={80}
        count={5500}
        factor={3.5}
        saturation={0.15}
        fade
        speed={0.2}
      />
    </group>
  );
}

/* ── Loading placeholder ───────────────────────────────────────── */
function EarthShell({ isLightMode }) {
  return (
    <mesh>
      <sphereGeometry args={[2.0, 24, 24]} />
      <meshBasicMaterial
        color={isLightMode ? "#ea580c" : "#0a1a35"}
        wireframe
        opacity={isLightMode ? 0.25 : 0.18}
        transparent
      />
    </mesh>
  );
}

/* ── EarthScene Component ───────────────────────────────────────── */
export default function EarthScene({ isLightMode = false }) {
  return (
    <div className={`earth-scene-container ${isLightMode ? 'light-earth' : ''}`} aria-hidden="true">
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
          toneMappingExposure: isLightMode ? 1.25 : 1.1,
        }}
        style={{ background: 'transparent' }}
      >
        <AdaptiveDpr pixelated />

        {/* Dynamic Starfield that smoothly fades during day */}
        <Starfield isLightMode={isLightMode} />

        {/* Dynamic lighting */}
        <SceneLighting isLightMode={isLightMode} />

        {/* Animated 3D Sun and Moon */}
        <CelestialSunAndMoon isLightMode={isLightMode} />

        <Suspense fallback={<EarthShell isLightMode={isLightMode} />}>
          <EarthCanvas isLightMode={isLightMode} />
          <SatelliteLayer isLightMode={isLightMode} />
        </Suspense>
      </Canvas>
    </div>
  );
}
