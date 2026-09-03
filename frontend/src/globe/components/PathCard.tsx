import type { SignalPath } from "../types/signalPath";

interface PathCardProps {
  path: SignalPath;
}

export function PathCard({
  path,
}: PathCardProps) {
  return (
    <article className="info-card">
      <div className="info-card__eyebrow">
        Signal path
      </div>

      <h3 className="info-card__title">
        Propagation route
      </h3>

      <dl className="info-card__details">
        <div>
          <dt>Strength</dt>
          <dd>
            {Math.round(path.strength * 100)}%
          </dd>
        </div>

        <div>
          <dt>Source</dt>
          <dd>
            {path.source.latitude.toFixed(2)},{" "}
            {path.source.longitude.toFixed(2)}
          </dd>
        </div>

        <div>
          <dt>Target</dt>
          <dd>
            {path.target.latitude.toFixed(2)},{" "}
            {path.target.longitude.toFixed(2)}
          </dd>
        </div>
      </dl>
    </article>
  );
}
