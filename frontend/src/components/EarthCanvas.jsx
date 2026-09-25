/**
 * EarthCanvas — Cinematic photorealistic Earth using real NASA textures.
 *
 * Textures (NASA public domain / three-globe MIT):
 *   /assets/earth/earth-day.jpg      — Blue Marble albedo
 *   /assets/earth/earth-night.jpg    — Black Marble city lights
 *   /assets/earth/earth-clouds.jpg   — cloud combined layer
 *   /assets/earth/earth-bump.png     — elevation normal map
 *
 * Fully reactive to Day (Light Mode) / Night (Dark Mode) transitions:
 *   - Smooth 3D animation flow as the sun rises/sets
 *   - In Day Mode: Whole visible globe is bathed in clear daylight, vibrant blue oceans,
 *     lush continents, bright white clouds, and warm aerospace atmosphere rim.
 *   - In Night Mode: Cinematic terminator with glowing golden city lights and deep space rim.
 */

import React, { useRef, useMemo } from 'react';
import { useFrame, useLoader } from '@react-three/fiber';
import * as THREE from 'three';

const EARTH_RADIUS = 2.0;
const CLOUD_RADIUS = EARTH_RADIUS * 1.008;

const EARTH_SETTINGS = {
  daylightIntensity: 1.5,
  saturation: 1.35,
  cityLightIntensity: 2.2,
  cityLightColor: new THREE.Color(0xffcc55), // Warm golden city lights
};

