'use client'
import { UserCircle, LinkedinLogo } from '@phosphor-icons/react'
import StatusBadge from './StatusBadge'

function FitRing({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(100, (score / 10) * 100))
  const r = 17
  const c = 2 * Math.PI * r
  return (
    <div style={{ position: 'relative', width: 44, height: 44, flexShrink: 0 }}>
      <svg width="44" height="44" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="22" cy="22" r={r} stroke="var(--border-strong)" strokeWidth="3" fill="none" />
        <circle
          cx="22"
          cy="22"
          r={r}
          stroke="var(--ink)"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c - (c * pct) / 100}
          style={{ transition: 'stroke-dashoffset 0.6s cubic-bezier(0.22,1,0.36,1)' }}
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 12.5,
          fontWeight: 700,
          color: 'var(--ink)',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {score.toFixed(1)}
      </div>
    </div>
  )
}

export default function CompanyCard({ company }: { company: any }) {
  const hasScore = company.fit_score != null
  const tech = (company.tech_stack || []).slice(0, 3)

  return (
    <div
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '14px 16px',
        display: 'flex',
        gap: 14,
        alignItems: 'flex-start',
        transition: 'transform 0.15s ease, border-color 0.15s ease, box-shadow 0.2s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)'
        e.currentTarget.style.borderColor = 'var(--border-strong)'
        e.currentTarget.style.boxShadow = 'var(--shadow)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.borderColor = 'var(--border)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {hasScore ? (
        <FitRing score={company.fit_score} />
      ) : (
        <div
          style={{
            width: 44,
            height: 44,
            flexShrink: 0,
            borderRadius: 11,
            background: 'var(--surface-2)',
            border: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 17,
            fontWeight: 700,
            color: 'var(--muted)',
          }}
        >
          {(company.name || '?').charAt(0).toUpperCase()}
        </div>
      )}

      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: 10,
            marginBottom: 6,
          }}
        >
          <span
            style={{
              fontWeight: 600,
              fontSize: 14.5,
              letterSpacing: '-0.01em',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {company.name}
          </span>
          <StatusBadge status={company.status} />
        </div>

        {company.hiring_manager && (
          <div
            style={{
              fontSize: 12,
              color: 'var(--text-dim)',
              marginBottom: 8,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              flexWrap: 'wrap',
            }}
          >
            <UserCircle size={14} weight="duotone" color="#78716c" />
            <span style={{ color: 'var(--ink)', fontWeight: 600 }}>
              {company.hiring_manager}
            </span>
            {company.hiring_manager_role && (
              <span style={{ color: 'var(--muted)' }}>· {company.hiring_manager_role}</span>
            )}
            {company.hiring_manager_linkedin && (
              <a
                href={company.hiring_manager_linkedin}
                target="_blank"
                rel="noreferrer"
                title="View LinkedIn profile"
                style={{ display: 'inline-flex', alignItems: 'center', color: 'var(--muted)' }}
                onClick={(e) => e.stopPropagation()}
              >
                <LinkedinLogo size={14} weight="fill" />
              </a>
            )}
          </div>
        )}

        {(company.funding_stage || tech.length > 0) && (
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {company.funding_stage && <span className="tag">{company.funding_stage}</span>}
            {tech.map((t: string) => (
              <span key={t} className="tag">
                {t}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
