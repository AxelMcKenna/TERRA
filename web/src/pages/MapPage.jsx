import { useEffect, useMemo, useState } from 'react';

import {
  getFarms,
  getObservationDates,
  getObservationsByDate,
  getPaddocks,
  getPaddockSeries,
  getLatestRecommendation,
} from '../api/client';
import PaddockMap from '../components/PaddockMap';
import TrendChart from '../components/TrendChart';

export default function MapPage() {
  const [farm, setFarm] = useState(null);
  const [paddocks, setPaddocks] = useState([]);
  const [dates, setDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [observations, setObservations] = useState([]);
  const [selectedPaddockId, setSelectedPaddockId] = useState('');
  const [series, setSeries] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadFarmContext() {
      try {
        const farmResponse = await getFarms();
        const firstFarm = farmResponse.data?.[0];
        if (!firstFarm) {
          return;
        }
        setFarm(firstFarm);

        const [paddockResponse, datesResponse, recResponse] = await Promise.all([
          getPaddocks(firstFarm.id),
          getObservationDates(firstFarm.id),
          getLatestRecommendation(firstFarm.id).catch(() => ({ data: null })),
        ]);

        const paddockList = paddockResponse.data || [];
        setPaddocks(paddockList);
        if (paddockList.length > 0) {
          setSelectedPaddockId(paddockList[0].id);
        }

        const dateList = datesResponse.data?.dates || [];
        setDates(dateList);
        if (dateList.length > 0) {
          setSelectedDate(dateList[0]);
        }

        const recRows = recResponse.data?.paddock_recommendations || [];
        setRecommendations(recRows);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadFarmContext();
  }, []);

  useEffect(() => {
    async function loadObservations() {
      if (!farm || !selectedDate) {
        return;
      }
      try {
        const response = await getObservationsByDate(farm.id, selectedDate);
        setObservations(response.data || []);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadObservations();
  }, [farm, selectedDate]);

  useEffect(() => {
    async function loadSeries() {
      if (!selectedPaddockId) {
        return;
      }
      try {
        const response = await getPaddockSeries(selectedPaddockId);
        setSeries(response.data || null);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadSeries();
  }, [selectedPaddockId]);

  const selectedPaddock = useMemo(
    () => paddocks.find((paddock) => paddock.id === selectedPaddockId),
    [paddocks, selectedPaddockId]
  );

  const selectedRecommendation = useMemo(
    () => recommendations.find((row) => row.paddock_id === selectedPaddockId),
    [recommendations, selectedPaddockId]
  );

  return (
    <section className="map-layout">
      <article className="map-card">
        <div className="map-toolbar">
          <h2>Map View</h2>
          <label>
            Date
            <select value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)}>
              {dates.map((dateValue) => (
                <option key={dateValue} value={dateValue}>
                  {dateValue}
                </option>
              ))}
            </select>
          </label>
        </div>
        <PaddockMap
          paddocks={paddocks}
          observations={observations}
          onSelectPaddock={setSelectedPaddockId}
          fallbackCenter={farm ? [farm.longitude, farm.latitude] : [174.76, -36.85]}
        />
      </article>

      <aside className="panel-card">
        <h3>{selectedPaddock?.name || 'Paddock Detail'}</h3>
        {selectedPaddock && <p>Area: {selectedPaddock.area_ha.toFixed(2)} ha</p>}
        {selectedRecommendation && (
          <p>
            <strong>{selectedRecommendation.rec_type}</strong>: {selectedRecommendation.message}
          </p>
        )}
        <TrendChart points={series?.points || []} />
      </aside>

      {error && <p className="error">{error}</p>}
    </section>
  );
}
