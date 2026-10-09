import React from 'react';
import {
  Shield,
  PhoneCall,
  LayoutDashboard,
  MessageSquare,
  FileCheck2,
  TrendingUp,
  History,
  Sliders,
  Radio,
} from 'lucide-react';

export type NavTab = 'dashboard' | 'live' | 'analyze' | 'results' | 'timeline' | 'recent' | 'settings';

interface HeaderProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  hasActiveResult: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onSelectTab,
  hasActiveResult,
}) => {
  const navItems = [
    { id: 'dashboard' as NavTab, label: 'Dashboard', icon: <LayoutDashboard size={16} /> },
    { id: 'live' as NavTab, label: 'Live Call Detection', icon: <Radio size={16} /> },
    { id: 'analyze' as NavTab, label: 'Analyze Conversation', icon: <MessageSquare size={16} /> },
    { id: 'results' as NavTab, label: 'Risk Results', icon: <FileCheck2 size={16} />, disabled: !hasActiveResult },
    { id: 'timeline' as NavTab, label: 'Conversation Timeline', icon: <TrendingUp size={16} />, disabled: !hasActiveResult },
    { id: 'recent' as NavTab, label: 'Recent Analyses', icon: <History size={16} /> },
    { id: 'settings' as NavTab, label: 'Settings', icon: <Sliders size={16} /> },
  ];

  return (
    <header style={{
      backgroundColor: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      backdropFilter: 'blur(8px)',
    }}>
      {/* Top Banner Row */}
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '14px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '14px',
      }}>
        {/* Brand identity */}
        <div
          onClick={() => onSelectTab('dashboard')}
          style={{ display: 'flex', alignItems: 'center', gap: '14px', cursor: 'pointer' }}
        >
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            backgroundColor: 'rgba(6, 182, 212, 0.12)',
            border: '1.5px solid var(--accent-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-cyan)',
            boxShadow: '0 0 16px rgba(6, 182, 212, 0.2)',
          }}>
            <Shield size={24} strokeWidth={2.4} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                fontSize: '1.35rem',
                fontWeight: 800,
                letterSpacing: '-0.02em',
                color: 'var(--text-primary)',
              }}>
                Elder<span style={{ color: 'var(--accent-cyan)' }}>Shield</span>
              </span>
              <span style={{
                fontSize: '0.7rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                padding: '2px 7px',
                borderRadius: '4px',
                backgroundColor: 'rgba(20, 184, 166, 0.15)',
                color: 'var(--accent-teal)',
                border: '1px solid rgba(20, 184, 166, 0.3)',
              }}>
                HWV4-PS05
              </span>
            </div>
            <p style={{
              fontSize: '0.8rem',
              color: 'var(--text-secondary)',
              marginTop: '1px',
            }}>
              Real-Time Conversational Scam Detection for Elderly Users
            </p>
          </div>
        </div>

        {/* Emergency Helpline Callout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <a
            href="tel:1930"
            title="National Cyber Crime Reporting Helpline"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 14px',
              backgroundColor: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid var(--risk-high-border)',
              borderRadius: 'var(--radius-md)',
              color: '#fca5a5',
              textDecoration: 'none',
              fontWeight: 700,
              fontSize: '0.86rem',
            }}
          >
            <PhoneCall size={15} color="#ef4444" />
            <span>Cyber Helpline: <strong>1930</strong></span>
          </a>
        </div>
      </div>

      {/* Navigation Tabs Bar */}
      <nav style={{
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-primary)',
        overflowX: 'auto',
      }}>
        <div style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '0 24px',
          display: 'flex',
          gap: '4px',
          minWidth: 'max-content',
        }}>
          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => !item.disabled && onSelectTab(item.id)}
                disabled={item.disabled}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 16px',
                  background: 'transparent',
                  border: 'none',
                  borderBottom: isActive ? '2.5px solid var(--accent-cyan)' : '2.5px solid transparent',
                  color: isActive ? 'var(--accent-cyan)' : item.disabled ? 'var(--text-muted)' : 'var(--text-secondary)',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '0.88rem',
                  cursor: item.disabled ? 'not-allowed' : 'pointer',
                  opacity: item.disabled ? 0.4 : 1,
                  transition: 'all 0.15s ease',
                  whiteSpace: 'nowrap',
                }}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </header>
  );
};
