import { useState } from 'react';

import { createFarm, getFarms, importPaddocks } from '../api/client';

const SAMPLE_FEATURE_COLLECTION = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { name: 'Imported Demo Paddock' },
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [174.759, -36.853],
            [174.761, -36.853],
            [174.761, -36.851],
            [174.759, -36.851],
            [174.759, -36.853],
          ],
        ],
      },
    },
  ],
};

export default function SetupPage() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState('-36.85');
  const [longitude, setLongitude] = useState('174.76');
  const [farmId, setFarmId] = useState('');
  const [featureCollectionText, setFeatureCollectionText] = useState(
    JSON.stringify(SAMPLE_FEATURE_COLLECTION, null, 2)
  );
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function onCreateFarm(event) {
    event.preventDefault();
    setError('');
    try {
      const payload = {
        name,
        description,
        latitude: Number(latitude),
        longitude: Number(longitude),
      };
      const response = await createFarm(payload);
      setFarmId(response.data.id);
      setMessage(`Farm created: ${response.data.name}`);
    } catch (createError) {
      setError(createError.message);
    }
  }

  async function onImportPaddocks() {
    setError('');
    try {
      const targetFarmId = farmId || (await getFarms()).data?.[0]?.id;
      if (!targetFarmId) {
        setError('Create a farm first.');
        return;
      }
      const parsed = JSON.parse(featureCollectionText);
      const response = await importPaddocks(targetFarmId, parsed);
      setMessage(`Imported ${response.meta.count} paddocks.`);
    } catch (importError) {
      setError(importError.message);
    }
  }

  return (
    <section className="page-grid">
      <article className="card">
        <h2>Create Farm</h2>
        <form onSubmit={onCreateFarm} className="form">
          <label>
            Farm Name
            <input value={name} onChange={(event) => setName(event.target.value)} required />
          </label>
          <label>
            Description
            <input value={description} onChange={(event) => setDescription(event.target.value)} />
          </label>
          <label>
            Latitude
            <input value={latitude} onChange={(event) => setLatitude(event.target.value)} required />
          </label>
          <label>
            Longitude
            <input value={longitude} onChange={(event) => setLongitude(event.target.value)} required />
          </label>
          <button type="submit">Create Farm</button>
        </form>
      </article>

      <article className="card wide">
        <h2>Import Paddocks (GeoJSON FeatureCollection)</h2>
        <textarea
          value={featureCollectionText}
          onChange={(event) => setFeatureCollectionText(event.target.value)}
          rows={16}
        />
        <button onClick={onImportPaddocks}>Import Paddocks</button>
      </article>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
