'use client'
import {
  MagnifyingGlass,
  Brain,
  PenNib,
  Hourglass,
  CheckCircle,
  PaperPlaneTilt,
  ChatCircleDots,
  Target,
  Play,
  MinusCircle,
  Icon,
} from '@phosphor-icons/react'
import CompanyCard from './CompanyCard'
import type { Company } from '@/lib/api'

const COLUMNS: { key: string; label: string; icon: Icon }[] = [
  { key: 'discovered', label: 'Discovered', icon: MagnifyingGlass },
  { key: 'researched', label: 'Researched', icon: Brain },
  { key: 'skipped', label: 'Skipped / Low Fit', icon: MinusCircle },
  { key: 'draft_ready', label: 'Draft Ready', icon: PenNib },
  { key: 'pending_approval', label: 'Awaiting Approval', icon: Hourglass },
  { key: 'approved', label: 'Approved', icon: CheckCircle },
  { key: 'sent', label: 'Sent', icon: PaperPlaneTilt },
  { key: 'replied', label: 'Replied', icon: ChatCircleDots },
]

function EmptyState({ onRun, running }: { onRun?: () => void; running?: boolean }) {
  return (
    <div
      style={{
        border: '1px dashed var(--border-strong)',
        borderRadius: 'var(--radius-lg)',
        padding: '56px 32px',
        textAlign: 'center',
        background: 'var(--surface)',
      }}
    >
      <div
        style={{
          width: 52,
          height: 52,
          borderRadius: 14,
          background: 'var(--bg-2)',
          border: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
        }}
      >
        <Target size={24} weight="duotone" color="#1c1917" />
      </div>
      <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>
        Your pipeline is empty
      </div>
      <div
        style={{
          fontSize: 13.5,
          color: 'var(--text-dim)',
          maxWidth: 380,
          margin: '0 auto 22px',
          lineHeight: 1.6,
        }}
      >
        Hit run and watch five agents discover companies, research them, and draft your
        outreach in real time.
      </div>
      {onRun && (
        <button onClick={onRun} disabled={running} className="btn-primary">
          <Play size={15} weight="fill" />
          {running ? 'Hunting…' : 'Run the hunt'}
        </button>
      )}
    </div>
  )
}

const STATUS_MAP: Record<string, string[]> = {
  discovered: ['discovered', 'researching'],
  researched: ['researched', 'drafting'],
  approved: ['approved', 'delivering'],
  skipped: ['skipped_low_fit', 'skipped_by_user'],
}

export default function PipelineBoard({
  companies,
  onRun,
  running,
  onRefresh,
}: {
  companies: Company[]
  onRun?: () => void
  running?: boolean
  onRefresh?: () => void
}) {
  const byStatus = (columnKey: string) => {
    const statuses = STATUS_MAP[columnKey] || [columnKey]
    return companies.filter((c) => statuses.includes(c.status))
  }
  const active = COLUMNS.filter((col) => byStatus(col.key).length > 0)

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 9,
          marginBottom: 18,
        }}
      >
        <h2 style={{ fontSize: 15, fontWeight: 700, letterSpacing: '-0.01em' }}>Pipeline</h2>
        <span
          style={{
            fontSize: 11.5,
            fontWeight: 600,
            color: 'var(--muted)',
            background: 'var(--surface-2)',
            border: '1px solid var(--border)',
            borderRadius: 999,
            padding: '2px 9px',
          }}
        >
          {companies.length}
        </span>
      </div>

      {companies.length === 0 ? (
        <EmptyState onRun={onRun} running={running} />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 26 }}>
          {active.map((col) => {
            const items = byStatus(col.key)
            const Ico = col.icon
            return (
              <section key={col.key} className="fade-up">
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 9,
                    marginBottom: 12,
                  }}
                >
                  <Ico size={14} weight="bold" color="#57534e" />
                  <span
                    style={{
                      fontSize: 11.5,
                      letterSpacing: '0.06em',
                      textTransform: 'uppercase',
                      fontWeight: 700,
                      color: 'var(--text-dim)',
                    }}
                  >
                    {col.label}
                  </span>
                  <span style={{ fontSize: 11, color: 'var(--muted)', fontWeight: 600 }}>
                    {items.length}
                  </span>
                  <div className="hairline" style={{ flex: 1 }} />
                </div>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                    gap: 10,
                  }}
                >
                  {items.map((c) => (
                    <CompanyCard key={c.id} company={c} onRerun={onRefresh} />
                  ))}
                </div>
              </section>
            )
          })}
        </div>
      )}
    </div>
  )
}