/* ── Atmosphere Glow ───────────────────────────────────────────── */
function Atmosphere({ isLightMode = false }) {
  const matRef = useRef();
  const progressRef = useRef(isLightMode ? 1.0 : 0.0);

  const mat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: {
      sunDir: { value: new THREE.Vector3(1, 0.3, 1).normalize() },
      atmosphereColor: { value: new THREE.Color(isLightMode ? 0x38bdf8 : 0x0088ff) },
      glowIntensity: { value: 0.95 },
      modeProgress: { value: isLightMode ? 1.0 : 0.0 },
    },
    vertexShader: /* glsl */`
      varying vec3 vNormal;
      varying vec3 vWorldPos;
      void main() {
        vNormal   = normalize(normalMatrix * normal);
        vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */`
      uniform vec3 sunDir;
      uniform vec3 atmosphereColor;
      uniform float glowIntensity;
      uniform float modeProgress;
      varying vec3 vNormal;
      varying vec3 vWorldPos;

      void main() {
        vec3 viewDir  = normalize(cameraPosition - vWorldPos);
        float rim     = 1.0 - abs(dot(viewDir, vNormal));
        rim           = smoothstep(0.0, 1.0, rim);
        rim           = pow(rim, 4.2);
        
        float sunRim  = max(dot(vNormal, sunDir), 0.0);
        float glow    = rim * (0.2 + sunRim * 2.2) * glowIntensity;
        
        // Blend between deep cosmic blue (night) and warm golden-cyan aerospace (day)
        vec3 nightColor = vec3(0.0, 0.55, 1.0);
        vec3 dayColor   = vec3(0.3, 0.75, 1.0);
        vec3 currentAtmos = mix(nightColor, dayColor, modeProgress);

        gl_FragColor  = vec4(currentAtmos * glow, glow * 0.75);
      }
    `,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    transparent: true,
    depthWrite: false,
  }), []);

  matRef.current = mat;

  useFrame((state, delta) => {
    const target = isLightMode ? 1.0 : 0.0;
    progressRef.current = THREE.MathUtils.damp(progressRef.current, target, 3.0, delta);
    const p = progressRef.current;

    if (matRef.current) {
      matRef.current.uniforms.modeProgress.value = p;
      matRef.current.uniforms.glowIntensity.value = THREE.MathUtils.lerp(0.9, 1.25, p);

      const t = state.clock.getElapsedTime() * 0.005;
      const nightSun = new THREE.Vector3(Math.cos(t) * 1.4, 0.3, Math.sin(t) * 1.4).normalize();
      const daySun = new THREE.Vector3(2.6, 1.8, 2.2).normalize();
      matRef.current.uniforms.sunDir.value.copy(nightSun).lerp(daySun, p).normalize();
    }
  });

  return (
    <mesh>
      <sphereGeometry args={[EARTH_RADIUS * 1.03, 64, 64]} />
      <primitive object={mat} attach="material" />
    </mesh>
  );
}

/* ── Main Earth Sphere ─────────────────────────────────────────── */
function EarthSphere({ dayTex, nightTex, bumpTex, isLightMode = false }) {
  const earthRef = useRef();
  const progressRef = useRef(isLightMode ? 1.0 : 0.0);

  const mat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: {
      dayTex:             { value: dayTex },
      nightTex:           { value: nightTex },
      bumpTex:            { value: bumpTex },
      sunDir:             { value: new THREE.Vector3(1, 0.3, 1).normalize() },
      bumpScale:          { value: 0.035 },
      daylightIntensity:  { value: 1.5 },
      saturation:         { value: EARTH_SETTINGS.saturation },
      cityLightIntensity: { value: EARTH_SETTINGS.cityLightIntensity },
      cityLightColor:     { value: EARTH_SETTINGS.cityLightColor },
      modeProgress:       { value: isLightMode ? 1.0 : 0.0 },
    },
    vertexShader: /* glsl */`
      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vWorldPos;
      void main() {
        vUv       = uv;
        vNormal   = normalize(normalMatrix * normal);
        vWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */`
      uniform sampler2D dayTex;
      uniform sampler2D nightTex;
      uniform sampler2D bumpTex;
      uniform vec3 sunDir;
      uniform float bumpScale;
      
      uniform float daylightIntensity;
      uniform float saturation;
      uniform float cityLightIntensity;
      uniform vec3 cityLightColor;
      uniform float modeProgress;

      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vWorldPos;

      void main() {
        vec4 day    = texture2D(dayTex,   vUv);
        vec4 night  = texture2D(nightTex, vUv);
        vec4 bump   = texture2D(bumpTex,  vUv);

        // Lighten slightly to prevent oceans from being pure dark
        day.rgb = pow(day.rgb, vec3(0.86));

        // Detect oceans (low green compared to red)
        float isOcean = (1.0 - smoothstep(0.06, 0.15, day.g - day.r));
        day.rgb += isOcean * vec3(0.02, 0.08, 0.18);

        // Natural color saturation adjustment
        float luminance = dot(day.rgb, vec3(0.299, 0.587, 0.114));
        vec3 satColor = mix(vec3(luminance), day.rgb, saturation);
        day.rgb = satColor * daylightIntensity;

        // Normal mapping with bump
        vec3 n = normalize(vNormal + (bump.rgb - 0.5) * bumpScale);

        // Diffuse lighting
        float NdotL = dot(n, sunDir);
        float nightTerminator = smoothstep(-0.25, 0.25, NdotL);
        // In light mode, daylight softly fills the entire visible globe (no pitch black night)
        float dayMix = mix(nightTerminator, max(0.55, nightTerminator), modeProgress);

        // Atmosphere tint on the limb
        vec3 viewDir = normalize(cameraPosition - vWorldPos);
        float rimDot = 1.0 - max(dot(viewDir, n), 0.0);
        float atmos  = pow(rimDot, 3.8) * mix(dayMix, 1.0, modeProgress * 0.5) * 0.45;

        // Ocean specular glint
        float spec    = pow(max(dot(reflect(-sunDir, n), viewDir), 0.0), 50.0);
        vec3 specTint = mix(vec3(0.4, 0.6, 0.9), vec3(1.0, 0.88, 0.65), modeProgress);
        vec3 specCol  = specTint * spec * isOcean * dayMix * 1.1;

        // City lights - smoothly fade out in light mode
        vec3 cityLights = night.rgb * cityLightColor * cityLightIntensity * (1.0 - modeProgress);
        float nightMix  = 1.0 - smoothstep(-0.1, 0.2, NdotL);
        cityLights *= nightMix;

        // Base surface blend
        vec3 col = mix(vec3(0.0), day.rgb, dayMix);
        
        // Night side surface illumination:
        // In dark mode: very dim ambient (0.12).
        // In light mode: diffuse daylight skylight (0.85) so the whole globe is visible and beautiful.
        vec3 nightSurface = day.rgb * mix(0.12, 0.85, modeProgress);
        col += nightSurface * (1.0 - dayMix);

        // Add city lights (only active in dark night mode)
        col += cityLights;
        
        // Atmosphere rim tint
        vec3 darkAtmos  = vec3(0.05, 0.35, 0.95);
        vec3 lightAtmos = vec3(0.25, 0.65, 0.98);
        vec3 atmosColor = mix(darkAtmos, lightAtmos, modeProgress);
        col += atmosColor * atmos;
        col += specCol;

        gl_FragColor = vec4(col, 1.0);
      }
    `,
  }), [dayTex, nightTex, bumpTex]);

  useFrame((state, delta) => {
    if (earthRef.current) {
      earthRef.current.rotation.y = state.clock.getElapsedTime() * 0.035;
    }

    const target = isLightMode ? 1.0 : 0.0;
    progressRef.current = THREE.MathUtils.damp(progressRef.current, target, 3.0, delta);
    const p = progressRef.current;

    if (mat.uniforms) {
      mat.uniforms.modeProgress.value = p;
      mat.uniforms.daylightIntensity.value = THREE.MathUtils.lerp(1.5, 2.3, p);
      mat.uniforms.cityLightIntensity.value = THREE.MathUtils.lerp(2.2, 0.0, p);

      const t = state.clock.getElapsedTime() * 0.005;
      const nightSun = new THREE.Vector3(Math.cos(t) * 1.4, 0.3, Math.sin(t) * 1.4).normalize();
      const daySun = new THREE.Vector3(2.6, 1.8, 2.2).normalize();
      mat.uniforms.sunDir.value.copy(nightSun).lerp(daySun, p).normalize();
    }
  });

  return (
    <mesh ref={earthRef} castShadow>
      <sphereGeometry args={[EARTH_RADIUS, 128, 128]} />
      <primitive object={mat} attach="material" />
    </mesh>
  );
}

