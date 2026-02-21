import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';

import DashboardPage from './pages/DashboardPage';
import MapPage from './pages/MapPage';
import SetupPage from './pages/SetupPage';

function App() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Farm Intelligence</p>
          <h1>Dev-Facing MVP</h1>
        </div>
        <nav>
          <Link className={location.pathname === '/dashboard' ? 'active' : ''} to="/dashboard">
            Dashboard
          </Link>
          <Link className={location.pathname === '/map' ? 'active' : ''} to="/map">
            Map
          </Link>
          <Link className={location.pathname === '/setup' ? 'active' : ''} to="/setup">
            Setup
          </Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/setup" element={<SetupPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
