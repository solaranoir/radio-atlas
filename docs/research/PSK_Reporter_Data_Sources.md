# PSK Reporter Data Sources

## Purpose

This document records the PSK Reporter data retrieval research performed
for Radio Atlas Phase 1, Story 4.1.

The objective is to identify a reliable retrieval strategy for
near-real-time amateur radio reception reports.

## Candidate Interfaces

### HTTP Query API

Endpoint:

`https://retrieve.pskreporter.info/query`

Format:

XML

Supports filtering by callsign, mode, frequency range, time window, and
sequence number.

PSK Reporter recommends retrieving reception data no more frequently
than once every five minutes.

Live testing confirmed that the `mode` query parameter can be used to
filter reception reports by mode. A query using `mode=FT8` returned FT8
reception reports.

Testing with `rptlimit=5` did not restrict the response to five
`receptionReport` elements. The semantics of `rptlimit` therefore
require additional investigation and should not currently be relied upon
as a conventional result-count limit.

### MQTT Feed

Broker:

`mqtt.pskreporter.info`

Message format:

JSON

Filter topic:

`pskr/filter/v2/{band}/{mode}/{tx}/{rx}/{tx_grid}/{rx_grid}/{tx_dxcc}/{rx_dxcc}`

Provides live individual reception reports.

Live payload investigation has been completed. A bounded 20-meter FT8
subscription returned individual JSON reception reports successfully.

## Phase 1 Selection

**Decision: use the MQTT feed as the primary Phase 1 PSK Reporter
ingestion interface.**

Live investigation validated both the HTTP Query API and MQTT feed. MQTT
is the better primary path because it provides near-real-time push
delivery, one report per JSON message, explicit band and mode, and a
per-report sequence number.

The HTTP Query API remains a documented secondary interface for
querying, troubleshooting, and potential future gap recovery or backfill
using `lastseqno`.

This decision also changes the original roadmap assumption of polling
PSK Reporter every one minute. The Phase 1 provider should instead
maintain a persistent MQTT subscription. HTTP recovery is not required
for the initial provider unless implementation testing demonstrates a
need for it.

## Observed HTTP Response

Live testing confirmed that the HTTP Query API returns XML containing
individual `<receptionReport>` elements.

Observed attributes include:

-   `receiverCallsign`
-   `receiverLocator`
-   `senderCallsign`
-   `senderLocator`
-   `frequency`
-   `flowStartSeconds`
-   `mode`
-   `sNR`
-   `senderDXCC`
-   `senderDXCCCode`
-   `senderDXCCLocator`
-   `senderLotwUpload`
-   `senderEqslAuthGuar`

Not every attribute is present on every reception report.

`frequency` is represented as an integer number of Hz.

`flowStartSeconds` is represented as Unix epoch seconds and must be
converted to a UTC datetime during normalization.

Maidenhead locators vary in precision and casing. Radio Atlas should
therefore normalize locator values rather than assuming a fixed length
or canonical casing.

The response also contains response-level metadata:

-   `lastSequenceNumber`
-   `maxFlowStartSeconds`

These values may be useful for incremental ingestion and determining the
newest report represented by a query.

## Observed Optional Fields

Live responses demonstrate that individual reception reports may omit
attributes.

In particular, `frequency` is not present on every report.

Provider-level models should therefore tolerate missing values where the
upstream API permits them. Validation and filtering required by Radio
Atlas should occur during normalization rather than assuming every PSK
Reporter record is complete.

## Callsign and Locator Variability

Observed callsigns include portable/suffixed callsigns such as `W1AW/7`
as well as SWL identifiers.

Provider models should avoid restrictive callsign validation.

Observed Maidenhead locators vary substantially in precision, including
4-, 6-, 8-, and longer-character representations. Locator values also
vary in casing.

Radio Atlas should normalize Maidenhead locator casing and support
variable valid precision.

## Incremental HTTP Retrieval

