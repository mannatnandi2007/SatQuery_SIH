"""
SatQuery AI — Ground Sampling Distance (GSD) Normalisation Engine
Track A: Madhura & Dipesh

Handles multi-sensor spatial resolution detection, GeoTIFF spatial metadata extraction,
canonical resampling (e.g. Sentinel-2 10m baseline), and physical metric scale calculations.
"""

import os
from io import BytesIO
from typing import Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from PIL import Image, TiffImagePlugin


# Canonical working GSD in meters per pixel (Sentinel-2 visual resolution standard)
CANONICAL_GSD_M = 10.0

# Known satellite sensor resolution baselines (meters per pixel)
SENSOR_GSD_PROFILES = {
    "sentinel-2_10m": {"gsd": 10.0, "sensor": "Sentinel-2 MSI (10m Optical)", "default_crs": "EPSG:4326"},
    "sentinel-2_20m": {"gsd": 20.0, "sensor": "Sentinel-2 MSI (20m RedEdge/SWIR)", "default_crs": "EPSG:4326"},
    "sentinel-2_60m": {"gsd": 60.0, "sensor": "Sentinel-2 MSI (60m Atmospheric)", "default_crs": "EPSG:4326"},
    "landsat_8_9_30m": {"gsd": 30.0, "sensor": "Landsat 8/9 OLI (30m Multispectral)", "default_crs": "EPSG:4326"},
    "landsat_8_9_15m": {"gsd": 15.0, "sensor": "Landsat 8/9 OLI (15m Panchromatic)", "default_crs": "EPSG:4326"},
    "planetscope_3m": {"gsd": 3.0, "sensor": "PlanetScope DOVE (3m High-Res)", "default_crs": "EPSG:4326"},
    "aerial_worldview_05m": {"gsd": 0.5, "sensor": "WorldView / Aerial (0.5m Very High Res)", "default_crs": "EPSG:4326"},
    "drone_uav_01m": {"gsd": 0.1, "sensor": "UAV / Drone (<0.1m Ultra High Res)", "default_crs": "EPSG:4326"},
}


