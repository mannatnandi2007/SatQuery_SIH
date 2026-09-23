/**
 * SatelliteLayer — Cinematic 3D satellites orbiting Earth.
 *
 * Design goals (Dribbble reference DNA):
 * - Recognizable satellite silhouettes: main bus + extended solar panels + antenna
 * - Metallic dark-grey/anthracite materials with subtle blue panel tint
 * - Multiple inclined orbital planes (not all equatorial)
 * - Satellites move behind the Earth naturally via renderOrder
 * - Orbital path lines are subtle, semi-transparent, slightly glowing
 * - Smooth continuous motion, different speeds per orbit
 */

import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

/* ── Reusable Glow Texture ─────────────────────────────────────── */
const glowTexture = (function() {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;
  const ctx = canvas.getContext('2d');
  const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
  grad.addColorStop(0.2, 'rgba(255, 220, 180, 0.8)');
  grad.addColorStop(0.5, 'rgba(255, 150, 50, 0.3)');
  grad.addColorStop(1, 'rgba(255, 150, 50, 0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(canvas);
})();

/* ── Satellite body geometry ───────────────────────────────────── */
function SatelliteModel({ scale = 1, panelAngle = 0, colorType = 'cool' }) {
  const isWarm = colorType === 'warm';
  
  const panelColor = isWarm ? "#ffdd88" : "#aaddff";
  const panelEmissive = isWarm ? "#ff8822" : "#0088ff";
  const lightColor = isWarm ? "#ff9933" : "#33bbff";

  return (
    <group scale={scale}>
      {/* ─── Main bus ─── */}
      <mesh castShadow>
        <boxGeometry args={[0.10, 0.065, 0.065]} />
        <meshStandardMaterial
          color="#3a404c"
          metalness={0.9}
          roughness={0.15}
          emissive="#1a2030"
          emissiveIntensity={0.4}
        />
      </mesh>

      {/* Bus detail panel — front face */}
      <mesh position={[0.051, 0, 0]}>
        <planeGeometry args={[0.065, 0.065]} />
        <meshStandardMaterial color="#ffffff" emissive={panelEmissive} emissiveIntensity={1.2} />
      </mesh>

      {/* ─── Solar panel arms ─── */}
      {/* Left arm */}
      <mesh position={[-0.145, 0, 0]} rotation={[panelAngle, 0, 0]}>
        <boxGeometry args={[0.21, 0.0015, 0.082]} />
        <meshStandardMaterial color="#102040" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* Left panel cells grid — dynamic emissive tint */}
      <mesh position={[-0.145, 0.001, 0]} rotation={[panelAngle, 0, 0]}>
        <planeGeometry args={[0.21, 0.082]} />
        <meshStandardMaterial
          color={panelColor}
          metalness={0.6}
          roughness={0.2}
          emissive={panelEmissive}
          emissiveIntensity={0.8}
          side={THREE.FrontSide}
        />
      </mesh>

      {/* Right arm */}
      <mesh position={[0.145, 0, 0]} rotation={[panelAngle, 0, 0]}>
        <boxGeometry args={[0.21, 0.0015, 0.082]} />
        <meshStandardMaterial color="#102040" metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[0.145, 0.001, 0]} rotation={[panelAngle, 0, 0]}>
        <planeGeometry args={[0.21, 0.082]} />
        <meshStandardMaterial
          color={panelColor}
          metalness={0.6}
          roughness={0.2}
          emissive={panelEmissive}
          emissiveIntensity={0.8}
          side={THREE.FrontSide}
        />
      </mesh>

      {/* ─── Antenna dish ─── */}
      <mesh position={[0, 0.062, -0.01]} rotation={[Math.PI / 6, 0, 0]}>
        <cylinderGeometry args={[0.032, 0.032, 0.003, 16]} />
        <meshStandardMaterial color="#ffffff" metalness={0.9} roughness={0.1} emissive="#4466aa" emissiveIntensity={0.4} />
      </mesh>
      {/* Antenna strut */}
      <mesh position={[0, 0.042, 0]}>
        <cylinderGeometry args={[0.003, 0.003, 0.04, 6]} />
        <meshStandardMaterial color="#aaaaaa" metalness={0.8} roughness={0.2} />
      </mesh>

      {/* ─── Status light & bloom halo ─── */}
      <pointLight color={lightColor} intensity={2.5} distance={1.2} decay={2} />
      
      {/* Glow billboard for cinematic halo */}
      <sprite scale={[0.5, 0.5, 1]}>
        <spriteMaterial 
          color={lightColor}
          transparent 
          opacity={isWarm ? 0.9 : 0.7} 
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          map={glowTexture} 
        />
      </sprite>
    </group>
  );
}

