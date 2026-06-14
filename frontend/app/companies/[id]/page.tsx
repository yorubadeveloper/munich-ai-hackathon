import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Target, Buildings } from '@phosphor-icons/react'
import StatusBadge from '@/components/StatusBadge'
import { getCompanyDossier } from '@/lib/api'
import ResourceChart from '@/components/ResourceChart'
import ApprovalActions from '@/components/ApprovalActions'
import OptionalVisualDossier from '@/components/OptionalVisualDossier'

type PageProps = {
  params: { id: string }
}

export default async function CompanyDossierPage({ params }: PageProps) {
  const dossier = await getCompanyDossier(params.id)

  if (!dossier) {
    notFound()
  }

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: 'var(--bg)',
      }}
    >
      <header
        style={{
          flexShrink: 0,
          zIndex: 20,
          height: 60,
          padding: '0 26px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(250,250,249,0.82)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Link
            href="/dashboard"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              color: 'var(--muted)',
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            <ArrowLeft size={15} weight="bold" />
            Back
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 16 }}>
            <Target size={18} weight="fill" color="#1c1917" />
            <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: '-0.02em' }}>
              Dossier
            </span>
          </div>
        </div>
      </header>

      <main
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '40px 26px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div style={{ width: '100%', maxWidth: 960, display: 'flex', flexDirection: 'column', gap: 32 }}>
          {/* Header Summary Section */}
          <section
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px 32px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
              <div>
                <h1 style={{ fontSize: 24, fontWeight: 800, margin: '0 0 8px 0', letterSpacing: '-0.02em' }}>
                  {dossier.name}
                </h1>
                <div style={{ display: 'flex', gap: 12, color: 'var(--muted)', fontSize: 14 }}>
                  {dossier.website && (
                    <a href={dossier.website} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <Buildings size={16} />
                      Website
                    </a>
                  )}
                  {dossier.job_url && (
                    <a href={dossier.job_url} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      Job Post
                    </a>
                  )}
                </div>
              </div>
              <StatusBadge status={dossier.status} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 24 }}>
                {dossier.fit_score != null && (
                  <div>
                    <div style={{ fontSize: 12, color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Fit Score</div>
                    <div style={{ fontSize: 18, fontWeight: 700 }}>{dossier.fit_score.toFixed(1)} / 10</div>
                  </div>
                )}
                {dossier.funding_stage && (
                  <div>
                    <div style={{ fontSize: 12, color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Funding</div>
                    <div style={{ fontSize: 16, fontWeight: 500 }}>{dossier.funding_stage}</div>
                  </div>
                )}
                {dossier.hiring_manager && (
                  <div>
                    <div style={{ fontSize: 12, color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Hiring Manager</div>
                    <div style={{ fontSize: 16, fontWeight: 500 }}>
                      {dossier.hiring_manager}
                      {dossier.hiring_manager_role && <span style={{ color: 'var(--muted)' }}> · {dossier.hiring_manager_role}</span>}
                    </div>
                  </div>
                )}
            </div>
            {dossier.tech_stack && dossier.tech_stack.length > 0 && (
              <div style={{ marginTop: 24 }}>
                <div style={{ fontSize: 12, color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 8 }}>Tech Stack</div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {dossier.tech_stack.map(tech => (
                    <span key={tech} className="tag">{tech}</span>
                  ))}
                </div>
              </div>
            )}
          </section>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 32 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
              {/* Fit Reasoning Section */}
              {dossier.fit_reasoning && (
                <section>
                  <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Gemini Fit Reasoning</h2>
                  <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '20px', fontSize: 14, lineHeight: 1.6, color: 'var(--ink)' }}>
                    {dossier.fit_reasoning}
                  </div>
                </section>
              )}

              {/* Outreach Hook Section */}
              {dossier.outreach_hook && (
                <section>
                  <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Outreach Hook Draft</h2>
                  <div style={{ background: 'var(--bg-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '20px', fontSize: 14, lineHeight: 1.6, color: 'var(--ink)' }}>
                    {dossier.outreach_hook}
                  </div>
                </section>
              )}

              {/* Evidence Events Sections */}
              {dossier.evidence_events && dossier.evidence_events.length > 0 && (
                <section>
                  <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Evidence Trail</h2>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {dossier.evidence_events.map(event => (
                      <div key={event.id} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '16px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <span style={{ fontWeight: 600, fontSize: 14 }}>{event.resource_name}</span>
                            <span style={{ fontSize: 12, color: 'var(--muted)', background: 'var(--bg-2)', padding: '2px 6px', borderRadius: 4 }}>{event.artifact_type}</span>
                          </div>
                          <span style={{ fontSize: 12, color: 'var(--muted)' }}>{new Date(event.timestamp).toLocaleString()}</span>
                        </div>
                        {event.status !== 'success' && (
                           <div style={{ fontSize: 12, color: 'var(--red, #ef4444)', marginBottom: 8, fontWeight: 500 }}>
                              Status: {event.status}
                           </div>
                        )}
                        <pre style={{ margin: 0, fontSize: 12, background: 'var(--bg)', padding: '12px', borderRadius: 'var(--radius)', overflowX: 'auto', color: 'var(--text-dim)' }}>
                          {JSON.stringify(event.payload, null, 2)}
                        </pre>
                        {event.error_context && (
                           <pre style={{ marginTop: 8, margin: 0, fontSize: 12, background: 'rgba(239,68,68,0.1)', padding: '12px', borderRadius: 'var(--radius)', overflowX: 'auto', color: 'var(--red, #ef4444)' }}>
                             {JSON.stringify(event.error_context, null, 2)}
                           </pre>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
               {/* Approval State Section */}
               <section>
                  <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Approval State</h2>
                  <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                       <div style={{
                         width: 12, height: 12, borderRadius: '50%',
                         background: dossier.approval_state.status === 'approved' ? '#22c55e' : dossier.approval_state.status === 'rejected' ? '#ef4444' : '#eab308'
                       }} />
                       <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{dossier.approval_state.status}</span>
                    </div>
                    {dossier.approval_state.comment && (
                      <div style={{ fontSize: 13, color: 'var(--text-dim)', fontStyle: 'italic', marginBottom: 8 }}>
                        &quot;{dossier.approval_state.comment}&quot;
                      </div>
                    )}
                    {dossier.approval_state.updated_at && (
                      <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                        Updated: {new Date(dossier.approval_state.updated_at).toLocaleString()}
                      </div>
                    )}
                    <ApprovalActions companyId={dossier.id} approvalState={dossier.approval_state} />
                  </div>
               </section>

               {/* Optional Visual Dossier Section */}
               <OptionalVisualDossier events={dossier.evidence_events} />

               {/* Placeholders for visual charts */}
               <section>
                 <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Resource Analysis</h2>
                 <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '20px' }}>
                   {dossier.evidence_events && dossier.evidence_events.some(e => e.artifact_type === 'entity_extraction' || e.artifact_type === 'reasoning') ? (
                     <ResourceChart events={dossier.evidence_events} />
                   ) : (
                     <div style={{ fontSize: 13, color: 'var(--muted)', textAlign: 'center', padding: '40px 0' }}>
                       No structured resource data available yet.
                     </div>
                   )}
                 </div>
               </section>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
