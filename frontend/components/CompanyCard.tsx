'use client'
import { useState } from 'react'
import { UserCircle, LinkedinLogo, ArrowClockwise, CircleNotch, Trash } from '@phosphor-icons/react'
import StatusBadge from './StatusBadge'
import { rerunResearch, deleteCompany } from '@/lib/api'
import type { Company } from '@/lib/api'

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

export default function CompanyCard({
  company,
  onRerun,
}: {
  company: Company
  onRerun?: () => void
}) {
  const fitScore = company.fit_score
  const hasScore = fitScore != null
  const tech = (company.tech_stack || []).slice(0, 3)
  const [rerunning, setRerunning] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const canRerun = ['discovered', 'skipped_low_fit', 'skipped_by_user'].includes(
    company.status
  )

  const handleRerun = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (rerunning) return
    setRerunning(true)
    await rerunResearch(company.id)
    setTimeout(() => {
      setRerunning(false)
      onRerun?.()
    }, 1200)
  }

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (deleting) return
    setDeleting(true)
    await deleteCompany(company.id)
    onRerun?.() // Trigger the refresh callback to remove it from the screen
  }

  const isActive = ['discovered', 'researching', 'drafting', 'approved', 'delivering'].includes(
    company.status
  )

  return (
    <div
      style={{
        background: 'var(--surface)',
        border: isActive ? '1px solid var(--ink)' : '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '14px 16px',
        display: 'flex',
        gap: 14,
        alignItems: 'flex-start',
        transition: 'transform 0.15s ease, border-color 0.15s ease, box-shadow 0.2s ease',
        boxShadow: isActive ? 'var(--shadow)' : 'none',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)'
        e.currentTarget.style.borderColor = 'var(--border-strong)'
        e.currentTarget.style.boxShadow = 'var(--shadow)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.borderColor = isActive ? 'var(--ink)' : 'var(--border)'
        e.currentTarget.style.boxShadow = isActive ? 'var(--shadow)' : 'none'
      }}
    >
      {isActive ? (
        <div
          style={{
            width: 44,
            height: 44,
            flexShrink: 0,
            borderRadius: 11,
            background: 'var(--bg-2)',
            border: '1px dashed var(--border-strong)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircleNotch
            size={18}
            weight="bold"
            color="var(--ink)"
            style={{ animation: 'spin 1s linear infinite' }}
          />
        </div>
      ) : hasScore ? (
        <FitRing score={fitScore} />
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

        {company.recent_news && (
          <div
            style={{
              fontSize: 12,
              color: 'var(--text-dim)',
              lineHeight: 1.5,
              marginBottom: 8,
            }}
          >
            {company.recent_news.length > 150
              ? company.recent_news.slice(0, 150) + '…'
              : company.recent_news}
          </div>
        )}

        {(company.funding_stage || tech.length > 0) && (
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {company.funding_stage && <span className="tag">{company.funding_stage}</span>}
            {tech.map((t) => (
              <span key={t} className="tag">
                {t}
              </span>
            ))}
          </div>
        )}

        <div style={{ display: 'flex', gap: 8, marginTop: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          {confirmDelete ? (
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                background: 'var(--bg-2)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                padding: '4px 10px',
                fontSize: 12,
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <span style={{ color: 'var(--text-dim)', fontWeight: 500 }}>Delete?</span>
              <button
                onClick={handleDelete}
                disabled={deleting}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--red, #ef4444)',
                  fontWeight: 700,
                  cursor: 'pointer',
                  padding: '2px 4px',
                }}
              >
                {deleting ? 'Deleting…' : 'Yes'}
              </button>
              <span style={{ color: 'var(--border-strong)' }}>|</span>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setConfirmDelete(false)
                }}
                disabled={deleting}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--muted)',
                  fontWeight: 600,
                  cursor: 'pointer',
                  padding: '2px 4px',
                }}
              >
                No
              </button>
            </div>
          ) : (
            <>
              {canRerun && (
                <button
                  onClick={handleRerun}
                  disabled={rerunning}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    background: 'transparent',
                    border: '1px solid var(--border)',
                    borderRadius: 8,
                    padding: '5px 11px',
                    fontSize: 12,
                    fontWeight: 600,
                    color: rerunning ? 'var(--muted)' : 'var(--ink)',
                    cursor: rerunning ? 'wait' : 'pointer',
                  }}
                >
                  <ArrowClockwise
                    size={13}
                    weight="bold"
                    style={rerunning ? { animation: 'spin 0.7s linear infinite' } : undefined}
                  />
                  {rerunning ? 'Researching…' : 'Re-research'}
                </button>
              )}

              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setConfirmDelete(true)
                }}
                disabled={rerunning}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 28,
                  height: 28,
                  background: 'transparent',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--muted)',
                  cursor: 'pointer',
                  transition: 'color 0.15s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = 'var(--red, #ef4444)'
                  e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = 'var(--muted)'
                  e.currentTarget.style.borderColor = 'var(--border)'
                }}
                title="Delete company"
              >
                <Trash size={14} />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
