const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export async function getFarms() {
  return request('/farms');
}

export async function createFarm(payload) {
  return request('/farms', { method: 'POST', body: JSON.stringify(payload) });
}

export async function getPaddocks(farmId) {
  return request(`/farms/${farmId}/paddocks`);
}

export async function importPaddocks(farmId, featureCollection) {
  return request(`/farms/${farmId}/paddocks/import`, {
    method: 'POST',
    body: JSON.stringify({ feature_collection: featureCollection }),
  });
}

export async function getObservationDates(farmId) {
  return request(`/farms/${farmId}/observations/dates`);
}

export async function getObservationsByDate(farmId, date) {
  return request(`/farms/${farmId}/observations?date=${date}`);
}

export async function getPaddockSeries(paddockId) {
  return request(`/paddocks/${paddockId}/observations`);
}

export async function getWeather(farmId) {
  return request(`/farms/${farmId}/weather/forecast`);
}

export async function triggerIngest(farmId) {
  return request(`/farms/${farmId}/jobs/ingest`, { method: 'POST' });
}

export async function getLatestRecommendation(farmId) {
  return request(`/farms/${farmId}/recommendations/latest`);
}

export async function generateRecommendation(farmId) {
  return request(`/farms/${farmId}/recommendations/generate`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}
