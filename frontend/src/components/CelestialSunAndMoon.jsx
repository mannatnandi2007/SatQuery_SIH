import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * CelestialSunAndMoon — Cinematic 3D Sun and Moon with smooth rising & setting orbital physics.
 * 
 * When toggled to Light mode:
 *   - The 3D Sun rises along an arc from below the horizon to high in the upper-right sky.
 *   - The 3D Moon sets downward below the horizon.
 * When toggled to Dark mode:
 *   - The 3D Sun sets down below the horizon.
 *   - The 3D Moon rises up along an arc into the upper-left cosmic starry sky.
 */
export default function CelestialSunAndMoon({ isLightMode }) {
  const sunGroupRef = useRef();
  const moonGroupRef = useRef();
  const sunCoreRef = useRef();
  const sunCoronaRef = useRef();
  const sunLightRef = useRef();
  const moonLightRef = useRef();
  
  // Continuous transition progress: 0.0 = full night, 1.0 = full day
  const progressRef = useRef(isLightMode ? 1.0 : 0.0);

  useFrame((state, delta) => {
    const target = isLightMode ? 1.0 : 0.0;
    // Smooth cinematic spring/damping (around 1.2s transition)
    progressRef.current = THREE.MathUtils.damp(progressRef.current, target, 3.0, delta);
    const p = progressRef.current;
    const q = 1.0 - p; // Moon progress
    const t = state.clock.getElapsedTime();

    // ── Sun Arc Motion (Rises to upper right, sets below horizon) ──
    if (sunGroupRef.current) {
      const sunX = THREE.MathUtils.lerp(1.2, 3.8, p);
      const sunY = -4.8 + Math.sin(p * Math.PI * 0.5) * 7.4; // Arc from -4.8 to +2.6
      const sunZ = THREE.MathUtils.lerp(-3.0, -0.2, p);
      sunGroupRef.current.position.set(sunX, sunY, sunZ);

      const sunScale = Math.max(0.001, THREE.MathUtils.lerp(0.05, 1.0, p));
      sunGroupRef.current.scale.setScalar(sunScale);

      // Subtle corona pulsation and rotation
      if (sunCoronaRef.current) {
        sunCoronaRef.current.rotation.z = t * 0.15;
        const pulse = 1.0 + Math.sin(t * 2.5) * 0.06;
        sunCoronaRef.current.scale.setScalar(pulse);
      }

      // Dynamic warm sunlight point light
      if (sunLightRef.current) {
        sunLightRef.current.intensity = p * 45.0;
      }
    }

    // ── Moon Arc Motion (Rises to upper left, sets below horizon) ──
    if (moonGroupRef.current) {
      const moonX = THREE.MathUtils.lerp(0.5, -3.2, q);
      const moonY = -4.8 + Math.sin(q * Math.PI * 0.5) * 7.0; // Arc from -4.8 to +2.2
      const moonZ = THREE.MathUtils.lerp(-3.0, -0.4, q);
      moonGroupRef.current.position.set(moonX, moonY, moonZ);

      const moonScale = Math.max(0.001, THREE.MathUtils.lerp(0.05, 1.0, q));
      moonGroupRef.current.scale.setScalar(moonScale);

      // Slow lunar axial rotation
      moonGroupRef.current.rotation.y = t * 0.05;

      // Soft cool moonlight point light
      if (moonLightRef.current) {
        moonLightRef.current.intensity = q * 8.0;
      }
    }
  });

  return (
    <group>
      {/* ═══════════════ 3D SUN ═══════════════ */}
      <group ref={sunGroupRef}>
        {/* Core incandescent solar ball */}
        <mesh ref={sunCoreRef}>
          <sphereGeometry args={[0.38, 32, 32]} />
          <meshBasicMaterial color="#fffbeb" />
        </mesh>

        {/* Inner radiant corona glow */}
        <mesh>
          <sphereGeometry args={[0.52, 32, 32]} />
          <meshBasicMaterial
            color="#fbbf24"
            transparent
            opacity={0.75}
            blending={THREE.AdditiveBlending}
            side={THREE.BackSide}
          />
        </mesh>

        {/* Outer warm amber atmosphere flare */}
        <mesh ref={sunCoronaRef}>
          <sphereGeometry args={[0.78, 32, 32]} />
          <meshBasicMaterial
            color="#ea580c"
            transparent
            opacity={0.4}
            blending={THREE.AdditiveBlending}
            side={THREE.BackSide}
          />
        </mesh>

        {/* Sun Flare billboard cross rings */}
        <mesh rotation={[0, 0, Math.PI / 4]}>
          <ringGeometry args={[0.42, 1.1, 32]} />
          <meshBasicMaterial
            color="#fed7aa"
            transparent
            opacity={0.25}
            blending={THREE.AdditiveBlending}
            side={THREE.DoubleSide}
          />
        </mesh>

        {/* Dynamic Sun Light Source */}
        <pointLight
          ref={sunLightRef}
          color="#fff8ed"
          intensity={35}
          distance={30}
          decay={2}
        />
      </group>

      {/* ═══════════════ 3D MOON ═══════════════ */}
      <group ref={moonGroupRef}>
        {/* Realistic cratered lunar surface */}
        <mesh>
          <sphereGeometry args={[0.26, 32, 32]} />
          <meshStandardMaterial
            color="#e2e8f0"
            roughness={0.9}
            metalness={0.05}
            emissive="#1e293b"
            emissiveIntensity={0.2}
          />
        </mesh>

        {/* Soft lunar luminescence halo */}
        <mesh>
          <sphereGeometry args={[0.36, 32, 32]} />
          <meshBasicMaterial
            color="#93c5fd"
            transparent
            opacity={0.35}
            blending={THREE.AdditiveBlending}
            side={THREE.BackSide}
          />
        </mesh>

        {/* Outer faint moonlight glow */}
        <mesh>
          <sphereGeometry args={[0.54, 32, 32]} />
          <meshBasicMaterial
            color="#60a5fa"
            transparent
            opacity={0.18}
            blending={THREE.AdditiveBlending}
            side={THREE.BackSide}
          />
        </mesh>

        {/* Dynamic Moon Light Source */}
        <pointLight
          ref={moonLightRef}
          color="#93c5fd"
          intensity={6}
          distance={20}
          decay={2}
        />
      </group>
    </group>
  );
}
