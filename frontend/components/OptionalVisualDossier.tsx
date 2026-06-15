'use client'

import { EvidenceEvent } from '@/lib/api'

type OptionalVisualDossierProps = {
  events: EvidenceEvent[]
}

export default function OptionalVisualDossier({ events }: OptionalVisualDossierProps) {
  if (!events) return null

  // Find fal visual_artifact event
  const falEvent = events.find(
    (e) => e.resource_name === 'fal' && e.artifact_type === 'visual_artifact'
  )

  if (!falEvent) {
    return null
  }

  const promptText = (falEvent.payload?.prompt as string) || ''
  const imageUrl = (falEvent.payload?.image_url as string) || ''
  const errorMsg =
    (falEvent.payload?.error as string) ||
    (falEvent.error_context?.error as string) ||
    (falEvent.error_context?.message as string) ||
    (falEvent.error_context?.reason as string) ||
    ''

  if (falEvent.status === 'success' && imageUrl) {
    return (
      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Visual AI Dossier</h2>
        <div
          style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: 16,
          }}
        >
          <div
            style={{
              position: 'relative',
              width: '100%',
              aspectRatio: '16/9',
              borderRadius: 'var(--radius)',
              overflow: 'hidden',
              background: 'var(--bg-2)',
              border: '1px solid var(--border)',
            }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt="Visual AI Dossier Artifact"
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
          </div>
          {promptText && (
            <div style={{ fontSize: 13, color: 'var(--text-dim)', fontStyle: 'italic', lineHeight: 1.5 }}>
              &quot;{promptText}&quot;
            </div>
          )}
        </div>
      </section>
    )
  }

  // If error status or missing imageUrl
  return (
    <section style={{ marginBottom: 32 }}>
      <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Visual AI Dossier</h2>
      <div
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px',
          textAlign: 'center',
          color: 'var(--muted)',
          fontSize: 14,
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 4, color: 'var(--text-dim)' }}>
          Visual artifact unavailable
        </div>
        {errorMsg && (
          <div style={{ fontSize: 12, color: 'var(--faint)', marginTop: 4 }}>
            Reason: {errorMsg}
          </div>
        )}
      </div>
    </section>
  )
}