PSK Reporter responses include a `lastSequenceNumber` value that can be
used with the `lastseqno` query parameter for subsequent retrieval.

Live testing demonstrated the following behavior:

1.  An initial query returned:

    `lastSequenceNumber = 71868925247`

2.  A subsequent request was issued using:

    `lastseqno=71868925247`

3.  The subsequent response returned newer reception reports and:

    `lastSequenceNumber = 71868942411`

This indicates that `lastseqno` can be used as an incremental ingestion
cursor.

The provider should persist the most recently successfully processed
sequence number and supply it as `lastseqno` on the next polling
request.

The cursor MUST NOT be advanced until the corresponding batch has been
successfully parsed, normalized, and persisted.

This produces an at-least-once ingestion model. The persistence layer
should therefore support idempotent insertion or deduplication of
repeated observations.

`maxFlowStartSeconds` should be retained as useful response metadata and
may be used for observability, lag measurement, and debugging, but
should not be used as the primary ingestion cursor while sequence-based
retrieval is available.

## MQTT Live Feed

### Broker

`mqtt.pskreporter.info`

### Message Format

JSON

Each MQTT message represents one PSK Reporter reception report.

### Topic Structure

`pskr/filter/v2/{band}/{mode}/{tx}/{rx}/{tx_grid}/{rx_grid}/{tx_dxcc}/{rx_dxcc}`

Live testing using a 20-meter FT8 subscription successfully returned
individual reception reports.

### Observed Payload

Example:

``` json
{
  "sq": 71869170759,
  "f": 14075361,
  "md": "FT8",
  "rp": -5,
  "t": 1787168040,
  "t_tx": 1787168025,
  "sc": "EA5JLN",
  "sl": "IM99TN",
  "rc": "DL4JC",
  "rl": "JN39lh",
  "sa": 281,
  "ra": 230,
  "b": "20m"
}


## MQTT Live Feed Findings

### Live Test

A bounded command-line subscription to:

`pskr/filter/v2/20m/FT8/#`

successfully returned individual FT8 reception reports.

Five consecutive reports used sequence numbers:

```text
71869170759
71869170760
71869170761
71869170762
71869170763
```

### Observed Payload

``` json
{
  "sq": 71869170759,
  "f": 14075361,
  "md": "FT8",
  "rp": -5,
  "t": 1787168040,
  "t_tx": 1787168025,
  "sc": "EA5JLN",
  "sl": "IM99TN",
  "rc": "DL4JC",
  "rl": "JN39lh",
  "sa": 281,
  "ra": 230,
  "b": "20m"
}
```

### Working MQTT Field Mapping

The following mapping is based on the live payload investigation.
Abbreviated upstream field semantics should still be checked against the
authoritative MQTT schema during implementation where ambiguity remains.

  -----------------------------------------------------------------------
  MQTT field              Working interpretation  Proposed provider field
  ----------------------- ----------------------- -----------------------
  `sq`                    PSK Reporter sequence   `sequence_number`
                          number                  

  `f`                     frequency in Hz         `frequency_hz`

  `md`                    operating mode          `mode`

  `rp`                    received/report signal  `snr_db`
                          level; observed as      
                          SNR-like dB values      

  `t`                     report/reception        `observed_at`
                          timestamp, Unix epoch   
                          seconds                 

  `t_tx`                  transmission timestamp, `transmitted_at`
                          Unix epoch seconds      

  `sc`                    sender callsign         `sender_callsign`

  `sl`                    sender Maidenhead       `sender_locator`
                          locator                 

  `rc`                    receiver callsign       `receiver_callsign`

  `rl`                    receiver Maidenhead     `receiver_locator`
                          locator                 

  `sa`                    sender entity/DXCC      `sender_entity_id`
                          identifier              

  `ra`                    receiver entity/DXCC    `receiver_entity_id`
                          identifier              

  `b`                     amateur band            `band`
  -----------------------------------------------------------------------

