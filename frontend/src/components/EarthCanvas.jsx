/**
 * EarthCanvas — Cinematic photorealistic Earth using real NASA textures.
 *
 * Textures (NASA public domain / three-globe MIT):
 *   /assets/earth/earth-day.jpg      — Blue Marble albedo
 *   /assets/earth/earth-night.jpg    — Black Marble city lights
 *   /assets/earth/earth-clouds.jpg   — cloud combined layer
 *   /assets/earth/earth-bump.png     — elevation normal map
 *
 * Rendering approach:
 *   - Custom GLSL shader for realistic day/night terminator blending
 *   - Specular ocean shimmer
 *   - Atmospheric glow via second larger sphere with additive blending
 *   - Cloud layer on a slightly larger sphere, independent rotation
 *   - Slow continuous axial rotation
 */

import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame, useLoader, useThree } from '@react-three/fiber';
import * as THREE from 'three';

const EARTH_RADIUS = 2.0;
const CLOUD_RADIUS = EARTH_RADIUS * 1.008;
const ATMOS_RADIUS = EARTH_RADIUS * 1.045;

const EARTH_SETTINGS = {
  daylightIntensity: 1.5,
  saturation: 1.4,
  cityLightIntensity: 2.0,
  cityLightColor: new THREE.Color(0xffcc55), // Golden/amber
  atmosphereIntensity: 0.85, // Reduced for a thinner, less overwhelming rim
  cloudOpacity: 0.85       // Brighter clouds
};

/* ── Atmosphere Glow ───────────────────────────────────────────── */
function Atmosphere() {
  const mat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: {
      sunDir: { value: new THREE.Vector3(1, 0.3, 1).normalize() },
      atmosphereColor: { value: new THREE.Color(0x0088ff) }, // Electric blue
      glowIntensity: { value: EARTH_SETTINGS.atmosphereIntensity },
    },
    vertexShader: /* glsl */`
      uniform vec3 sunDir;
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
      varying vec3 vNormal;
      varying vec3 vWorldPos;
      void main() {
        vec3 viewDir  = normalize(cameraPosition - vWorldPos);
        float rim     = 1.0 - abs(dot(viewDir, vNormal));
        rim           = smoothstep(0.0, 1.0, rim);
        // Sharper, thinner falloff for a more elegant rim
        rim           = pow(rim, 4.5);
        
        float sunRim  = max(dot(vNormal, sunDir), 0.0);
        float glow    = rim * (0.2 + sunRim * 2.0) * glowIntensity;
        
        gl_FragColor  = vec4(atmosphereColor * glow, glow * 0.7);
      }
    `,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    transparent: true,
    depthWrite: false,
  }), []);

  useFrame(({ clock }) => {
    if (mat.uniforms) {
      const t = clock.getElapsedTime() * 0.004;
      mat.uniforms.sunDir.value.set(Math.cos(t) * 1.4, 0.3, Math.sin(t) * 1.4).normalize();
    }
  });

  return (
    <mesh>
      {/* Slightly smaller atmosphere radius for a tighter rim */}
      <sphereGeometry args={[EARTH_RADIUS * 1.03, 64, 64]} />
      <primitive object={mat} attach="material" />
    </mesh>
  );
}