/* ── Orbital path line (extremely subtle) ──────────────────────── */
function OrbitalPath({ semiMajor, semiMinor, inclination, raan }) {
  const points = useMemo(() => {
    const pts = [];
    const n = 128;
    for (let i = 0; i <= n; i++) {
      const θ = (i / n) * Math.PI * 2;
      pts.push(new THREE.Vector3(
        Math.cos(θ) * semiMajor,
        0,
        Math.sin(θ) * semiMinor
      ));
    }
    return pts;
  }, [semiMajor, semiMinor]);

  const geo = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);

  const euler = useMemo(() => new THREE.Euler(inclination, raan, 0, 'YXZ'), [inclination, raan]);

  return (
    <group rotation={euler}>
      <line geometry={geo}>
        <lineBasicMaterial
          color="#224466"
          transparent
          opacity={0.04}
          blending={THREE.AdditiveBlending}
        />
      </line>
    </group>
  );
}

/* ── Fading Glowing Trail ────────────────────────────────────────── */
function FadingTrail({ semiMajor, semiMinor, inclination, raan, speed, phase, colorType }) {
  const lineRef = useRef();

  const trailColor = colorType === 'warm' 
    ? new THREE.Color(0xff6611) 
    : new THREE.Color(0x00bbff);

  const { geometry, material } = useMemo(() => {
    const pts = [];
    const thetas = [];
    const n = 256;
    for (let i = 0; i <= n; i++) {
      const theta = (i / n) * Math.PI * 2;
      pts.push(new THREE.Vector3(
        Math.cos(theta) * semiMajor,
        0,
        Math.sin(theta) * semiMinor
      ));
      thetas.push(theta);
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    geo.setAttribute('theta', new THREE.Float32BufferAttribute(thetas, 1));

    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uAngle: { value: 0 },
        uColor: { value: trailColor },
      },
      vertexShader: /* glsl */`
        attribute float theta;
        varying float vTheta;
        void main() {
          vTheta = theta;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */`
        uniform float uAngle;
        uniform vec3 uColor;
        varying float vTheta;
        void main() {
          // Calculate angular distance behind satellite
          float diff = mod(uAngle - vTheta, 6.283185307);
          
          // Fading length (roughly 75 degrees)
          float trailLength = 1.3; 
          float alpha = 1.0 - (diff / trailLength);
          alpha = max(0.0, alpha);
          
          // Core brightness
          float core = pow(alpha, 2.5);
          vec3 finalColor = mix(uColor, vec3(1.0, 0.9, 0.8), core * 0.7);
          
          gl_FragColor = vec4(finalColor, alpha * 0.75);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });

    return { geometry: geo, material: mat };
  }, [semiMajor, semiMinor]);

  const euler = useMemo(() => new THREE.Euler(inclination, raan, 0, 'YXZ'), [inclination, raan]);

  useFrame(({ clock }) => {
    if (lineRef.current) {
      const t = clock.getElapsedTime() * speed + phase;
      let angle = t % (Math.PI * 2);
      if (angle < 0) angle += Math.PI * 2;
      lineRef.current.material.uniforms.uAngle.value = angle;
    }
  });

  return (
    <group rotation={euler}>
      <line ref={lineRef} geometry={geometry} material={material} />
    </group>
  );
}

