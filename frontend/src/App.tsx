import { MotionProvider } from '@/hooks/useMotion';
import { Navigate, Route, Routes, useParams } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { PublicLayout } from '@/components/layout/Public';
import { ROUTES } from '@/lib/routes';
import Landing from '@/pages/Landing';
import Dashboard from '@/pages/Dashboard';
import Products from '@/pages/Products';
import ProductWorkspace from '@/pages/ProductWorkspace';
import Analyze from '@/pages/Analyze';
import DataSources from '@/pages/DataSources';
import TextLab from '@/pages/TextLab';
import Help from '@/pages/Help';
import Settings from '@/pages/Settings';
import Technical from '@/pages/Technical';
import Harvester from '@/pages/Harvester';
import { Login, Recover, Register } from '@/pages/Auth';

function ProductIdRedirect() {
  const { id } = useParams<{ id: string }>();
  return <Navigate to={`/product/${encodeURIComponent(id ?? '')}/overview`} replace />;
}

/**
 * Single router conforming to FRONTEND_SPEC.md v4:
 * - Public routes: Landing, Login, Register, Recover
 * - AppShell routes: Dashboard, All Products, Product Workspace (/product/:id/:tab),
 *   Analyze a Link, Data Sources, Text Lab, Help, Settings, Technical
 * - Spec redirects: /reviews, /analysis, /topics, /language, /readability, /analytics -> /products;
 *   /harvester -> /analyze; /about -> /help.
 */
export default function App() {
  return (
    <MotionProvider>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path={ROUTES.landing} element={<Landing />} />
          <Route path={ROUTES.login} element={<Login />} />
          <Route path={ROUTES.register} element={<Register />} />
          <Route path={ROUTES.recover} element={<Recover />} />
        </Route>

        <Route element={<AppShell />}>
          <Route path={ROUTES.dashboard} element={<Dashboard />} />
          <Route path={ROUTES.products} element={<Products />} />
          <Route path="/product/:id/:tab" element={<ProductWorkspace />} />
          <Route path="/product/:id" element={<ProductIdRedirect />} />
          <Route path={ROUTES.analyze} element={<Analyze />} />
          <Route path={ROUTES.data} element={<DataSources />} />
          <Route path={ROUTES.textLab} element={<TextLab />} />
          <Route path={ROUTES.help} element={<Help />} />
          <Route path={ROUTES.settings} element={<Settings />} />
          <Route path={ROUTES.technical} element={<Technical />} />
          <Route path="/harvester-admin" element={<Harvester />} />

          {/* Explicit redirects per FRONTEND_SPEC.md v4 */}
          <Route path="/reviews" element={<Navigate to={ROUTES.products} replace />} />
          <Route path="/analysis" element={<Navigate to={ROUTES.products} replace />} />
          <Route path="/topics" element={<Navigate to={ROUTES.products} replace />} />
          <Route path="/language" element={<Navigate to={ROUTES.products} replace />} />
          <Route path="/readability" element={<Navigate to={ROUTES.products} replace />} />
          <Route path="/analytics" element={<Navigate to={ROUTES.products} replace />} />
          <Route path="/harvester" element={<Navigate to={ROUTES.analyze} replace />} />
          <Route path="/about" element={<Navigate to={ROUTES.help} replace />} />
        </Route>

        <Route path="*" element={<Navigate to={ROUTES.landing} replace />} />
      </Routes>
    </MotionProvider>
  );
}
