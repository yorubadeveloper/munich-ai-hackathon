'use client'

import {
  MagnifyingGlass,
  Brain,
  PenNib,
  Hourglass,
  CheckCircle,
  PaperPlaneTilt,
  ChatCircleDots,
  MinusCircle,
  Icon,
} from '@phosphor-icons/react'

type Conf = { label: string; icon: Icon; strong?: boolean }

const STATUS: Record<string, Conf> = {
  discovered: { label: 'Discovered', icon: MagnifyingGlass },
  researching: { label: 'Researching…', icon: Brain, strong: true },
  researched: { label: 'Researched', icon: Brain },
  drafting: { label: 'Drafting…', icon: PenNib, strong: true },
  draft_ready: { label: 'Draft ready', icon: PenNib },
  pending_approval: { label: 'Awaiting you', icon: Hourglass, strong: true },
  approved: { label: 'Approved', icon: CheckCircle },
  delivering: { label: 'Sending…', icon: PaperPlaneTilt, strong: true },
  sent: { label: 'Sent', icon: PaperPlaneTilt, strong: true },
  replied: { label: 'Replied', icon: ChatCircleDots, strong: true },
  skipped_low_fit: { label: 'Low fit', icon: MinusCircle },
  skipped_by_user: { label: 'Skipped', icon: MinusCircle },
}

export default function StatusBadge({ status }: { status: string }) {
  const conf = STATUS[status] || { label: status, icon: MinusCircle }
  const Ico = conf.icon
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        flexShrink: 0,
        fontSize: 11,
        fontWeight: 600,
        padding: '3px 9px',
        borderRadius: 999,
        background: conf.strong ? 'var(--ink)' : 'var(--surface-2)',
        color: conf.strong ? '#fff' : 'var(--text-dim)',
        border: `1px solid ${conf.strong ? 'var(--ink)' : 'var(--border)'}`,
      }}
    >
      <Ico size={11} weight="bold" />
      {conf.label}
    </span>
  )
}
