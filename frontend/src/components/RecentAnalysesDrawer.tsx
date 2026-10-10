import React, { useState, useMemo } from 'react';
import {
  History,
  ShieldAlert,
  ShieldCheck,
  AlertOctagon,
  HelpCircle,
  ChevronRight,
  Search,
  Filter,
  Download,
  Printer,
  Database,
  ArrowUpDown,
} from 'lucide-react';
import type { RiskAssessment, RiskLevel } from '../types';

interface RecentAnalysesDrawerProps {
  recentList: RiskAssessment[];
  onSelectAnalysis: (result: RiskAssessment) => void;
  activeId?: string;
  isRetainingHistory: boolean;
}

export const RecentAnalysesDrawer: React.FC<RecentAnalysesDrawerProps> = ({
  recentList,
  onSelectAnalysis,
  activeId,
  isRetainingHistory,
}) => {
  const [filterLevel, setFilterLevel] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  // Filtered and sorted analyses
  const filteredList = useMemo(() => {
    return recentList
      .filter((item) => {
        if (filterLevel !== 'ALL' && item.risk_level !== filterLevel) {
          return false;
        }
        if (!searchQuery.trim()) return true;
        const q = searchQuery.toLowerCase();
        const idMatch = item.id.toLowerCase().includes(q);
        const langMatch = item.language_detected.toLowerCase().includes(q);
        const decisionMatch = item.decision.toLowerCase().includes(q);
        const evidenceMatch = item.evidence.some(
          (e) => e.signal_category.toLowerCase().includes(q) || e.explanation.toLowerCase().includes(q) || e.exact_quote.toLowerCase().includes(q)
        );
        return idMatch || langMatch || decisionMatch || evidenceMatch;
      })
      .sort((a, b) => {
        if (sortOrder === 'desc') {
          return b.risk_score - a.risk_score;
        }
        return a.risk_score - b.risk_score;
      });
  }, [recentList, filterLevel, searchQuery, sortOrder]);

  const getRiskBadge = (risk: RiskLevel) => {
    switch (risk) {
      case 'HIGH_RISK':
        return {
          className: 'badge-danger',
          icon: <AlertOctagon size={13} />,
          label: 'High Risk',
        };
      case 'SUSPICIOUS':
        return {
          className: 'badge-warning',
          icon: <ShieldAlert size={13} />,
          label: 'Suspicious',
        };
      case 'LOW_RISK':
        return {
          className: 'badge-safe',
          icon: <ShieldCheck size={13} />,
          label: 'Low Risk',
        };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return {
          className: 'badge-neutral',
          icon: <HelpCircle size={13} />,
          label: 'Insufficient Evidence',
        };
    }
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(recentList, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `eldershield_evaluations_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handlePrintAudit = () => {
    window.print();
  };

  return (
    <section
      aria-label="Recent Evaluations Ledger"
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '24px',
        marginBottom: '28px',
        boxShadow: 'var(--shadow-card)',
      }}
    >
      {/* Top Header & Metadata */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: '20px',
          flexWrap: 'wrap',
          gap: '14px',
          borderBottom: '1px solid var(--divider-subtle)',
          paddingBottom: '16px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-secondary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--brand-primary)',
              }}
            >
              <History size={18} />
            </div>
            <div>
              <h3
                style={{
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  letterSpacing: '-0.01em',
                }}
              >
                Evaluation Ledger & Historical Scans
              </h3>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                Verifiable record of multi-vector behavioral evaluations and risk determinations.
              </p>
            </div>
          </div>
        </div>

        {/* Right Action Buttons & Privacy indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '5px 10px',
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.78rem',
              color: 'var(--text-secondary)',
            }}
          >
            <Database size={13} color="var(--brand-primary)" />
            <span>
              {isRetainingHistory ? 'Encrypted Browser Retention' : 'Session-Scoped (Zero-Disk)'}
            </span>
          </div>

          {recentList.length > 0 && (
            <>
              <button
                onClick={handleExportJSON}
                title="Export evaluation records as JSON"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                }}
              >
                <Download size={14} />
                <span>Export JSON</span>
              </button>

              <button
                onClick={handlePrintAudit}
                title="Print clinical evaluation ledger"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                }}
              >
                <Printer size={14} />
                <span>Print Ledger</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '18px',
        }}
      >
        {/* Risk Level Filter Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Filter size={13} />
            <span>Filter:</span>
          </span>
          {[
            { id: 'ALL', label: `All (${recentList.length})` },
            { id: 'HIGH_RISK', label: `High Risk (${recentList.filter((r) => r.risk_level === 'HIGH_RISK').length})` },
            { id: 'SUSPICIOUS', label: `Suspicious (${recentList.filter((r) => r.risk_level === 'SUSPICIOUS').length})` },
            { id: 'LOW_RISK', label: `Low Risk (${recentList.filter((r) => r.risk_level === 'LOW_RISK').length})` },
          ].map((chip) => {
            const isSelected = filterLevel === chip.id;
            return (
              <button
                key={chip.id}
                onClick={() => setFilterLevel(chip.id)}
                style={{
                  padding: '5px 11px',
                  borderRadius: 'var(--radius-full)',
                  border: isSelected ? '1px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                  backgroundColor: isSelected ? 'var(--brand-primary)' : 'var(--bg-surface)',
                  color: isSelected ? 'var(--text-on-brand)' : 'var(--text-secondary)',
                  fontSize: '0.78rem',
                  fontWeight: isSelected ? 700 : 500,
                }}
              >
                {chip.label}
              </button>
            );
          })}
        </div>

        {/* Search Box & Sort Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 10px',
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            <Search size={14} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search scan ID, language, flags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                border: 'none',
                background: 'transparent',
                outline: 'none',
                fontSize: '0.82rem',
                color: 'var(--text-primary)',
                width: '180px',
              }}
            />
          </div>

          <button
            onClick={() => setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')}
            title={`Sort score ${sortOrder === 'desc' ? 'Highest first' : 'Lowest first'}`}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'var(--bg-surface)',
              fontSize: '0.78rem',
              color: 'var(--text-secondary)',
              fontWeight: 500,
            }}
          >
            <ArrowUpDown size={13} />
            <span>Score {sortOrder === 'desc' ? '↓' : '↑'}</span>
          </button>
        </div>
      </div>

      {/* Evaluations List or Empty State */}
      {filteredList.length === 0 ? (
        <div
          style={{
            padding: '40px 20px',
            textAlign: 'center',
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-sm)',
            border: '1px dashed var(--border-subtle)',
          }}
        >
          <HelpCircle size={28} color="var(--text-muted)" style={{ margin: '0 auto 8px' }} />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            No Matching Evaluations Found
          </h4>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '420px', margin: '4px auto 0' }}>
            {recentList.length === 0
              ? 'No conversations have been evaluated in this session yet. Run a live audio scan or load a benchmark demo to begin.'
              : 'Try clearing your search query or adjusting the risk filter above.'}
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {filteredList.map((item) => {
            const badge = getRiskBadge(item.risk_level);
            const isSelected = activeId === item.id;

            return (
              <div
                key={item.id}
                onClick={() => onSelectAnalysis(item)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 18px',
                  backgroundColor: isSelected ? 'var(--bg-soft-sage)' : 'var(--bg-surface)',
                  border: isSelected ? '1.5px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  transition: 'background-color 0.12s ease, border-color 0.12s ease',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}
              >
                {/* Left: Badge & Identification */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px', minWidth: 0, flex: 1 }}>
                  <span className={badge.className} style={{ flexShrink: 0 }}>
                    {badge.icon}
                    <span>{badge.label}</span>
                  </span>

                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span
                        style={{
                          fontSize: '0.9rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                          fontFamily: 'monospace',
                        }}
                      >
                        #{item.id}
                      </span>
                      <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                        • {item.decision}
                      </span>
                      {item.is_demo && (
                        <span
                          style={{
                            fontSize: '0.72rem',
                            padding: '1px 6px',
                            borderRadius: 'var(--radius-xs)',
                            backgroundColor: 'var(--bg-secondary)',
                            border: '1px solid var(--border-subtle)',
                            color: 'var(--text-secondary)',
                            fontWeight: 600,
                          }}
                        >
                          Benchmark Case
                        </span>
                      )}
                    </div>

                    <div
                      style={{
                        fontSize: '0.78rem',
                        color: 'var(--text-muted)',
                        marginTop: '3px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        flexWrap: 'wrap',
                      }}
                    >
                      <span>{item.timestamp}</span>
                      <span>•</span>
                      <span>Lang: <strong>{item.language_detected}</strong></span>
                      <span>•</span>
                      <span>{item.turn_progression.length} Turns Evaluated</span>
                      <span>•</span>
                      <span>{item.evidence.length} Forensic Evidence Triggers</span>
                    </div>
                  </div>
                </div>

                {/* Right: Risk Score & Action */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexShrink: 0 }}>
                  <div style={{ textAlign: 'right' }}>
                    <div
                      style={{
                        fontSize: '1.25rem',
                        fontWeight: 800,
                        fontFamily: 'var(--font-heading)',
                        color:
                          item.risk_level === 'HIGH_RISK'
                            ? 'var(--risk-high)'
                            : item.risk_level === 'SUSPICIOUS'
                            ? 'var(--risk-warning)'
                            : 'var(--brand-primary)',
                        lineHeight: 1,
                      }}
                    >
                      {item.risk_score.toFixed(0)}
                      <span style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)' }}>
                        /100
                      </span>
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Calibrated Velocity
                    </div>
                  </div>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      color: isSelected ? 'var(--brand-primary)' : 'var(--text-secondary)',
                    }}
                  >
                    <span>View Findings</span>
                    <ChevronRight size={16} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
