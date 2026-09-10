import React from 'react';

const humanize = (value) => String(value || 'unknown').replaceAll('_', ' ');

const DepartmentCard = ({ name, data, icon }) => {
  if (!data) return null;

  const isSuccess = data.status === 'success';
  const displayData = Object.entries(data.data || {}).filter(([, value]) => value !== null && value !== undefined && value !== '');
  const status = humanize(data.status);

  return (
    <article className={`dept-card ${isSuccess ? 'success' : 'error'}`} aria-label={`${name} result`}>
      <div className="dept-header">
        <span className="dept-icon" aria-hidden="true">{icon}</span>
        <h3>{name}</h3>
        <span className={`status-badge ${isSuccess ? 'success' : 'error'}`}>{status}</span>
      </div>

      <div className="dept-content">
        {displayData.length > 0 ? (
          <dl className="data-list">
            {displayData.map(([key, value]) => (
              <div key={key} className="data-row">
                <dt className="data-label">{humanize(key)}</dt>
                <dd className="data-value">{String(value)}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <p className={isSuccess ? 'text-muted' : 'error-text'}>
            {data.error || (isSuccess ? 'No details were returned.' : `Department result: ${status}.`)}
          </p>
        )}
      </div>
      {(data.raw_response || data.source_mapping) && <details className="inspection-panel">
        <summary>How this result was produced</summary>
        <div className="inspection-meta">
          <span><strong>Protocol:</strong> {data.protocol || 'Unknown'}</span>
          <span><strong>Actual duration:</strong> {data.duration_ms ?? 'Not measured'} ms</span>
          <span><strong>Correlation ID:</strong> {data.correlation_id || 'Unavailable'}</span>
          {data.external_job_id && <span><strong>Job ID:</strong> {data.external_job_id}</span>}
          {data.schema_version && <span><strong>Schema:</strong> v{data.schema_version}</span>}
          {data.mapping_version && <span><strong>Approved mapping:</strong> v{data.mapping_version}</span>}
        </div>
        <h4>Captured synthetic source response</h4><pre>{data.raw_response || 'No source payload retained.'}</pre>
        <h4>Protocol adapter mapping</h4><pre>{JSON.stringify(data.source_mapping || {}, null, 2)}</pre>
        <h4>Normalized output</h4><pre>{JSON.stringify(data.normalized_output || data.data || {}, null, 2)}</pre>
        <small className="text-muted">Protocol adaptation is separate from advisory rule evaluation. Payloads are bounded and available only in this synthetic demo.</small>
      </details>}
    </article>
  );
};

const AdvisoryInsights = ({ insights = [] }) => (
  <section className="advisory-section" aria-labelledby="advisory-title">
    <div className="advisory-heading">
      <div>
        <h3 id="advisory-title">Advisory Insights</h3>
        <p className="text-muted text-sm">Deterministic checks across normalized department responses.</p>
      </div>
      <span className="badge badge-neutral">Rule-based</span>
    </div>

    {insights.length === 0 ? (
      <p className="advisory-empty">No advisory issues were detected in the available records.</p>
    ) : (
      <ul className="advisory-list">
        {insights.map((insight) => (
          <li key={insight.rule_id} className={`advisory-item ${insight.severity}`}>
            <span className={`badge badge-${insight.severity}`}>{insight.severity}</span>
            <div>
              <code>{insight.rule_id}</code>
              <p>{insight.message}</p>
            </div>
          </li>
        ))}
      </ul>
    )}

    <p className="advisory-disclaimer">Advisory only — verify with the responsible department before taking action.</p>
  </section>
);

const ResultsView = ({ result, onResume, resumeLoading }) => {
  if (!result) return null;

  const citizen = result.citizen || {};
  const overallStatus = humanize(result.overall_status);
  const departmentResults = [result.identity, result.property, result.municipality, result.tax].filter(Boolean);
  const taxIsPending = ['pending', 'processing', 'pending_external'].includes(result.tax?.status);
  const hasRetryableFailure = departmentResults.some((department) =>
    ['failed', 'error', 'unavailable', 'schema_incompatible'].includes(department.status)
  );

  return (
    <div className="results-container fade-in">
      <div className="results-header">
        <h2>Service Request Status</h2>
        <div className="meta-info">
          {result.request_id && <span><strong>Request ID:</strong> {result.request_id}</span>}
          {result.correlation_id && <span><strong>Correlation ID:</strong> {result.correlation_id}</span>}
          {result.consent_id && <span><strong>Consent ID:</strong> {result.consent_id}</span>}
          {result.policy_decision && <span className="text-xs text-muted"><strong>Policy:</strong> {result.policy_decision}</span>}
          <span className={`badge ${result.overall_status === 'denied' ? 'badge-error' : 'badge-success'} mt-1`}>{overallStatus}</span>
        </div>
      </div>

      <section className="citizen-info" aria-labelledby="citizen-title">
        <h3 id="citizen-title">Citizen Identity</h3>
        <div className="citizen-grid">
          {citizen.citizen_id && <div><strong>ID:</strong> {citizen.citizen_id}</div>}
          {citizen.name && <div><strong>Name:</strong> {citizen.name}</div>}
          {citizen.address && <div className="full-width"><strong>Address:</strong> {citizen.address}</div>}
          {!citizen.citizen_id && !citizen.name && !citizen.address && <p className="text-muted">Citizen details are unavailable.</p>}
        </div>
      </section>

      <AdvisoryInsights insights={result.insights} />
      {(taxIsPending || hasRetryableFailure) && (
        <button className="btn btn-primary" onClick={onResume} disabled={resumeLoading}>
          {resumeLoading
            ? (taxIsPending ? 'Checking job…' : 'Retrying failed department…')
            : (taxIsPending ? `Resume tax job ${result.tax.external_job_id || ''}` : 'Retry failed department')}
        </button>
      )}

      <div className="departments-grid">
        <DepartmentCard name="Identity" data={result.identity} icon="👤" />
        <DepartmentCard name="Property" data={result.property} icon="🏠" />
        <DepartmentCard name="Municipality" data={result.municipality} icon="🏛️" />
        <DepartmentCard name="Tax" data={result.tax} icon="💰" />
      </div>
    </div>
  );
};

export default ResultsView;
