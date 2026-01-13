import React from 'react';
import { DashboardSection } from '../../types/navigation';

interface HeaderProps {
  activeSection: DashboardSection;
  onSectionChange: (section: DashboardSection) => void;
}

const NAV_ITEMS: Array<{ label: string; section: DashboardSection }> = [
  { label: 'Dashboard', section: 'dashboard' },
  { label: 'Agents', section: 'agents' },
  { label: 'Workflows', section: 'workflows' },
  { label: 'Intelligence', section: 'intelligence' },
  { label: 'Financial', section: 'financial' },
  { label: 'Security', section: 'security' },
  { label: 'Leads', section: 'leads' },
  { label: 'Marketing', section: 'marketing' },
  { label: 'Subscribers', section: 'subscribers' },
  { label: 'Head Office', section: 'head-office' },
];

export const Header: React.FC<HeaderProps> = ({ activeSection, onSectionChange }) => (
  <header className="header-frame">
    <div className="header-brand">
      <div className="brand-glyph">FC</div>
      <div>
        <h1>Fallat CrewAI</h1>
        <p>Autonomous Operations Control Deck</p>
      </div>
    </div>
    <nav className="header-nav" aria-label="Dashboard sections">
      {NAV_ITEMS.map((item) => {
        const isActive = item.section === activeSection;
        return (
          <button
            key={item.section}
            type="button"
            className={`header-nav__button${isActive ? ' header-nav__button--active' : ''}`}
            onClick={() => onSectionChange(item.section)}
            aria-pressed={isActive}
          >
            {item.label}
          </button>
        );
      })}
    </nav>
  </header>
);
