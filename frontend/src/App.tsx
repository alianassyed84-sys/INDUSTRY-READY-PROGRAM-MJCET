import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { PublicLayout } from '@/components/layout/Public';
import { ROUTES } from '@/lib/routes';
import Landing from '@/pages/Landing';
import Dashboard from '@/pages/Dashboard';
import Reviews from '@/pages/Reviews';
import Analysis from '@/pages/Analysis';
import Language from '@/pages/Language';
import Topics from '@/pages/Topics';
import Readability from '@/pages/Readability';
import { Login, Recover, Register } from '@/pages/Auth';
import Harvester from '@/pages/Harvester';
import Analytics from '@/pages/Analytics';
import Settings from '@/pages/Settings';
import About from '@/pages/About';

/** Single router: Landing + Auth use the public layout; all app pages share AppShell. */
export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path={ROUTES.landing} element={<Landing />} />
        <Route path={ROUTES.login} element={<Login />} />
        <Route path={ROUTES.register} element={<Register />} />
        <Route path={ROUTES.recover} element={<Recover />} />
      </Route>
      <Route element={<AppShell />}>
        <Route path={ROUTES.dashboard} element={<Dashboard />} />
        <Route path={ROUTES.reviews} element={<Reviews />} />
        <Route path={ROUTES.analysis} element={<Analysis />} />
        <Route path={ROUTES.language} element={<Language />} />
        <Route path={ROUTES.topics} element={<Topics />} />
        <Route path={ROUTES.readability} element={<Readability />} />
        <Route path={ROUTES.harvester} element={<Harvester />} />
        <Route path={ROUTES.analytics} element={<Analytics />} />
        <Route path={ROUTES.settings} element={<Settings />} />
        <Route path={ROUTES.about} element={<About />} />
      </Route>
      <Route path="*" element={<Navigate to={ROUTES.landing} replace />} />
    </Routes>
  );
}
