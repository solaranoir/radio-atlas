# 13. Wireframes

## 13.1 Wireframe Purpose

The Radio Atlas interface should make complex radio data feel immediate, dynamic, and explorable.

Wireframes should prioritize:

* The globe as the primary visual surface
* Minimal obstruction of geographic data
* Fast access to filters and layers
* Clear separation between **observation**, **prediction**, and **AI interpretation**
* Progressive disclosure of technical information
* Strong visual hierarchy
* Responsive behavior across desktop, tablet, and mobile devices

The initial wireframes are conceptual.

They define **interaction patterns and information architecture rather than final visual styling.** :contentReference[oaicite:1]{index=1}

---

## 13.2 Primary Desktop Experience

The default desktop experience shall function as the application's **command center and observatory.**

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ SOLARASPHERE: RADIO ATLAS          LIVE ●          Search         Profile    │
├───────────────────┬───────────────────────────────────┬─────────────────────┤
│                   │                                   │                     │
│ LAYERS            │                                   │ CURRENT CONDITIONS  │
│                   │                                   │                     │
│ ☑ Signal Paths    │                                   │ Solar Flux     184  │
│ ☑ Gray Line       │                                   │ Kp Index         2  │
│ ☐ Aurora          │                                   │ MUF         26 MHz  │
│ ☑ Anomalies       │       RADIO WEATHER GLOBE         │                     │
│ ☑ Personal QSOs   │                                   ├─────────────────────┤
│                   │                                   │                     │
│ FILTERS           │                                   │ FORECAST            │
│                   │                                   │                     │
│ Band: 20m         │                                   │ 20m █████████ 93%   │
│ Mode: FT8         │                                   │ 17m ████████ 81%    │
│ Window: 15 min    │                                   │ 15m █████ 58%       │
│                   │                                   │                     │
│ [Reset Filters]   │                                   │ Europe +38 minutes  │
│                   │                                   │                     │
├───────────────────┴───────────────────────────────────┴─────────────────────┤
│ ◀◀   ▶   ▶▶        18:00 ━━━━━━━●━━━━━━━━ 22:00       LIVE                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Primary Actions

Users shall be able to:

* Rotate and zoom the globe
* Select signal paths
* Toggle layers
* Filter activity
* View current conditions
* View predicted openings
* Enter Replay Mode
* Search for callsigns, grids, or entities

The globe should remain the dominant visual element at all times. :contentReference[oaicite:2]{index=2}

---

## 13.3 QSO Story Experience

Selecting a signal path or contact shall open a **contextual slide-out panel** rather than replacing the globe.

The panel shall preserve visual context.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                            RADIO WEATHER GLOBE                               │
│                                                                              │
│         KK7QEA ●──────────────────────────────● JA1ABC                       │
│                                                                              │
│                                          ┌──────────────────────────────┐    │
│                                          │ QSO STORY                    │    │
│                                          ├──────────────────────────────┤    │
│                                          │ 20m • FT8 • 5,200 miles      │    │
│                                          │ 19:42 local                  │    │
│                                          ├──────────────────────────────┤    │
│                                          │ OBSERVED EVIDENCE            │    │
│                                          │ SFI: 184                     │    │
│                                          │ Kp: 2                        │    │
│                                          │ Path rarity: Top 3%          │    │
│                                          ├──────────────────────────────┤    │
│                                          │ AI INTERPRETATION            │    │
│                                          │ Your signal crossed the      │    │
│                                          │ Pacific gray line during a   │    │
│                                          │ favorable 20m opening...     │    │
│                                          ├──────────────────────────────┤    │
│                                          │ [Beginner] [Technical]       │    │
│                                          │ [View Similar Contacts]      │    │
│                                          └──────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Requirements

The panel shall:

* Preserve the globe context
* Highlight the selected path
* Present objective facts separately from AI interpretation
* Present evidence before conclusions
* Support multiple explanation levels
* Provide access to similar historical contacts

This interaction model replaces the original "AI card" approach and aligns with the post-analysis emphasis on **evidence-grounded explanations.** :contentReference[oaicite:3]{index=3}