/* ── Cloud Layer ───────────────────────────────────────────────── */
function CloudLayer({ cloudTex, isLightMode = false }) {
  const cloudRef = useRef();
  const progressRef = useRef(isLightMode ? 1.0 : 0.0);

  const mat = useMemo(() => new THREE.MeshPhongMaterial({
    map: cloudTex,
    transparent: true,
    opacity: 0.45,
    depthWrite: false,
    blending: THREE.NormalBlending,
    side: THREE.FrontSide,
  }), [cloudTex]);

  useFrame((state, delta) => {
    if (cloudRef.current) {
      // Slightly faster than Earth rotation → clouds drift smoothly
      cloudRef.current.rotation.y = state.clock.getElapsedTime() * 0.042;
    }

    const target = isLightMode ? 1.0 : 0.0;
    progressRef.current = THREE.MathUtils.damp(progressRef.current, target, 3.0, delta);
    const p = progressRef.current;
    // Brighter and more visible clouds in light mode
    mat.opacity = THREE.MathUtils.lerp(0.42, 0.62, p);
  });

  return (
    <mesh ref={cloudRef}>
      <sphereGeometry args={[CLOUD_RADIUS, 64, 64]} />
      <primitive object={mat} attach="material" />
    </mesh>
  );
}

/* ── Earth Group (loads all textures) ──────────────────────────── */
export default function EarthCanvas({ isLightMode = false }) {
  const [dayTex, nightTex, cloudTex, bumpTex] = useLoader(THREE.TextureLoader, [
    '/assets/earth/earth-day.jpg',
    '/assets/earth/earth-night.jpg',
    '/assets/earth/earth-clouds.jpg',
    '/assets/earth/earth-bump.png',
  ]);

  // Equirectangular wrapping setup
  [dayTex, nightTex, cloudTex, bumpTex].forEach(t => {
    if (t) {
      t.wrapS = THREE.RepeatWrapping;
      t.wrapT = THREE.ClampToEdgeWrapping;
      t.colorSpace = THREE.SRGBColorSpace;
    }
  });

  return (
    <group rotation={[0.1, 0, 0]}>  {/* Real Earth axial tilt */}
      <EarthSphere dayTex={dayTex} nightTex={nightTex} bumpTex={bumpTex} isLightMode={isLightMode} />
      <CloudLayer cloudTex={cloudTex} isLightMode={isLightMode} />
      <Atmosphere isLightMode={isLightMode} />
    </group>
  );
}