The JSON representation provides native numeric types for sequence
number, frequency, signal report, timestamps, and entity identifiers,
which reduces parsing ambiguity compared with the HTTP XML interface.

### Topic and Payload Responsibilities

The MQTT topic carries useful routing/filter information such as band,
mode, transmitter, receiver, grid prefixes, and entity identifiers.

The JSON payload should remain the provider's primary source for report
data. The implementation should not require reconstructing a report from
topic segments when the payload already contains the relevant values.

### Sequence Numbers

Each observed MQTT report contained its own `sq` sequence number.

The sequence values appear to share the same sequence-number space used
by the HTTP Query API's `lastSequenceNumber` / `lastseqno` mechanism.

This creates a potential future recovery architecture:

``` text
MQTT live stream
      ↓
persist sequence N
      ↓
connection loss
      ↓
HTTP query using lastseqno=N
      ↓
recover missed reports
      ↓
deduplicate / persist
      ↓
continue live MQTT ingestion
```

HTTP recovery is intentionally **not required for the initial Phase 1
provider**. Phase 1 should establish reliable MQTT ingestion and retain
sequence numbers so recovery can be added later without redesigning the
observation contract.

A filtered MQTT subscription must not assume that every globally
consecutive PSK Reporter sequence number will appear on that topic.
Sequence discontinuities should initially be observable rather than
automatically treated as confirmed data loss.

### MQTT Operational Considerations

Story 4.3 should account for:

-   persistent broker connection lifecycle;
-   reconnect after connection loss;
-   resubscription after reconnect;
-   malformed or unexpected JSON without terminating the consumer;
-   independent Pydantic validation of each message;
-   duplicate-message tolerance/idempotency;
-   retention of upstream `sq` for provenance;
-   sequence-discontinuity logging/metrics;
-   bounded buffering or backpressure if downstream processing is slower
    than message arrival;
-   clean shutdown; and
-   avoiding assumptions that every field observed in the five-message
    sample is universally present.

### Subscription Scope

The research subscription was intentionally narrow:

`pskr/filter/v2/20m/FT8/#`

Production subscription scope must be selected deliberately. A broad or
global subscription may produce substantially more traffic than the
research subscription.

Phase 1 should use the narrowest topic or set of topics that satisfies
the product requirements and should measure throughput before
substantially broadening the subscription.

## HTTP vs. MQTT Decision Matrix

  -----------------------------------------------------------------------
  Consideration           HTTP Query API          MQTT Feed
  ----------------------- ----------------------- -----------------------
  Delivery model          Poll/batch              Push/event stream

  Format                  XML                     JSON

  Granularity             Multiple reports per    One report per message
                          response                

  Near-real-time behavior Limited by polling      Native live delivery
                          cadence                 

  Sequence information    Response-level          Per-report `sq`
                          `lastSequenceNumber`    

  Incremental retrieval   `lastseqno`             Live sequence
                                                  progression

  Explicit band           Not relied upon in      Yes, `b`
                          tested payloads         

  Mode                    Yes                     Yes, `md`

  Frequency               Observed as optional    Present in all five
                                                  MQTT samples

  Callsigns               Sender and receiver     Sender and receiver

  Locators                Sender and receiver     Sender and receiver

  Signal report           `sNR` when present      `rp` in all five
                                                  samples

  TX timestamp            Not separately observed `t_tx`

  Report timestamp        `flowStartSeconds`      `t`

  Connection model        Stateless request       Persistent connection

  Recovery/backfill       Strong                  Requires reconnect
                                                  and/or secondary path

  Phase 1 role            Secondary/recovery      **Primary ingestion**
                          candidate               
  -----------------------------------------------------------------------

## Phase 1 Retrieval Strategy

### Primary Path

Use MQTT as the primary PSK Reporter ingestion mechanism:

