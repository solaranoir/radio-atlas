# Radio Atlas research note
## HF link validation and ionospheric profile sensitivity

**Source brief** — October 23, 2026  
**Status** — Proposed roadmap additions for the Propagation Experiment Framework

Add a bounded B0/B1 sensitivity experiment as **Story 6.18** and extend **Story 6.17** with one reproducible HF link-budget benchmark. Follow with residual diagnostics and a historical storm replay once the baseline and evidence pipeline can be replayed reliably.

## Proposed roadmap items

| Priority | Work item | Deliverable and acceptance criteria |
| --- | --- | --- |
| P1 | **6.17 follow-up — Reproduce one published HF link budget** | Select a Weber et al. case with documented inputs. Capture antenna assumptions, receiver bandwidth, signal and noise units, and the paper’s P.372-17 version. Reproduce a published link-budget output to a declared tolerance justified by source precision, or document the missing inputs and the resulting discrepancy. Store geometry, estimated signal/noise and observation evidence as distinct outputs. |
| P1 | **6.18 — Ionospheric profile sensitivity and uncertainty evaluation** | Replay one fixed path across selected times and frequencies with the original IRI profile and controlled B0/B1 variants. Deliver a run manifest and paired comparison of reachability, hop count, takeoff angle and closest receiver approach. Report where variants change the result and where results are stable. |
| P2 | **Model comparison — Add spatial and temporal residual diagnostics** | Use the same replay windows and observation eligibility rules across models. Report coverage and denominators by distance, bearing, geomagnetic latitude and local day/night. Where timestamped evidence supports it, report onset lag, duration error and geographic extent separately. Mark sparse or unevaluable bins explicitly. |
| P2 | **Historical validation — Build a May 2024 storm replay fixture** | Start with May 9 as the quiet reference and May 10–11 UTC as the event window. Preserve original timestamps and ionosonde quality flags. Compare foF2 and hmF2 timing at available equatorial South American stations. Add matched HF observations only where a historical corpus is available and record coverage gaps. |

## Story 6.18 experiment design

1. **Freeze the baseline.** Version the IRI configuration, solar and geomagnetic inputs, electron-density grid, PyRayHF build and solver settings, launch-angle grid, and receiver hit tolerance. Start with one path and include at least one frequency near a modeled reachability transition.
2. **Build controlled variants.** Treat B0 as bottomside thickness in km and B1 as a dimensionless shape parameter. Verify how the chosen IRI integration exposes them. Vary each individually, then run a small paired sweep using physically plausible bounds informed by ionosonde profiles or the published parameter analysis. Record the bounds and rationale. Keep foF2, hmF2 and the topside profile fixed by design, and check profile continuity, density validity and preservation of the F2 peak.
3. **Run paired traces.** Hold the path, frequency, timestamp and tracing configuration fixed within each comparison. Verify that a zero perturbation reproduces the baseline within declared numerical tolerances. Record solver failures separately from modeled misses. Recheck borderline hits with a finer launch grid or a documented tolerance sensitivity check.
4. **Compare with reception evidence.** Positive FT8 spots can corroborate reception. Treat missing spots as unknown unless independent transmitter and receiver evidence establishes a valid observation opportunity. Use eligible non-detections only for detectability analysis and report counts and coverage. Keep geometric reachability, detectability and observed reception in separate fields.
5. **Publish the result.** Archive a manifest with profile inputs and versions, the run configuration, raw observation references and paired outputs. Report reachability flips and geometry changes by frequency and time, with case counts. If sensitivity is concentrated near the transition, expand that cohort first. Any later profile-fitting experiment should use independent observations and a held-out evaluation corpus.

Story 6.18 depends on replayable IRI/PyRayHF runs and a pinned baseline. The 6.17 benchmark can proceed in parallel. PSK Reporter data availability affects reception comparisons, while the controlled geometry sweep can run independently.

## Articles for the Radio Atlas research folder

Index the papers by DOI or arXiv ID and record the story each supports. For any PDF stored in the repository, use a version whose license permits redistribution and retain the attribution and license.

| Add | Article | Why it belongs |
| --- | --- | --- |
| Now | [Weber et al. (2026), Wideband HF Skywave Propagation](https://arxiv.org/abs/2609.05811) | Story 6.17. Provides a link-budget reproduction candidate and an example of using FT8 and ionosondes to corroborate modeled maximum usable frequency. The linked author version identifies the article as CC BY 4.0. |
| Now | [Wang, Zhu and Li (2026), Optimization Algorithms for Retrieving the Bottomside Ionospheric B0 and B1 Parameters](https://doi.org/10.1029/2026RS008718) | Story 6.18. Defines the profile parameters and provides an empirical basis for choosing and documenting perturbations. |
| Supporting | [Nwankwo-Omoloja et al. (2026), GITM–TIDAS Comparison With Millstone Hill ISR Measurements](https://doi.org/10.1029/2026JA035273) | Model comparison. Informs diagnostics for localized structure, temporal smoothing and nighttime behavior. |
| Supporting | [Santos et al. (2026), Equatorial F-Region Responses to the 10 May 2024 Geomagnetic Storm](https://doi.org/10.1029/2026JA035071) | Historical replay. Provides the event timeline, reference day, station measurements and data-quality context. |

## SolaraSignal follow-ups

- **P1 — SDR capture pilot.** Run a small scenario-driven capture across a few modulation families and receiver settings. Package captures with SigMF metadata and hold out entire recording sessions for evaluation. [Joly, Cardoso and Gorce, CorteXforge](https://arxiv.org/abs/2610.26999)
- **P2 — Lightweight classification benchmark.** Compare spectrogram dispersion-entropy features with a CNN on the same session splits and report scores by SNR and class. Treat the published wireless-technology results as motivation for a separate HF test. [Alhellani et al., Entropy-Based Wireless Technology Recognition](https://arxiv.org/abs/2610.23158)
