'use client'

import dynamic from 'next/dynamic'
import { EvidenceEvent } from '@/lib/api'

const ResourceChartInner = dynamic(
  () => import('./ResourceChartInner'),
  { ssr: false, loading: () => <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>Loading chart...</div> }
)

export default function ResourceChart({ events }: { events: EvidenceEvent[] }) {
  return <ResourceChartInner events={events} />
}
