'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  BarChart3,
  TrendingUp,
  Cpu,
  Newspaper,
  Briefcase,
  Target,
  Sparkles,
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  exact?: boolean;
  matchPrefix?: string;
}

const NAV_ITEMS: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard, exact: true },
  { name: 'Market', href: '/', icon: BarChart3, exact: false, matchPrefix: '/market' },
  { name: 'Stocks', href: '/stock/AAPL', icon: TrendingUp, exact: false, matchPrefix: '/stock' },
  { name: 'AI Debate', href: '/debate/NVDA', icon: Cpu, exact: false, matchPrefix: '/debate' },
  { name: 'News', href: '/news', icon: Newspaper, exact: false, matchPrefix: '/news' },
  { name: 'Performance', href: '/performance', icon: Target, exact: false, matchPrefix: '/performance' },
];

export default function Sidebar() {
  const pathname = usePathname();

  const isLinkActive = (item: NavItem) => {
    if (item.exact) {
      return pathname === item.href;
    }
    if (item.matchPrefix) {
      return pathname.startsWith(item.matchPrefix);
    }
    return pathname === item.href;
  };

  return (
    <aside className="sidebar">
      {/* Brand Logo */}
      <div className="sidebar-logo">
        <Link href="/" style={{ textDecoration: 'none', display: 'block' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="sidebar-logo-text">FINIQ</span>
            <Sparkles size={14} color="#7C5DFA" />
          </div>
          <div className="sidebar-logo-sub">AI Financial Intelligence</div>
          <span className="sidebar-logo-badge">PROTOTYPE</span>
        </Link>
      </div>

      {/* Navigation Links */}
      <div className="sidebar-section-title">Navigation</div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = isLinkActive(item);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`sidebar-link ${active ? 'active' : ''}`}
              title={item.name}
            >
              <Icon size={18} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className="sidebar-footer">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: '8px',
            fontSize: '11px',
            fontWeight: 600,
            color: 'var(--positive)',
          }}
        >
          <span
            style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: 'var(--positive)',
              boxShadow: '0 0 8px var(--positive)',
              display: 'inline-block',
            }}
          />
          <span>Demo Mode Active</span>
        </div>
        <div className="sidebar-footer-text">
          FINIQ Terminal v1.0
          <br />
          This project is a prototype and is not financial advice.
        </div>
      </div>
    </aside>
  );
}
