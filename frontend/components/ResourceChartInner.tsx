'use client'

import { useMemo } from 'react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts'
import { EvidenceEvent } from '@/lib/api'

export default function ResourceChartInner({ events }: { events: EvidenceEvent[] }) {
  // Check if there is a pioneer_eval event
  const evalEvent = events.find(e => e.artifact_type === 'pioneer_eval' && e.status === 'success')

  const evalData = useMemo(() => {
    if (!evalEvent || !evalEvent.payload) return null
    const payload = evalEvent.payload as Record<string, unknown>
    const pioneerScores = (payload.per_label_f1_pioneer as Record<string, number>) || {}
    const geminiScores = (payload.per_label_f1_gemini as Record<string, number>) || {}

    // Get all unique labels
    const labels = Array.from(new Set([...Object.keys(pioneerScores), ...Object.keys(geminiScores)]))

    return labels.map(label => ({
      name: label,
      Pioneer: pioneerScores[label] || 0,
      Gemini: geminiScores[label] || 0
    }))
  }, [evalEvent])

  const chartData = useMemo(() => {
    if (evalEvent) return [] // skip generic radar parsing if eval event exists

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
  }, [events, evalEvent])

  if (evalEvent && evalData) {
    return (
      <div style={{ width: '100%', height: 300 }}>
        <h3 style={{ textAlign: 'center', marginBottom: 16, fontSize: 14, fontWeight: 600 }}>
          Pioneer vs Gemini Entity Extraction (F1 Score)
        </h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={evalData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
            <XAxis dataKey="name" tick={{ fill: 'var(--muted)', fontSize: 12 }} />
            <YAxis tick={{ fill: 'var(--muted)', fontSize: 12 }} domain={[0, 1]} />
            <Tooltip contentStyle={{ borderRadius: 'var(--radius)', border: '1px solid var(--border)' }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Pioneer" fill="var(--ink)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Gemini" fill="var(--muted)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

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