``` text
PSK Reporter MQTT
        ↓
topic subscription
        ↓
JSON message
        ↓
PSK Reporter provider model
        ↓
validation / normalization
        ↓
ProviderObservation
        ↓
persistence
```

The original roadmap assumption of polling PSK Reporter every one minute
should be replaced with persistent MQTT subscription behavior.

### Secondary / Future Recovery Path

Retain the HTTP Query API as a secondary mechanism.

A future recovery workflow can potentially use the last successfully
persisted MQTT sequence number with HTTP `lastseqno` to retrieve reports
after an interruption. This should be implemented only after its
interaction with production topic filters, deduplication, and
persistence semantics has been tested.

## Provider-Model Implications for Story 4.2

The provider model should represent the upstream MQTT report separately
from normalized/domain representations.

The raw/provider model should include, at minimum:

-   sequence number;
-   sender callsign;
-   receiver callsign;
-   sender locator;
-   receiver locator;
-   frequency in Hz;
-   band;
-   mode;
-   report/reception timestamp;
-   transmission timestamp;
-   signal report/SNR-like value;
-   sender entity identifier; and
-   receiver entity identifier.

Provider validation should be conservative:

-   do not impose a narrow amateur-callsign regex;
-   support variable Maidenhead precision;
-   normalize locator casing separately from raw parsing;
-   convert Unix timestamps to timezone-aware UTC datetimes during
    normalization;
-   preserve the original frequency in Hz;
-   do not assume all fields observed in the small MQTT sample are
    universally mandatory until confirmed; and
-   retain the upstream sequence number for provenance and future
    recovery.

Coordinates required by the roadmap should be **derived from Maidenhead
locators during normalization** rather than expected as native PSK
Reporter latitude/longitude fields, unless later research identifies an
upstream coordinate field that should be preferred.

## Provider-Implementation Implications for Story 4.3

Story 4.3 should no longer be designed as a one-minute HTTP polling
provider.

The implementation should provide:

1.  MQTT connection lifecycle management.
2.  Topic subscription.
3.  JSON decoding.
4.  Pydantic validation.
5.  Conversion to `ProviderObservation`.
6.  Structured logging.
7.  Graceful handling of malformed messages.
8.  Reconnect and resubscription behavior.
9.  Clean shutdown.
10. Sequence-number retention and observability.
11. Unit tests using mocked MQTT messages rather than the public broker.

A separate integration test can validate live broker connectivity
without making the deterministic unit suite dependent on external
infrastructure.

## Open Questions / Follow-Up Research

The following items should be verified before or during Stories 4.2 and
4.3 rather than silently assumed:

1.  Authoritative definitions for abbreviated MQTT fields, especially
    `rp`, `t`, `t_tx`, `sa`, and `ra`.
2.  Which MQTT fields are formally required versus optional.
3.  MQTT QoS and resulting duplicate/loss semantics.
4.  Recommended client identification, keepalive, reconnect, or
    connection-limit behavior.
5.  Whether production should use a TLS-enabled MQTT connection.
6.  Exact production subscription scope: selected bands/modes versus a
    broader feed.
7.  Expected message throughput for the selected subscription.
8.  Whether `sq` is globally sequenced across all reports and how
    filtered subscriptions should interpret gaps.
9.  Retention/age limits for HTTP `lastseqno` recovery.
10. Exact `rptlimit` semantics if HTTP batch limiting is later needed.

These questions do not block the Story 4.1 architectural decision, but
they should be resolved before production code relies on the
corresponding behavior.

## Story 4.1 Outcome

**Primary interface:** MQTT.

**Secondary interface:** HTTP Query API for querying/debugging and
potential future sequence-based gap recovery.

**Roadmap adjustment:** replace planned one-minute PSK Reporter HTTP
polling with persistent MQTT subscription behavior.

**Implementation principle:** preserve upstream sequence numbers and
design ingestion/persistence to tolerate duplicate delivery and future
replay/backfill.

**Next:** Story 4.2 --- Create PSK Reporter Models.
