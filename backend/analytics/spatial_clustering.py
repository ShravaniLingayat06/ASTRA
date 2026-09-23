"""Spatial clustering using Haversine DBSCAN (refactored & improved from show.py)."""
import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict, Any, Tuple

EARTH_RADIUS_KM = 6371.0088

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    
    a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return EARTH_RADIUS_KM * c

def perform_spatial_clustering(
    coordinates: List[Tuple[float, float]],
    eps_km: float = 0.5,
    min_samples: int = 2
) -> List[int]:
    """
    Cluster lat/lon coordinates using DBSCAN with haversine metric.
    Returns cluster labels (-1 for noise/outliers).
    """
    if not coordinates or len(coordinates) == 0:
        return []
    
    coords_arr = np.array(coordinates)
    if len(coords_arr) < min_samples:
        return [0] * len(coords_arr) if len(coords_arr) > 0 else []

    # Convert coordinates from degrees to radians for haversine metric
    coords_rad = np.radians(coords_arr)
    # eps in radians
    kms_per_radian = EARTH_RADIUS_KM
    epsilon_rad = eps_km / kms_per_radian

    db = DBSCAN(eps=epsilon_rad, min_samples=min_samples, metric='haversine')
    labels = db.fit_predict(coords_rad)
    return labels.tolist()

def compute_cluster_metrics(coords: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Calculate centroid, bounding radius in meters, and spatial concentration score."""
    if not coords:
        return {"centroid": (0.0, 0.0), "radius_meters": 0.0, "spatial_score": 0.0}

    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    center_lat = float(np.mean(lats))
    center_lon = float(np.mean(lons))

    # Calculate max distance from centroid
    max_dist_km = 0.0
    for lat, lon in coords:
        d = haversine_distance_km(center_lat, center_lon, lat, lon)
        if d > max_dist_km:
            max_dist_km = d

    radius_meters = max_dist_km * 1000.0

    # Spatial concentration score: tight clusters (smaller radius, more points) score higher
    # Base density: points / area (km^2)
    area_km2 = max(np.pi * (max_dist_km ** 2), 0.01)
    density = len(coords) / area_km2
    # Normalize density into 0 - 100 score
    spatial_score = min(100.0, float(density * 5.0) + min(len(coords) * 8.0, 40.0))

    return {
        "centroid": (center_lat, center_lon),
        "radius_meters": round(radius_meters, 1),
        "spatial_score": round(spatial_score, 2)
    }
