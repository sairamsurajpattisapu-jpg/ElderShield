import React, { useState } from 'react';
import {
  PhoneCall,
  Search,
  Building2,
  AlertTriangle,
  HelpCircle,
  AlertOctagon,
  ArrowRight,
  Info,
} from 'lucide-react';
import type { CallerIntelligenceResult } from '../types';
import { lookupCallerIdentity } from '../api';

interface CallerLookupViewProps {
  onStartAnalysisWithCaller?: (phoneNumber: string, claimedOrg?: string) => void;
}

export const CallerLookupView: React.FC<CallerLookupViewProps> = ({
  onStartAnalysisWithCaller,
}) => {
  const [phoneNumber, setPhoneNumber] = useState<string>('');
  const [claimedOrg, setClaimedOrg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<CallerIntelligenceResult | null>(null);

  // Common quick-test numbers for senior verification demo
  const quickTestCases = [
    { label: 'SBI Official Toll-Free', number: '18001234', org: 'State Bank of India' },
    { label: 'Claimed CBI (Private Mobile)', number: '+91 98490 12345', org: 'Central Bureau of Investigation' },
    { label: 'Unknown Mobile', number: '+91 91234 56789', org: '' },
  ];

  const handleLookup = async (overrideNumber?: string, overrideOrg?: string) => {
    const num = (overrideNumber !== undefined ? overrideNumber : phoneNumber).trim();
    const org = (overrideOrg !== undefined ? overrideOrg : claimedOrg).trim();

    setValidationError(null);
    setErrorMessage(null);
    setResult(null);

    if (!num) {
      setValidationError('Please enter a phone number to verify (e.g., +91 98490 12345 or 1800 1234).');
      return;
    }

    const digitsOnly = num.replace(/\D/g, '');
    if (digitsOnly.length < 3) {
      setValidationError('Phone number must contain at least 3 digits.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await lookupCallerIdentity(num, org || undefined);
      setResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Telecom registry lookup failed';
      setErrorMessage(`${msg}. Please verify your network connection and try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectQuickTest = (item: { number: string; org: string }) => {
    setPhoneNumber(item.number);
    setClaimedOrg(item.org);
    handleLookup(item.number, item.org);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Search Input Card */}
      <div className="es-card">
        <div style={{ marginBottom: '20px' }}>
          <h2
            style={{
              fontSize: '1.2rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <PhoneCall size={20} color="var(--brand-primary)" />
            <span>Caller Identity Triage & Spoof Conflict Verification</span>
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Cross-references incoming numbers against ITU E.164 formatting rules, national numbering plans, and institutional contact registries to detect impersonation.
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLookup();
          }}
          style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
        >
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
            <div>
              <label
                htmlFor="phone-number-input"
                style={{
                  display: 'block',
                  fontSize: '0.84rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginBottom: '6px',
                }}
              >
                Caller Phone Number *
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="phone-number-input"
                  type="text"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="e.g., +91 98490 12345 or 1800 1234"
                  style={{
                    width: '100%',
                    padding: '11px 14px 11px 38px',
                    borderRadius: 'var(--radius-sm)',
                    border: validationError ? '1.5px solid var(--risk-high)' : '1px solid var(--border-subtle)',
                    backgroundColor: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    fontSize: '0.94rem',
                  }}
                />
                <Search
                  size={17}
                  color="var(--text-muted)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="claimed-org-input"
                style={{
                  display: 'block',
                  fontSize: '0.84rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginBottom: '6px',
                }}
              >
                Claimed Institution / Organization (Optional)
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="claimed-org-input"
                  type="text"
                  value={claimedOrg}
                  onChange={(e) => setClaimedOrg(e.target.value)}
                  placeholder="e.g., State Bank of India, Delhi Police, CBI"
                  style={{
                    width: '100%',
                    padding: '11px 14px 11px 38px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-subtle)',
                    backgroundColor: 'var(--bg-primary)',
                    color: 'var(--text-primary)',
                    fontSize: '0.94rem',
                  }}
                />
                <Building2
                  size={17}
                  color="var(--text-muted)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
            </div>
          </div>

          {validationError && (
            <div style={{ fontSize: '0.84rem', color: 'var(--risk-high)', fontWeight: 600 }}>
              {validationError}
            </div>
          )}

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginTop: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Quick benchmarks:</span>
              {quickTestCases.map((tc, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectQuickTest(tc)}
                  style={{
                    fontSize: '0.78rem',
                    padding: '4px 9px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-secondary)',
                    fontWeight: 500,
                  }}
                >
                  {tc.label}
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{ minWidth: '150px' }}
            >
              {isLoading ? (
                <span>Verifying Number...</span>
              ) : (
                <>
                  <Search size={16} />
                  <span>Verify Caller</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Error Message Banner */}
      {errorMessage && (
        <div
          style={{
            padding: '16px 20px',
            backgroundColor: 'var(--risk-high-bg)',
            border: '1px solid var(--risk-high-border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--risk-high)',
            fontSize: '0.9rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <AlertOctagon size={18} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Result Card */}
      {result && (
        <div className="es-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Top Status Heading */}
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '14px',
              paddingBottom: '18px',
              borderBottom: '1px solid var(--divider-subtle)',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {result.national_format || result.e164_format || result.raw_input}
                </span>

                {/* Classification Badge */}
                {result.spoofing_suspected ? (
                  <span className="badge-danger">
                    <AlertOctagon size={14} />
                    <span>Identity Conflict Detected</span>
                  </span>
                ) : result.is_registered_institution ? (
                  <span className="badge-warning">
                    <Building2 size={14} />
                    <span>Known Registry Match</span>
                  </span>
                ) : !result.is_valid ? (
                  <span className="badge-danger">
                    <AlertTriangle size={14} />
                    <span>Invalid Number Format</span>
                  </span>
                ) : (
                  <span className="badge-neutral">
                    <HelpCircle size={14} />
                    <span>Caller Identity Unverified</span>
                  </span>
                )}
              </div>

              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Normalized E.164: <code>{result.e164_format || 'N/A'}</code> • Number Type: <strong>{result.number_type}</strong>
              </p>
            </div>

            {onStartAnalysisWithCaller && (
              <button
                type="button"
                onClick={() => onStartAnalysisWithCaller(result.national_format || result.raw_input, claimedOrg || undefined)}
                className="btn-secondary"
                style={{ fontSize: '0.84rem', padding: '8px 14px' }}
              >
                <span>Analyze Audio with this Caller</span>
                <ArrowRight size={14} />
              </button>
            )}
          </div>

          {/* Advisory Box */}
          <div
            style={{
              padding: '16px 18px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: result.spoofing_suspected
                ? 'var(--risk-high-bg)'
                : result.is_registered_institution
                ? 'var(--risk-warning-bg)'
                : 'var(--bg-secondary)',
              border: `1px solid ${
                result.spoofing_suspected
                  ? 'var(--risk-high-border)'
                  : result.is_registered_institution
                  ? 'var(--risk-warning-border)'
                  : 'var(--border-subtle)'
              }`,
              color: result.spoofing_suspected
                ? 'var(--risk-high)'
                : result.is_registered_institution
                ? 'var(--risk-warning)'
                : 'var(--text-primary)',
            }}
          >
            <div style={{ fontWeight: 700, fontSize: '0.94rem', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              {result.spoofing_suspected ? (
                <>
                  <AlertOctagon size={17} />
                  <span>CRITICAL IMPERSONATION ALERT</span>
                </>
              ) : result.is_registered_institution ? (
                <>
                  <AlertTriangle size={17} />
                  <span>REGISTRY MATCH DOES NOT PROVE CALLER IDENTITY</span>
                </>
              ) : (
                <>
                  <Info size={17} />
                  <span>CALLER ADVISORY</span>
                </>
              )}
            </div>

            <p style={{ fontSize: '0.88rem', lineHeight: 1.5 }}>
              {result.advisory}
            </p>

            {result.is_registered_institution && (
              <p style={{ fontSize: '0.82rem', marginTop: '8px', opacity: 0.9 }}>
                Important: Scammers frequently spoof real institutional phone numbers on caller ID displays. Even if the number appears to match {result.registered_organization || 'an institution'}, never disclose one-time passwords, NetBanking PINs, or card CVVs over incoming calls.
              </p>
            )}
          </div>

          {/* Detailed Telecom & Identity Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
            <div style={{ padding: '14px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
                Telecom Allocation
              </span>
              <div style={{ fontSize: '0.94rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                {result.geographic_region || 'India (National Plan)'}
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginTop: '2px' }}>
                {result.metadata_disclaimer || 'Initial carrier allocation circle'}
              </span>
            </div>

            <div style={{ padding: '14px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
                Network Provider
              </span>
              <div style={{ fontSize: '0.94rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                {result.carrier || 'Standard Telecom Carrier'}
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginTop: '2px' }}>
                Provider classification: {result.number_type}
              </span>
            </div>

            <div style={{ padding: '14px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
                Registry Status
              </span>
              <div style={{ fontSize: '0.94rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                {result.is_registered_institution ? (
                  result.registered_organization || 'Listed Institutional Contact'
                ) : (
                  'No Institutional Match'
                )}
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginTop: '2px' }}>
                ITU E.164 + National Database
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Empty State when no search executed yet */}
      {!result && !isLoading && !errorMessage && (
        <div
          style={{
            padding: '36px 24px',
            textAlign: 'center',
            backgroundColor: 'var(--bg-surface)',
            border: '1px dashed var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-secondary)',
          }}
        >
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              backgroundColor: 'var(--bg-secondary)',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 12px',
            }}
          >
            <Search size={22} />
          </div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            No Caller Number Evaluated
          </h3>
          <p style={{ fontSize: '0.86rem', maxWidth: '440px', margin: '0 auto' }}>
            Enter an incoming phone number above or click one of the quick benchmarks to verify telecom registration, identify spoof conflicts, and view safety recommendations.
          </p>
        </div>
      )}
    </div>
  );
};
