import type { Station } from "../types/station";

interface StationCardProps {
  station: Station;
}

export function StationCard({
  station,
}: StationCardProps) {
  return (
    <article className="info-card">
      <div className="info-card__eyebrow">
        Station
      </div>

      <h3 className="info-card__title">
        {station.callsign}
      </h3>

      <dl className="info-card__details">
        <div>
          <dt>Latitude</dt>
          <dd>
            {station.latitude.toFixed(4)}
          </dd>
        </div>

        <div>
          <dt>Longitude</dt>
          <dd>
            {station.longitude.toFixed(4)}
          </dd>
        </div>
      </dl>
    </article>
  );
}
