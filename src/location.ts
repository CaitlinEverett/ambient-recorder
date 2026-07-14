// Coarse location — one fix at session start, region + altitude only.
// NEVER returns raw lat/long: the record is packaged into a shared dataset, so
// only a reverse-geocoded region and an altitude are kept (design decision,
// schema v0.1.1). Altitude contextualizes the barometer; region enables weather
// cross-reference for H1/H3.

import * as Location from 'expo-location';
import { LocationFix } from './schema';

/** Request permission, take one coarse fix, return region + altitude (or null). */
export async function getCoarseLocation(): Promise<LocationFix | null> {
  const perm = await Location.requestForegroundPermissionsAsync();
  if (!perm.granted) return null;

  const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Low });

  let region = 'unknown';
  try {
    const places = await Location.reverseGeocodeAsync({
      latitude: pos.coords.latitude,
      longitude: pos.coords.longitude,
    });
    const p = places[0];
    if (p) {
      region = [p.city, p.region, p.isoCountryCode].filter(Boolean).join(', ') || region;
    }
  } catch {
    // reverse geocode is best-effort; keep "unknown" rather than store coordinates
  }

  const altitudeM = typeof pos.coords.altitude === 'number' ? Math.round(pos.coords.altitude) : null;
  // raw pos.coords (lat/long) is deliberately discarded here.
  return { region, altitudeM, accuracy: 'city' };
}
