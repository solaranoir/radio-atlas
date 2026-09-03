interface SummaryCardProps {
  observationCount: number;
  anomalyCount: number;
}

export function SummaryCard({
  observationCount,
  anomalyCount,
}: SummaryCardProps) {
  return (
    <article className="info-card">
      <div className="info-card__eyebrow">
        Current view
      </div>

      <dl className="info-card__details">
        <div>
          <dt>Observations</dt>
          <dd>{observationCount}</dd>
        </div>

        <div>
          <dt>Anomalies</dt>
          <dd>{anomalyCount}</dd>
        </div>
      </dl>
    </article>
  );
}
