import { useEffect, useState } from 'react';

import { getFarms, getLatestRecommendation, getWeather, triggerIngest } from '../api/client';

export default function DashboardPage() {
  const [farm, setFarm] = useState(null);
  const [weather, setWeather] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      setError('');
      try {
        const farmsResponse = await getFarms();
        const firstFarm = farmsResponse.data?.[0];
        setFarm(firstFarm || null);
        if (!firstFarm) {
          setIsLoading(false);
          return;
        }

        const [weatherResponse, recommendationResponse] = await Promise.allSettled([
          getWeather(firstFarm.id),
          getLatestRecommendation(firstFarm.id),
        ]);

        if (weatherResponse.status === 'fulfilled') {
          setWeather(weatherResponse.value.data || []);
        }
        if (recommendationResponse.status === 'fulfilled') {
          setRecommendation(recommendationResponse.value.data || null);
        }
      } catch (loadError) {
        setError(loadError.message);
      } finally {
        setIsLoading(false);
      }
    }

    load();
  }, []);

  async function onRunPipeline() {
    if (!farm) {
      return;
    }
    setIsRunning(true);
    try {
      await triggerIngest(farm.id);
      const recommendationResponse = await getLatestRecommendation(farm.id);
      setRecommendation(recommendationResponse.data);
      const weatherResponse = await getWeather(farm.id);
      setWeather(weatherResponse.data || []);
    } catch (runError) {
      setError(runError.message);
    } finally {
      setIsRunning(false);
    }
  }

  if (isLoading) {
    return <p>Loading dashboard...</p>;
  }

  if (!farm) {
    return <p>No farm yet. Use Setup to create one.</p>;
  }

  return (
    <section className="page-grid">
      <article className="card">
        <h2>{farm.name}</h2>
        <p className="muted">{farm.description || 'No description yet.'}</p>
        <button onClick={onRunPipeline} disabled={isRunning}>
          {isRunning ? 'Running pipeline...' : 'Run Data Pipeline'}
        </button>
      </article>

      <article className="card">
        <h3>Weekly Summary</h3>
        {recommendation ? <pre>{recommendation.summary_md}</pre> : <p>No recommendation generated yet.</p>}
      </article>

      <article className="card wide">
        <h3>7-Day Forecast</h3>
        <div className="weather-strip">
          {weather.map((item) => (
            <div key={item.date} className="weather-cell">
              <strong>{item.date}</strong>
              <span>{item.rain_mm.toFixed(1)} mm</span>
              <span>
                {item.temp_min_c.toFixed(1)}° / {item.temp_max_c.toFixed(1)}°
              </span>
            </div>
          ))}
        </div>
      </article>

      {error && <p className="error">{error}</p>}
    </section>
  );
}
