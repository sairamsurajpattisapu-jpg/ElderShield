import React from 'react';
import {
  Shield,
  LayoutDashboard,
  Radio,
  PhoneCall,
  MessageSquare,
  FileCheck2,
  TrendingUp,
  History,
  Sliders,
  Phone,
  X,
  Smartphone,
} from 'lucide-react';
import type { NavTab } from './Header';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  hasActiveResult: boolean;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  isBackendHealthy: boolean;
  activeSessionsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  hasActiveResult,
  isOpenMobile,
  onCloseMobile,
  isBackendHealthy,
  activeSessionsCount,
}) => {
  const primaryNavItems: { id: NavTab; label: string; icon: React.ReactNode; badge?: string }[] = [
    {
      id: 'dashboard',
      label: 'Overview',
      icon: <LayoutDashboard size={18} strokeWidth={1.9} />,
    },
    {
      id: 'live',
      label: 'Live Audio Monitor',
      icon: <Radio size={18} strokeWidth={1.9} />,
      badge: activeSessionsCount > 0 ? `${activeSessionsCount} active` : undefined,
    },
    {
      id: 'caller',
      label: 'Caller Intelligence',
      icon: <PhoneCall size={18} strokeWidth={1.9} />,
    },
    {
      id: 'analyze',
      label: 'Analyze Transcript',
      icon: <MessageSquare size={18} strokeWidth={1.9} />,
    },
  ];

  const evidenceNavItems: { id: NavTab; label: string; icon: React.ReactNode; disabled?: boolean }[] = [
    {
      id: 'results',
      label: 'Evidence Ledger',
      icon: <FileCheck2 size={18} strokeWidth={1.9} />,
      disabled: !hasActiveResult,
    },
    {
      id: 'timeline',
      label: 'Risk Velocity',
      icon: <TrendingUp size={18} strokeWidth={1.9} />,
      disabled: !hasActiveResult,
    },
    {
      id: 'recent',
      label: 'Evaluation History',
      icon: <History size={18} strokeWidth={1.9} />,
    },
  ];

  const systemNavItems: { id: NavTab; label: string; icon: React.ReactNode }[] = [
    {
      id: 'settings',
      label: 'Settings & Privacy',
      icon: <Sliders size={18} strokeWidth={1.9} />,
    },
  ];

  const handleNavClick = (tab: NavTab, disabled?: boolean) => {
    if (disabled) return;
    onSelectTab(tab);
    onCloseMobile();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          onClick={onCloseMobile}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(32, 41, 35, 0.4)',
            zIndex: 998,
            backdropFilter: 'blur(2px)',
          }}
          aria-hidden="true"
        />
      )}

      {/* Main Sidebar Container */}
      <aside
        style={{
          width: 'var(--sidebar-width)',
          backgroundColor: 'var(--bg-surface)',
          borderRight: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          position: 'fixed',
          top: 0,
          bottom: 0,
          left: 0,
          zIndex: 999,
          transform: isOpenMobile ? 'translateX(0)' : undefined,
          transition: 'transform 0.2s ease',
        }}
        className={`es-sidebar ${isOpenMobile ? 'mobile-open' : ''}`}
      >
        {/* Brand Header */}
        <div
          style={{
            padding: '22px 20px 18px',
            borderBottom: '1px solid var(--divider-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div
            onClick={() => handleNavClick('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              cursor: 'pointer',
              userSelect: 'none',
            }}
          >
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--brand-primary)',
                color: 'var(--text-on-brand)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                boxShadow: 'var(--shadow-subtle)',
              }}
            >
              <Shield size={20} strokeWidth={2.4} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span
                  style={{
                    fontFamily: 'var(--font-heading)',
                    fontSize: '1.2rem',
                    fontWeight: 800,
                    letterSpacing: '-0.02em',
                    color: 'var(--text-primary)',
                  }}
                >
                  Elder<span style={{ color: 'var(--brand-primary)' }}>Shield</span>
                </span>
              </div>
              <p
                style={{
                  fontSize: '0.74rem',
                  color: 'var(--text-secondary)',
                  fontWeight: 500,
                  marginTop: '1px',
                }}
              >
                Companion Console
              </p>
            </div>
          </div>

          {/* Mobile Close Button */}
          <button
            onClick={onCloseMobile}
            className="mobile-close-btn"
            style={{
              background: 'none',
              border: 'none',
              padding: '6px',
              color: 'var(--text-secondary)',
              display: 'none',
            }}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        {/* Companion Relationship Pill */}
        <div style={{ padding: '14px 20px 8px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 12px',
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.78rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Smartphone size={14} color="var(--brand-primary)" />
              <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                Android Protection
              </span>
            </div>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                fontWeight: 600,
                color: isBackendHealthy ? 'var(--brand-primary)' : 'var(--text-muted)',
              }}
            >
              <span
                style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: isBackendHealthy ? 'var(--brand-primary)' : 'var(--text-muted)',
                }}
              />
              {isBackendHealthy ? 'Linked' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Scrollable Navigation Area */}
        <nav
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '12px 14px',
            display: 'flex',
            flexDirection: 'column',
            gap: '18px',
          }}
        >
          {/* Section: Operational */}
          <div>
            <div
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-muted)',
                padding: '0 8px 6px',
              }}
            >
              Live Operations
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              {primaryNavItems.map((item) => {
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: 'var(--radius-sm)',
                      border: 'none',
                      backgroundColor: isActive ? 'var(--brand-accent)' : 'transparent',
                      color: isActive ? 'var(--brand-primary)' : 'var(--text-secondary)',
                      fontWeight: isActive ? 700 : 500,
                      fontSize: '0.88rem',
                      textAlign: 'left',
                      transition: 'background-color 0.12s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ color: isActive ? 'var(--brand-primary)' : 'var(--text-secondary)' }}>
                        {item.icon}
                      </span>
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        style={{
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          padding: '2px 7px',
                          borderRadius: 'var(--radius-full)',
                          backgroundColor: 'var(--brand-primary)',
                          color: '#FFFFFF',
                        }}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section: Evidence & Investigation */}
          <div>
            <div
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-muted)',
                padding: '0 8px 6px',
              }}
            >
              Investigation & Audit
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              {evidenceNavItems.map((item) => {
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id, item.disabled)}
                    disabled={item.disabled}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: 'var(--radius-sm)',
                      border: 'none',
                      backgroundColor: isActive ? 'var(--brand-accent)' : 'transparent',
                      color: isActive
                        ? 'var(--brand-primary)'
                        : item.disabled
                        ? 'var(--disabled-text)'
                        : 'var(--text-secondary)',
                      fontWeight: isActive ? 700 : 500,
                      fontSize: '0.88rem',
                      textAlign: 'left',
                      cursor: item.disabled ? 'not-allowed' : 'pointer',
                      opacity: item.disabled ? 0.6 : 1,
                      transition: 'background-color 0.12s ease',
                    }}
                  >
                    <span style={{ color: isActive ? 'var(--brand-primary)' : 'inherit' }}>
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section: System */}
          <div>
            <div
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-muted)',
                padding: '0 8px 6px',
              }}
            >
              System Controls
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              {systemNavItems.map((item) => {
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: 'var(--radius-sm)',
                      border: 'none',
                      backgroundColor: isActive ? 'var(--brand-accent)' : 'transparent',
                      color: isActive ? 'var(--brand-primary)' : 'var(--text-secondary)',
                      fontWeight: isActive ? 700 : 500,
                      fontSize: '0.88rem',
                      textAlign: 'left',
                      transition: 'background-color 0.12s ease',
                    }}
                  >
                    <span style={{ color: isActive ? 'var(--brand-primary)' : 'inherit' }}>
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </nav>

        {/* Sidebar Footer */}
        <div
          style={{
            padding: '16px 18px',
            borderTop: '1px solid var(--divider-subtle)',
            backgroundColor: 'var(--bg-secondary)',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          {/* Emergency Helpline Callout */}
          <a
            href="tel:1930"
            title="Call National Cybercrime Helpline 1930"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '8px 12px',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              fontWeight: 600,
              boxShadow: 'var(--shadow-subtle)',
            }}
          >
            <Phone size={14} color="var(--risk-high)" />
            <span>Cybercrime Helpline: <strong>1930</strong></span>
          </a>

          <div
            style={{
              fontSize: '0.72rem',
              color: 'var(--text-muted)',
              textAlign: 'center',
              lineHeight: 1.4,
            }}
          >
            HWV4-PS05 • ITU E.164
            <br />
            Zero-Disk Retention Active
          </div>
        </div>
      </aside>
    </>
  );
};
