'use client'
import { useEffect, useRef, useState } from 'react'
import {
  MagnifyingGlass,
  PenNib,
  PaperPlaneTilt,
  ChatCircleDots,
  Icon,
} from '@phosphor-icons/react'
import type { Company } from '@/lib/api'

function useCountUp(target: number, duration = 650) {
  const [value, setValue] = useState(0)
  const prev = useRef(0)

  useEffect(() => {
    const from = prev.current
    const to = target
    if (from === to) return
    const start = performance.now()
    let raf = 0
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setValue(Math.round(from + (to - from) * eased))
      if (t < 1) raf = requestAnimationFrame(tick)
      else prev.current = to
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target, duration])

  return value
}

function Stat({ label, value, icon: Ico }: { label: string; value: number; icon: Icon }) {
  const display = useCountUp(value)
  return (
    <div
      style={{
        flex: 1,
        minWidth: 0,
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '16px 18px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <Ico size={15} weight="duotone" color="#78716c" />
        <span
          style={{
            fontSize: 10.5,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: 'var(--muted)',
            fontWeight: 700,
          }}
        >
          {label}
        </span>
      </div>
      <div
        style={{
          fontSize: 28,
          fontWeight: 700,
          lineHeight: 1,
          letterSpacing: '-0.02em',
          color: value > 0 ? 'var(--ink)' : 'var(--faint)',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {display}
      </div>
    </div>
  )
}

export default function StatBar({ companies }: { companies: Company[] }) {
  const count = (statuses: string[]) =>
    companies.filter((c) => statuses.includes(c.status)).length

  const found = companies.length
  const drafted = count(['draft_ready', 'pending_approval', 'approved', 'sent', 'replied'])
  const sent = count(['sent', 'replied'])
  const replied = count(['replied'])

  return (
    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
      <Stat label="Discovered" value={found} icon={MagnifyingGlass} />
      <Stat label="Drafted" value={drafted} icon={PenNib} />
      <Stat label="Sent" value={sent} icon={PaperPlaneTilt} />
      <Stat label="Replies" value={replied} icon={ChatCircleDots} />
    </div>
  )
}