/* ── Single orbiting satellite ─────────────────────────────────── */
function OrbitingSatellite({ semiMajor, semiMinor, inclination, raan, speed, phase, satScale, panelAngle, colorType, label }) {
  const groupRef  = useRef();
  const satRef    = useRef();

  const euler = useMemo(() =>
    new THREE.Euler(inclination, raan, 0, 'YXZ'), [inclination, raan]);

  useFrame(({ clock }) => {
    if (!groupRef.current || !satRef.current) return;

    const t = clock.getElapsedTime() * speed + phase;

    // Position on ellipse in orbital plane
    const lx = Math.cos(t) * semiMajor;
    const lz = Math.sin(t) * semiMinor;

    // Rotate from orbital plane to world space
    const pos = new THREE.Vector3(lx, 0, lz).applyEuler(euler);
    groupRef.current.position.copy(pos);

    // Orient: up = radial outward, forward = prograde (tangential)
    const radial = pos.clone().normalize();
    const tangX  = -Math.sin(t) * semiMajor;
    const tangZ  =  Math.cos(t) * semiMinor;
    const tangent = new THREE.Vector3(tangX, 0, tangZ).applyEuler(euler).normalize();
    const cross   = new THREE.Vector3().crossVectors(radial, tangent).normalize();

    groupRef.current.quaternion.setFromRotationMatrix(
      new THREE.Matrix4().makeBasis(tangent, radial, cross)
    );

    // Slow panel flutter
    satRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.18 + phase) * 0.06;
  });

  return (
    <group ref={groupRef}>
      <group ref={satRef}>
        <SatelliteModel scale={satScale} panelAngle={panelAngle} colorType={colorType} />
      </group>
      {label && (
        <Html
          position={[0, 0.35, 0]}
          center
          distanceFactor={14}
          style={{ pointerEvents: 'none' }}
        >
          <div className="sat-orbit-tag">
            <span
              className="sat-orbit-tag-dot"
              style={{ background: colorType === 'warm' ? '#ff9933' : '#33bbff' }}
            />
            <span className="sat-orbit-tag-text">{label}</span>
          </div>
        </Html>
      )}
    </group>
  );
}

/* ── Satellite configuration ───────────────────────────────────── */
const SATS = [
  // Low, steeply inclined — polar-ish (Hero warm satellite)
  {
    label: 'Self-Adapting',
    semiMajor: 2.72,
    semiMinor: 2.68,
    inclination: 1.38,   // ~79°
    raan: 0.0,
    speed: 0.20,
    phase: 0.0,
    satScale: 1.45,      // Increased size
    panelAngle: 0.05,
    colorType: 'warm',
  },
  // Medium, equatorial-ish (slight inclination)
  {
    label: 'JEV-Like Decision Layer',
    semiMajor: 3.05,
    semiMinor: 2.95,
    inclination: 0.28,   // ~16°
    raan: Math.PI * 0.6,
    speed: 0.14,
    phase: Math.PI * 0.75,
    satScale: 1.15,      // Increased size
    panelAngle: -0.04,
    colorType: 'cool',
  },
  // Higher, retrograde-ish
  {
    label: 'JEPA Architecture',
    semiMajor: 3.4,
    semiMinor: 3.25,
    inclination: 2.1,    // ~120°
    raan: Math.PI * 1.2,
    speed: 0.10,
    phase: Math.PI * 1.4,
    satScale: 1.5,       // Increased size
    panelAngle: 0.08,
    colorType: 'cool',
  },
  // Small, sun-sync-ish
  {
    label: 'GSD Normalization',
    semiMajor: 2.55,
    semiMinor: 2.50,
    inclination: 1.6,    // ~92°
    raan: Math.PI * 0.35,
    speed: 0.26,
    phase: Math.PI * 0.3,
    satScale: 1.0,       // Increased size
    panelAngle: 0.02,
    colorType: 'cool',
  },
];

/* ── Export ────────────────────────────────────────────────────── */
export default function SatelliteLayer() {
  return (
    <group>
      {/* Orbital paths and Fading Trails */}
      {SATS.map((s, i) => (
        <React.Fragment key={`path-${i}`}>
          <OrbitalPath
            semiMajor={s.semiMajor}
            semiMinor={s.semiMinor}
            inclination={s.inclination}
            raan={s.raan}
          />
          <FadingTrail
            semiMajor={s.semiMajor}
            semiMinor={s.semiMinor}
            inclination={s.inclination}
            raan={s.raan}
            speed={s.speed}
            phase={s.phase}
            colorType={s.colorType}
          />
        </React.Fragment>
      ))}

      {/* Satellites */}
      {SATS.map((s, i) => (
        <OrbitingSatellite key={`sat-${i}`} {...s} />
      ))}
    </group>
  );
}
