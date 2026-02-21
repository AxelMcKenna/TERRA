import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

const COLORS = {
  'Very Low': '#8b0000',
  Low: '#dd6b20',
  Medium: '#c7a323',
  High: '#2f855a',
};

function toFeatureCollection(paddocks, observations) {
  const obsByPaddockId = new Map(observations.map((item) => [item.paddock_id, item]));
  return {
    type: 'FeatureCollection',
    features: paddocks.map((paddock) => {
      const obs = obsByPaddockId.get(paddock.id);
      const bucket = obs?.bucket || 'Low';
      return {
        type: 'Feature',
        geometry: paddock.geom_geojson,
        properties: {
          id: paddock.id,
          name: paddock.name,
          bucket,
          fill: COLORS[bucket] || COLORS.Low,
        },
      };
    }),
  };
}

export default function PaddockMap({ paddocks, observations, onSelectPaddock, fallbackCenter }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const token = import.meta.env.VITE_MAPBOX_TOKEN;

  useEffect(() => {
    if (!token || !containerRef.current) {
      return undefined;
    }

    mapboxgl.accessToken = token;
    mapRef.current = new mapboxgl.Map({
      container: containerRef.current,
      style: 'mapbox://styles/mapbox/outdoors-v12',
      center: fallbackCenter,
      zoom: 13,
    });

    mapRef.current.on('load', () => {
      mapRef.current.addSource('paddocks', {
        type: 'geojson',
        data: toFeatureCollection(paddocks, observations),
      });
      mapRef.current.addLayer({
        id: 'paddock-fill',
        type: 'fill',
        source: 'paddocks',
        paint: {
          'fill-color': ['get', 'fill'],
          'fill-opacity': 0.65,
        },
      });
      mapRef.current.addLayer({
        id: 'paddock-line',
        type: 'line',
        source: 'paddocks',
        paint: {
          'line-color': '#1a202c',
          'line-width': 1.5,
        },
      });
      mapRef.current.on('click', 'paddock-fill', (event) => {
        const feature = event.features?.[0];
        if (feature?.properties?.id) {
          onSelectPaddock(feature.properties.id);
        }
      });
    });

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [token]);

  useEffect(() => {
    if (!mapRef.current) {
      return;
    }

    const updateSource = () => {
      const source = mapRef.current?.getSource('paddocks');
      if (source) {
        source.setData(toFeatureCollection(paddocks, observations));
      }
    };

    if (mapRef.current.isStyleLoaded()) {
      updateSource();
      return;
    }

    mapRef.current.once('load', updateSource);
  }, [paddocks, observations]);

  if (!token) {
    return (
      <div className="map-fallback">
        <p>`VITE_MAPBOX_TOKEN` is not set.</p>
        <p>The app is still usable for API/data validation.</p>
      </div>
    );
  }

  return <div className="map" ref={containerRef} />;
}
