import {
  LayoutDashboard,
  Package,
  Link2,
  FolderUp,
  FlaskConical,
  HelpCircle,
  type LucideIcon,
} from 'lucide-react';

export const ROUTES = {
  landing: '/',
  dashboard: '/dashboard',
  products: '/products',
  product: '/product/:id/:tab',
  analyze: '/analyze',
  data: '/data',
  textLab: '/text-lab',
  help: '/help',
  settings: '/settings',
  technical: '/technical',
  login: '/login',
  register: '/register',
  recover: '/recover',

  // Aliases for redirects per FRONTEND_SPEC.md v4
  reviews: '/reviews',
  analysis: '/analysis',
  language: '/language',
  topics: '/topics',
  readability: '/readability',
  harvester: '/harvester',
  analytics: '/analytics',
  about: '/about',
} as const;

export type ProductTab =
  | 'overview'
  | 'reviews'
  | 'sentiment'
  | 'topics'
  | 'languages'
  | 'readability'
  | 'price';

export const PRODUCT_TABS: ProductTab[] = [
  'overview',
  'reviews',
  'sentiment',
  'topics',
  'languages',
  'readability',
  'price',
];

export const productRoute = (id: string, tab: ProductTab = 'overview') =>
  `/product/${encodeURIComponent(id)}/${tab}`;

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { to: ROUTES.dashboard, label: 'Dashboard', icon: LayoutDashboard },
  { to: ROUTES.products, label: 'All Products', icon: Package },
  { to: ROUTES.analyze, label: 'Analyze a Link', icon: Link2 },
  { to: ROUTES.data, label: 'Data Sources', icon: FolderUp },
  { to: ROUTES.textLab, label: 'Text Lab', icon: FlaskConical },
  { to: ROUTES.help, label: 'Help', icon: HelpCircle },
];