/* ── Main Earth Sphere ─────────────────────────────────────────── */
function EarthSphere({ dayTex, nightTex, bumpTex }) {
  const earthRef = useRef();

  const mat = useMemo(() => new THREE.ShaderMaterial({
    uniforms: {
      dayTex:             { value: dayTex },
      nightTex:           { value: nightTex },
      bumpTex:            { value: bumpTex },
      sunDir:             { value: new THREE.Vector3(1, 0.3, 1).normalize() },
      bumpScale:          { value: 0.04 },
      daylightIntensity:  { value: EARTH_SETTINGS.daylightIntensity },
      saturation:         { value: EARTH_SETTINGS.saturation },
      cityLightIntensity: { value: EARTH_SETTINGS.cityLightIntensity },
      cityLightColor:     { value: EARTH_SETTINGS.cityLightColor },
    },
    vertexShader: /* glsl */`
      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vWorldPos;
      void main() {
        vUv      = uv;
        vNormal  = normalize(normalMatrix * normal);
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

      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vWorldPos;

      void main() {
        vec4 day    = texture2D(dayTex,   vUv);
        vec4 night  = texture2D(nightTex, vUv);
        vec4 bump   = texture2D(bumpTex,  vUv);

        // Lighten the texture slightly to prevent oceans from being pure black
        day.rgb = pow(day.rgb, vec3(0.85));

        // Detect oceans (low green compared to red)
        float isOcean = (1.0 - smoothstep(0.06, 0.15, day.g - day.r));
        
        // Boost ocean blue specifically
        day.rgb += isOcean * vec3(0.02, 0.08, 0.18);

        // Saturation adjustment for richer natural colors
        float luminance = dot(day.rgb, vec3(0.299, 0.587, 0.114));
        vec3 satColor = mix(vec3(luminance), day.rgb, saturation);
        day.rgb = satColor * daylightIntensity;

        // Slightly perturb normal with bump
        vec3 n = normalize(vNormal + (bump.rgb - 0.5) * bumpScale);

        // Diffuse lighting
        float NdotL = dot(n, sunDir);
        // Smooth terminator for cinematic day/night transition
        float dayMix = smoothstep(-0.25, 0.25, NdotL);

        // Atmosphere tint on the limb (day side)
        vec3 viewDir = normalize(cameraPosition - vWorldPos);
        float rimDot = 1.0 - max(dot(viewDir, n), 0.0);
        float atmos  = pow(rimDot, 4.0) * dayMix * 0.35;

        // Ocean specular shimmer
        float spec    = pow(max(dot(reflect(-sunDir, n), viewDir), 0.0), 60.0);
        vec3 specCol  = vec3(0.4, 0.6, 0.9) * spec * isOcean * dayMix * 0.8;

        // City lights - warm golden tint
        vec3 cityLights = night.rgb * cityLightColor * cityLightIntensity;
        // Fade city lights out smoothly as they enter daylight
        float nightMix = 1.0 - smoothstep(-0.1, 0.2, NdotL);
        cityLights *= nightMix;

        // Base blend
        vec3 col = mix(vec3(0.0), day.rgb, dayMix);
        
        // Add very dim but visible surface details to the night side (not just pitch black)
        vec3 nightSurface = day.rgb * 0.15;
        col += nightSurface * (1.0 - dayMix);

        // Add city lights to the dark areas
        col += cityLights;
        
        // Add atmospheric electric-blue tint rim and ocean spec
        col += vec3(0.05, 0.3, 0.9) * atmos;
        col += specCol;

        gl_FragColor = vec4(col, 1.0);
      }
    `,
  }), [dayTex, nightTex, bumpTex]);

  useFrame(({ clock }) => {
    if (earthRef.current) {
      earthRef.current.rotation.y = clock.getElapsedTime() * 0.035;
    }
    if (mat.uniforms) {
      const t = clock.getElapsedTime() * 0.004;
      mat.uniforms.sunDir.value.set(Math.cos(t) * 1.4, 0.3, Math.sin(t) * 1.4).normalize();
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
function CloudLayer({ cloudTex }) {
  const cloudRef = useRef();

  const mat = useMemo(() => new THREE.MeshPhongMaterial({
    map: cloudTex,
    transparent: true,
    opacity: 0.42,
    depthWrite: false,
    blending: THREE.NormalBlending,
    side: THREE.FrontSide,
  }), [cloudTex]);

  useFrame(({ clock }) => {
    if (cloudRef.current) {
      // Slightly faster than Earth → clouds drift over surface
      cloudRef.current.rotation.y = clock.getElapsedTime() * 0.042;
    }
  });

  return (
    <mesh ref={cloudRef}>
      <sphereGeometry args={[CLOUD_RADIUS, 64, 64]} />
      <primitive object={mat} attach="material" />
    </mesh>
  );
}

/* ── Earth Group (loads all textures) ──────────────────────────── */
export default function EarthCanvas() {
  const [dayTex, nightTex, cloudTex, bumpTex] = useLoader(THREE.TextureLoader, [
    '/assets/earth/earth-day.jpg',
    '/assets/earth/earth-night.jpg',
    '/assets/earth/earth-clouds.jpg',
    '/assets/earth/earth-bump.png',
  ]);

  // Equirectangular wrapping
  [dayTex, nightTex, cloudTex, bumpTex].forEach(t => {
    if (t) {
      t.wrapS = THREE.RepeatWrapping;
      t.wrapT = THREE.ClampToEdgeWrapping;
      t.colorSpace = THREE.SRGBColorSpace;
    }
  });

  return (
    <group rotation={[0.1, 0, 0]}>  {/* Slight axial tilt */}
      <EarthSphere dayTex={dayTex} nightTex={nightTex} bumpTex={bumpTex} />
      <CloudLayer cloudTex={cloudTex} />
      <Atmosphere />
    </group>
  );
}