@dataclass
class GSDMetadata:
    """Structured spatial resolution and metadata descriptor for an image."""
    detected_gsd_m: float
    sensor_family: str
    crs: str
    width: int
    height: int
    is_geotiff: bool
    scale_factor_to_canonical: float
    normalization_applied: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GSDNormalizer:
    """
    Engine for extracting, standardizing, and arbitrating Ground Sampling Distance (GSD)
    across diverse satellite, aerial, and drone sensors.
    """

    def __init__(self, canonical_gsd: float = CANONICAL_GSD_M):
        self.canonical_gsd = canonical_gsd

    def extract_geotiff_pixel_scale(self, img: Image.Image) -> Optional[float]:
        """
        Extract ModelPixelScaleTag (Tag 33550) from GeoTIFF headers if present.
        ModelPixelScaleTag = (ScaleX, ScaleY, ScaleZ) in ground units (meters or degrees).
        """
        try:
            if hasattr(img, "tag_v2") and img.tag_v2:
                # Tag 33550 = ModelPixelScaleTag
                scale_tag = img.tag_v2.get(33550)
                if scale_tag and len(scale_tag) >= 2:
                    scale_x, scale_y = float(scale_tag[0]), float(scale_tag[1])
                    # If scale is in approximate geographic degrees, convert to meters at equator
                    if scale_x < 0.01:
                        # ~111,320 meters per degree
                        scale_m = ((scale_x + scale_y) / 2.0) * 111320.0
                    else:
                        scale_m = (scale_x + scale_y) / 2.0
                    if 0.01 <= scale_m <= 1000.0:
                        return round(scale_m, 2)
        except Exception:
            pass
        return None

    def infer_sensor_from_filename(self, filename: str) -> Tuple[float, str]:
        """Infer sensor profile and approximate GSD based on file naming conventions."""
        fname = filename.lower()
        if any(k in fname for k in ["s2", "sentinel-2", "sentinel2"]):
            if any(b in fname for b in ["b01", "b09", "b10", "60m"]):
                return SENSOR_GSD_PROFILES["sentinel-2_60m"]["gsd"], SENSOR_GSD_PROFILES["sentinel-2_60m"]["sensor"]
            if any(b in fname for b in ["b05", "b06", "b07", "b8a", "b11", "b12", "20m"]):
                return SENSOR_GSD_PROFILES["sentinel-2_20m"]["gsd"], SENSOR_GSD_PROFILES["sentinel-2_20m"]["sensor"]
            return SENSOR_GSD_PROFILES["sentinel-2_10m"]["gsd"], SENSOR_GSD_PROFILES["sentinel-2_10m"]["sensor"]

        if any(k in fname for k in ["lc08", "lc09", "landsat"]):
            if "b8" in fname or "pan" in fname:
                return SENSOR_GSD_PROFILES["landsat_8_9_15m"]["gsd"], SENSOR_GSD_PROFILES["landsat_8_9_15m"]["sensor"]
            return SENSOR_GSD_PROFILES["landsat_8_9_30m"]["gsd"], SENSOR_GSD_PROFILES["landsat_8_9_30m"]["sensor"]

        if any(k in fname for k in ["planet", "dove", "planetscope"]):
            return SENSOR_GSD_PROFILES["planetscope_3m"]["gsd"], SENSOR_GSD_PROFILES["planetscope_3m"]["sensor"]

        if any(k in fname for k in ["worldview", "wv", "aerial", "naip", "highres", "airport", "port"]):
            return SENSOR_GSD_PROFILES["aerial_worldview_05m"]["gsd"], SENSOR_GSD_PROFILES["aerial_worldview_05m"]["sensor"]

        if any(k in fname for k in ["drone", "uav"]):
            return SENSOR_GSD_PROFILES["drone_uav_01m"]["gsd"], SENSOR_GSD_PROFILES["drone_uav_01m"]["sensor"]

        # Default fallback: Sentinel-2 10m Optical standard
        return CANONICAL_GSD_M, "Standard Optical Scene (Estimated ~10m GSD)"

    def detect_gsd(self, image_input: Union[bytes, Image.Image], filename: str = "") -> GSDMetadata:
        """
        Full detection routine: extracts GeoTIFF tags, infers filename metadata,
        and computes resolution scale factor against the canonical baseline.
        """
        is_bytes = isinstance(image_input, bytes)
        img = Image.open(BytesIO(image_input)) if is_bytes else image_input

        w, h = img.size
        is_geotiff = False
        crs = "EPSG:4326 (WGS84)"
        detected_gsd = None
        sensor_name = ""

        # Step 1: Check GeoTIFF embedded tags
        if isinstance(img, TiffImagePlugin.TiffImageFile):
            is_geotiff = True
            detected_gsd = self.extract_geotiff_pixel_scale(img)
            if detected_gsd:
                sensor_name = f"GeoTIFF Raster ({detected_gsd}m/px calibrated)"

        # Step 2: Fallback to filename inference or sensor profile
        if detected_gsd is None:
            detected_gsd, sensor_name = self.infer_sensor_from_filename(filename)

        scale_factor = detected_gsd / self.canonical_gsd
        norm_method = "identity" if abs(scale_factor - 1.0) < 0.05 else (
            "anti_aliased_downsample" if scale_factor < 1.0 else "bicubic_upsample"
        )

        return GSDMetadata(
            detected_gsd_m=float(detected_gsd),
            sensor_family=sensor_name,
            crs=crs,
            width=w,
            height=h,
            is_geotiff=is_geotiff,
            scale_factor_to_canonical=round(scale_factor, 4),
            normalization_applied=norm_method
        )

    def resample_to_canonical(
        self,
        image: Image.Image,
        source_gsd: float,
        target_gsd: Optional[float] = None
    ) -> Tuple[Image.Image, float]:
        """
        Resamples an image so its physical resolution matches the canonical target resolution.
        Scale factor = source_gsd / target_gsd.
        Uses anti-aliased Lanczos resampling for downsampling and bicubic for upsampling.
        """
        target = target_gsd or self.canonical_gsd
        if abs(source_gsd - target) < 0.05:
            return image.copy(), 1.0

        scale = source_gsd / target
        new_w = max(16, int(round(image.width * scale)))
        new_h = max(16, int(round(image.height * scale)))

        # Use Lanczos for decimation (downsampling high-res to avoid moire patterns)
        resample_filter = Image.Resampling.LANCZOS if scale < 1.0 else Image.Resampling.BICUBIC
        resampled_img = image.resize((new_w, new_h), resample=resample_filter)
        return resampled_img, scale

    def compute_metric_dimensions(
        self,
        box_norm: Tuple[float, float, float, float],
        img_w: int,
        img_h: int,
        gsd_m: float
    ) -> Dict[str, Any]:
        """
        Given normalized bounding box [ymin, xmin, ymax, xmax] in percentages (0-100) or (0-1000),
        computes real-world physical metric width (meters), length (meters), and area (m² / km²).
        """
        ymin, xmin, ymax, xmax = box_norm
        # Standardize to 0.0 - 1.0
        if ymax > 100.0 or xmax > 100.0:
            ymin, xmin, ymax, xmax = ymin / 1000.0, xmin / 1000.0, ymax / 1000.0, xmax / 1000.0
        elif ymax > 1.0 or xmax > 1.0:
            ymin, xmin, ymax, xmax = ymin / 100.0, xmin / 100.0, ymax / 100.0, xmax / 100.0

        pixel_w = (xmax - xmin) * img_w
        pixel_h = (ymax - ymin) * img_h

        physical_w_m = round(pixel_w * gsd_m, 1)
        physical_h_m = round(pixel_h * gsd_m, 1)
        area_m2 = round(physical_w_m * physical_h_m, 1)
        area_km2 = round(area_m2 / 1_000_000.0, 4)

        return {
            "physical_width_m": physical_w_m,
            "physical_height_m": physical_h_m,
            "area_m2": area_m2,
            "area_km2": area_km2,
            "gsd_m_per_px": gsd_m
        }

    def generate_scale_bar(self, img_w: int, gsd_m: float) -> Dict[str, Any]:
        """
        Calculates an aesthetically pleasing calibrated metric scale bar
        for rendering in the corner of a satellite evidence overlay.
        """
        total_ground_width_m = img_w * gsd_m

        # Candidate nice metric lengths
        candidate_lengths_m = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
        # Target scale bar taking up roughly 15% to 25% of image width
        target_m = total_ground_width_m * 0.20

        chosen_length_m = min(candidate_lengths_m, key=lambda x: abs(x - target_m))
        pixel_length = int(round(chosen_length_m / gsd_m))

        label = f"{chosen_length_m} m" if chosen_length_m < 1000 else f"{chosen_length_m / 1000.0:.1f} km"

        return {
            "bar_length_m": chosen_length_m,
            "bar_length_px": pixel_length,
            "label": label,
            "gsd_m_per_px": gsd_m
        }


# Singleton instance for quick module access
gsd_normalizer = GSDNormalizer()
