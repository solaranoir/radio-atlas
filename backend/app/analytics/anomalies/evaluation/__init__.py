"""Offline evaluation harness for Story 5.1 anomaly-detection candidates.

The harness compares candidate detectors on historical hourly band rollups
under a strictly causal (no look-ahead) protocol, calibrates each detector to
the same alert budget on a training period, and reports behavior on a later
holdout period. See backend/docs/architecture/Anomaly_Detection.md, section 8.
"""
