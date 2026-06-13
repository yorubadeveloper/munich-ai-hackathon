'use client'
import {
  Compass,
  MagnifyingGlass,
  Brain,
  PenNib,
  PaperPlaneTilt,
  ArrowsClockwise,
  CircleNotch,
  Icon,
} from '@phosphor-icons/react'

type AgentMeta = { label: string; icon: Icon }

const AGENTS: Record<string, AgentMeta> = {
  orchestrator: { label: 'Orchestrator', icon: Compass },
  discovery_agent: { label: 'Discovery', icon: MagnifyingGlass },
  research_agent: { label: 'Research', icon: Brain },
  outreach_agent: { label: 'Outreach', icon: PenNib },
  delivery_agent: { label: 'Delivery', icon: PaperPlaneTilt },
  followup_agent: { label: 'Follow-up', icon: ArrowsClockwise },
}

function meta(agent: string): AgentMeta {
  return AGENTS[agent] || { label: agent, icon: Compass }
}

function timeAgo(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 5) return 'now'
  if (diff < 60) return `${diff}s`
  if (diff < 3600) return `${Math.floor(diff / 60)}m`
  return `${Math.floor(diff / 3600)}h`
}

export default function ActivityFeed({
  logs,
  running,
}: {
  logs: any[]
  running?: boolean
}) {
  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 18,
        }}
      >
        <span className="eyebrow">Agent activity</span>
        {logs.length > 0 && (
          <span
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 11,
              color: 'var(--muted)',
              fontWeight: 600,
            }}
          >
            <span className="live-dot" />
            live
          </span>
        )}
      </div>

      {running && (
        <div
          className="fade-in"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '11px 13px',
            marginBottom: 16,
            borderRadius: 'var(--radius-sm)',
            background: 'var(--bg-2)',
            border: '1px solid var(--border)',
          }}
        >
          <CircleNotch
            size={15}
            weight="bold"
            color="#1c1917"
            style={{ animation: 'spin 0.7s linear infinite', flexShrink: 0 }}
          />
          <span style={{ fontSize: 12.5, color: 'var(--text-dim)', fontWeight: 500 }}>
            Agents are thinking…
          </span>
        </div>
      )}

      {logs.length === 0 && !running ? (
        <div style={{ fontSize: 13, color: 'var(--muted)', padding: '20px 2px', lineHeight: 1.6 }}>
          No activity yet. Hit <strong style={{ color: 'var(--text-dim)' }}>Run</strong> and
          the agents will narrate every step here.
        </div>
      ) : (
        <div style={{ position: 'relative' }}>
          <div
            style={{
              position: 'absolute',
              left: 13,
              top: 6,
              bottom: 6,
              width: 1,
              background: 'var(--border)',
            }}
          />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {logs.map((l, i) => {
              const m = meta(l.agent)
              const Ico = m.icon
              return (
                <div
                  key={l.id}
                  className="fade-up"
                  style={{
                    display: 'flex',
                    gap: 12,
                    padding: '7px 4px',
                    position: 'relative',
                    animationDelay: `${Math.min(i, 6) * 0.03}s`,
                  }}
                >
                  <div
                    style={{
                      width: 27,
                      height: 27,
                      flexShrink: 0,
                      borderRadius: '50%',
                      background: 'var(--surface)',
                      border: '1px solid var(--border-strong)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      zIndex: 1,
                      boxShadow: '0 0 0 3px var(--surface)',
                    }}
                  >
                    <Ico size={13} weight="duotone" color="#1c1917" />
                  </div>

                  <div style={{ flex: 1, minWidth: 0, paddingTop: 1 }}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 8,
                        marginBottom: 1,
                      }}
                    >
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 700,
                          letterSpacing: '0.05em',
                          textTransform: 'uppercase',
                          color: 'var(--muted)',
                        }}
                      >
                        {m.label}
                      </span>
                      <span style={{ fontSize: 10.5, color: 'var(--faint)', flexShrink: 0 }}>
                        {timeAgo(l.created_at)}
                      </span>
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--ink)', lineHeight: 1.45 }}>
                      {l.action}
                    </div>
                    {l.detail && (
                      <div
                        style={{
                          fontSize: 12,
                          color: 'var(--muted)',
                          marginTop: 2,
                          lineHeight: 1.45,
                        }}
                      >
                        {l.detail}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
