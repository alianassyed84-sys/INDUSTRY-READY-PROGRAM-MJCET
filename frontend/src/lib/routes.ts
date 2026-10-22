import { BarChart3, BookOpen, FileText, Gauge, Globe2, Hash, LayoutDashboard, MessagesSquare, Download, type LucideIcon } from 'lucide-react';

export const ROUTES = {
  landing: '/', dashboard: '/dashboard', reviews: '/reviews', analysis: '/analysis', language: '/language',
  topics: '/topics', readability: '/readability', login: '/login', register: '/register', recover: '/recover',
  harvester: '/harvester', analytics: '/analytics', settings: '/settings', about: '/about',
} as const;

export interface NavItem { to: string; label: string; icon: LucideIcon }
export const NAV_ITEMS: NavItem[] = [
  { to: ROUTES.dashboard, label: 'Dashboard', icon: LayoutDashboard },
  { to: ROUTES.reviews, label: 'Product Reviews', icon: MessagesSquare },
  { to: ROUTES.analysis, label: 'Review Analysis', icon: BarChart3 },
  { to: ROUTES.language, label: 'Language Detection', icon: Globe2 },
  { to: ROUTES.topics, label: 'Topic Extraction', icon: Hash },
  { to: ROUTES.readability, label: 'Readability', icon: Gauge },
  { to: ROUTES.harvester, label: 'Review Harvester', icon: Download },
  { to: ROUTES.analytics, label: 'Analytics & Reports', icon: FileText },
  { to: ROUTES.about, label: 'About & Docs', icon: BookOpen },
];
