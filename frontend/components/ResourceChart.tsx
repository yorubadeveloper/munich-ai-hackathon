'use client'

import { useMemo } from 'react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts'
import { EvidenceEvent } from '@/lib/api'

export default function ResourceChart({ events }: { events: EvidenceEvent[] }) {
  const chartData = useMemo(() => {
    let rawLabels: string[] = []

    // Attempt to extract labels from pioneer entity extraction or gemini reasoning
    for (const ev of events) {
      if (ev.status === 'success' && ev.payload) {
        if (ev.artifact_type === 'entity_extraction' && Array.isArray(ev.payload.labels)) {
          rawLabels = rawLabels.concat(ev.payload.labels)
        } else if (ev.artifact_type === 'reasoning' && Array.isArray(ev.payload.labels)) {
          rawLabels = rawLabels.concat(ev.payload.labels)
        }
      }
    }

    if (rawLabels.length === 0) {
      // Provide some fallback demo data if no labels are present in DB to show the chart
      return [
        { label: 'Growth', count: 4 },
        { label: 'Culture', count: 3 },
        { label: 'Tech Stack', count: 5 },
        { label: 'Funding', count: 2 },
        { label: 'Leadership', count: 4 },
      ]
    }

    const counts: Record<string, number> = {}
    for (const label of rawLabels) {
      const l = label.trim().toLowerCase()
      counts[l] = (counts[l] || 0) + 1
    }

    // Capitalize and map for recharts
    return Object.entries(counts).map(([label, count]) => ({
      label: label.charAt(0).toUpperCase() + label.slice(1),
      count,
    }))
  }, [events])

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="var(--border)" />
          <PolarAngleAxis dataKey="label" tick={{ fill: 'var(--muted)', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 'dataMax + 1']} tick={false} axisLine={false} />
          <Radar
            name="Resource Mentions"
            dataKey="count"
            stroke="var(--ink)"
            fill="var(--ink)"
            fillOpacity={0.2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