---

## 13.4 Radio Forecast Workspace

The forecast experience shall evolve from a simple widget into a dedicated analytical workspace.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ RADIO FORECAST                                                Next 3 Hours   │
├──────────────────────────────┬───────────────────────────────────────────────┤
│ BAND OUTLOOK                 │                                               │
│                              │            PREDICTED PROPAGATION MAP          │
│ 20m  █████████████ 93%       │                                               │
│ 17m  ███████████  81%        │                Europe         Japan           │
│ 15m  ████████     58%        │                   ○              ○            │
│ 12m  ████         31%        │                                               │
│ 10m  ██           18%        │                  North America                │
│                              │                       ●                       │
│ Best opportunity             │                                               │
│ Europe                       │         Dashed arcs indicate predictions      │
│ 38 to 72 minutes             │                                               │
├──────────────────────────────┴───────────────────────────────────────────────┤
│ NOW      +30m      +60m      +90m      +120m      +180m                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Requirements

The forecast workspace shall:

* Rank bands
* Display confidence values
* Show forecast changes over time
* Visualize likely geographic openings
* Clearly distinguish forecasts from live observations

Predicted paths shall always be visually distinguishable from observed paths. :contentReference[oaicite:4]{index=4}

---

## 13.5 Propagation Time Machine

Replay Mode shall function as a **scientific reconstruction tool rather than a media player.**

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ PROPAGATION REPLAY                          Aug 14, 2026 • 18:42 UTC         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                           RADIO WEATHER GLOBE                               │
│                                                                              │
│                    Signal activity morphs over time                         │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ ◀◀  ◀  ▶  ▶▶      Speed: [1x] [2x] [5x] [10x]                               │
│                                                                              │
│ 00:00 ━━━━━━━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 24:00               │
│                              ▲                                               │
│                         Current Frame                                        │
│                                                                              │
│ ☑ Spots  ☑ Gray Line  ☑ Solar Conditions  ☑ Anomalies                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Requirements

Replay Mode shall:

* Display timestamps prominently
* Prevent confusion between live and historical data
* Support timeline scrubbing
* Support variable playback speeds
* Synchronize all enabled overlays

Replay is now considered a **primary differentiator** rather than a supporting feature. :contentReference[oaicite:5]{index=5}

---

## 13.6 Contact Intelligence and Rare Contact Discovery

Rare Contact Discovery shall become part of the **QSO Story ecosystem rather than an independent dashboard.**

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ CONTACT INTELLIGENCE                                                         │
├─────────────────────────────┬────────────────────────────────────────────────┤
│ ACHIEVEMENTS                │ UNUSUAL CONTACTS                               │
│                             │                                                │
│ 🏆 Longest Path             │ JA1ABC     5,200 mi     Top 3% rarity         │
│ 🏆 Gray Line Hunter         │ ZS6XYZ     9,100 mi     Long-path candidate   │
│ 🏆 Midnight DX              │ VK4ABC     New grid     First contact         │
│ 🏆 Rare Grid Explorer       │                                                │
│                             │ [View on Globe]                               │
└─────────────────────────────┴────────────────────────────────────────────────┘
```

Anomaly detection should eventually be incorporated into this panel. :contentReference[oaicite:6]{index=6}

---

## 13.7 Mobile Wireframe

```text
┌──────────────────────────────┐
│ RADIO ATLAS          ☰    ●  │
├──────────────────────────────┤
│                              │
│         RADIO WEATHER        │
│            GLOBE             │
│                              │
├──────────────────────────────┤
│ 20m • FT8 • LIVE             │
│ [Layers] [Filters] [Replay]  │
├──────────────────────────────┤
│ RADIO FORECAST               │
│ 20m █████████ 93%            │
│ 17m ████████ 81%             │
├──────────────────────────────┤
│ CURRENT CONDITIONS           │
│ SFI 184   Kp 2               │
└──────────────────────────────┘
```

Mobile devices should favor:

* Touch interaction
* Bottom-sheet panels
* Collapsible controls

Persistent sidebars should be avoided. :contentReference[oaicite:7]{index=7}
