export interface RadioObservation {
  id: number;
  provider_id: number;
  sequence_number: number | null;

  sender_callsign: string;
  receiver_callsign: string;

  sender_grid: string | null;
  receiver_grid: string | null;

  frequency_hz: number | null;
  band: string | null;
  mode: string;

  snr_db: number | null;

  observed_at: string;
  transmitted_at: string | null;
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000";

export async function fetchObservations(
  limit = 100,
): Promise<RadioObservation[]> {
  const url =
    new URL(
      "/api/v1/observations",
      API_BASE_URL,
    );

  url.searchParams.set(
    "limit",
    String(limit),
  );

  const response =
    await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Failed to fetch observations: ${response.status}`,
    );
  }

  return response.json() as Promise<
    RadioObservation[]
  >;
}
