"""
HSL Intrusion Detection Module - Phase Deviation Monitoring
============================================================

Monitors harmonic phase deviations using the detection criterion:
    Delta_phi(t) = |phi_hat(t) - phi_ref| > epsilon

When the observed phase deviation exceeds the configurable threshold
epsilon, an intrusion alert is raised. Supports sliding-window
analysis and cumulative deviation statistics.

Reference:
    Paper 4 (CC BY 4.0): DOI 10.5281/zenodo.19056387 - HPG 1.0
    Intrusion detection via phase deviation monitoring.

Author: Hubstry Deep Tech (guilhermemachado.ceo@hubstry.dev)
License: CC BY-NC-SA 4.0
"""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np
from numpy.typing import NDArray


class AlertSeverity(Enum):
    """Severity levels for intrusion alerts."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IntrusionAlert:
    """
    Represents a single intrusion detection alert.

    Attributes:
        timestamp: Unix epoch seconds when the alert was raised.
        severity: Alert severity level.
        delta_phi: The phase deviation that triggered the alert.
        epsilon: The threshold that was exceeded.
        node_id: Identifier of the monitored node.
        message: Human-readable alert description.
    """

    timestamp: float
    severity: AlertSeverity
    delta_phi: float
    epsilon: float
    node_id: str
    message: str

    def __repr__(self) -> str:
        return (
            f"IntrusionAlert(t={self.timestamp:.1f}, "
            f"severity={self.severity.value}, "
            f"delta={self.delta_phi:.6f}, "
            f"eps={self.epsilon:.6f}, "
            f"node={self.node_id})"
        )


@dataclass
class DetectionConfig:
    """Configuration for the intrusion detection system."""

    epsilon: float = 0.05
    window_size: int = 64
    high_severity_threshold: float = 0.10
    critical_severity_threshold: float = 0.20
    cooldown_seconds: float = 5.0
    alert_history_size: int = 256


@dataclass
class PhaseObservation:
    """
    A single phase observation event.

    Attributes:
        phi_hat: Observed phase angle in radians.
        phi_ref: Reference (expected) phase angle in radians.
        timestamp: Unix epoch seconds.
        node_id: Identifier of the source node.
    """

    phi_hat: float
    phi_ref: float
    timestamp: float
    node_id: str

    @property
    def delta_phi(self) -> float:
        """
        Compute phase deviation: Delta_phi(t) = |phi_hat(t) - phi_ref|.

        Returns:
            Absolute phase deviation in radians.
        """
        return abs(self.phi_hat - self.phi_ref)


class PhaseMonitor:
    """
    Monitors harmonic phase deviations for intrusion detection.

    Implements the detection criterion from Paper 4:
        Delta_phi(t) = |phi_hat(t) - phi_ref| > epsilon

    Uses a sliding window of recent observations to compute
    running statistics (mean, std, max deviation) for adaptive
    thresholding and trend analysis.

    Attributes:
        config: Detection configuration.
        window: Sliding window of recent PhaseObservations.
        alerts: History of generated alerts.
        _last_alert_time: Cooldown tracker.
    """

    def __init__(self, config: Optional[DetectionConfig] = None) -> None:
        self.config = config or DetectionConfig()
        self.window: deque[PhaseObservation] = deque(
            maxlen=self.config.window_size
        )
        self.alerts: list[IntrusionAlert] = []
        self._last_alert_time: float = 0.0
        self._total_observations: int = 0
        self._total_alerts: int = 0

    def compute_delta_phi(
        self, phi_hat: float, phi_ref: float
    ) -> float:
        """
        Compute the phase deviation Delta_phi.

        Args:
            phi_hat: Observed phase angle in radians.
            phi_ref: Reference phase angle in radians.

        Returns:
            Absolute phase deviation |phi_hat - phi_ref|.
        """
        return abs(phi_hat - phi_ref)

    def check_deviation(
        self, delta_phi: float, epsilon: Optional[float] = None
    ) -> bool:
        """
        Check if deviation exceeds the detection threshold.

        Args:
            delta_phi: Computed phase deviation.
            epsilon: Override threshold (uses config if None).

        Returns:
            True if Delta_phi > epsilon (intrusion detected).
        """
        eps = epsilon if epsilon is not None else self.config.epsilon
        return delta_phi > eps

    def _determine_severity(self, delta_phi: float) -> AlertSeverity:
        """Map deviation magnitude to alert severity."""
        if delta_phi > self.config.critical_severity_threshold:
            return AlertSeverity.CRITICAL
        if delta_phi > self.config.high_severity_threshold:
            return AlertSeverity.HIGH
        if delta_phi > self.config.epsilon * 2:
            return AlertSeverity.MEDIUM
        return AlertSeverity.LOW

    def observe(
        self,
        phi_hat: float,
        phi_ref: float,
        node_id: str = "unknown",
        timestamp: Optional[float] = None,
    ) -> Optional[IntrusionAlert]:
        """
        Process a new phase observation and check for intrusion.

        Args:
            phi_hat: Observed phase angle.
            phi_ref: Reference (expected) phase angle.
            node_id: Source node identifier.
            timestamp: Observation time (defaults to now).

        Returns:
            IntrusionAlert if deviation exceeds threshold, else None.
        """
        ts = timestamp if timestamp is not None else time.time()
        obs = PhaseObservation(
            phi_hat=phi_hat, phi_ref=phi_ref, timestamp=ts, node_id=node_id
        )
        self.window.append(obs)
        self._total_observations += 1

        delta = obs.delta_phi

        if self.check_deviation(delta):
            now = time.time()
            if now - self._last_alert_time < self.config.cooldown_seconds:
                return None

            severity = self._determine_severity(delta)
            alert = IntrusionAlert(
                timestamp=ts,
                severity=severity,
                delta_phi=delta,
                epsilon=self.config.epsilon,
                node_id=node_id,
                message=(
                    f"Phase deviation {delta:.6f} rad exceeds threshold "
                    f"{self.config.epsilon:.6f} rad on node {node_id}"
                ),
            )
            self.alerts.append(alert)
            if len(self.alerts) > self.config.alert_history_size:
                self.alerts = self.alerts[-self.config.alert_history_size :]
            self._last_alert_time = now
            self._total_alerts += 1
            return alert

        return None

    def get_statistics(self) -> dict[str, float]:
        """
        Compute running statistics over the sliding window.

        Returns:
            Dictionary with mean, std, max, min deviation values.
        """
        if not self.window:
            return {
                "mean": 0.0,
                "std": 0.0,
                "max": 0.0,
                "min": 0.0,
                "count": 0,
            }
        deviations = np.array([obs.delta_phi for obs in self.window])
        return {
            "mean": float(np.mean(deviations)),
            "std": float(np.std(deviations)),
            "max": float(np.max(deviations)),
            "min": float(np.min(deviations)),
            "count": len(deviations),
        }

    def get_deviation_array(self) -> NDArray[np.float64]:
        """Return numpy array of all deviations in the current window."""
        if not self.window:
            return np.array([], dtype=np.float64)
        return np.array([obs.delta_phi for obs in self.window])

    def adaptive_epsilon(self, k: float = 3.0) -> float:
        """
        Compute an adaptive threshold using running statistics.

        The adaptive epsilon is: mean + k * std

        Args:
            k: Number of standard deviations above the mean.

        Returns:
            Adaptive threshold value.
        """
        stats = self.get_statistics()
        return stats["mean"] + k * stats["std"]

    def reset(self) -> None:
        """Clear all observations and alerts."""
        self.window.clear()
        self.alerts.clear()
        self._total_observations = 0
        self._total_alerts = 0
        self._last_alert_time = 0.0

    @property
    def alert_rate(self) -> float:
        """Compute alert rate (alerts per observation)."""
        if self._total_observations == 0:
            return 0.0
        return self._total_alerts / self._total_observations

    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (
            f"PhaseMonitor(obs={self._total_observations}, "
            f"alerts={self._total_alerts}, "
            f"mean_delta={stats['mean']:.6f}, "
            f"eps={self.config.epsilon:.4f})"
        )


def simulate_intrusion_detection() -> None:
    """Demonstrate phase deviation monitoring with intrusion simulation."""
    print("=" * 60)
    print("  HSL Intrusion Detection - Phase Deviation Monitor")
    print("  Reference: DOI 10.5281/zenodo.19056387 (HPG 1.0)")
    print("  Criterion: Delta_phi(t) = |phi_hat(t) - phi_ref| > epsilon")
    print("=" * 60)

    monitor = PhaseMonitor(
        config=DetectionConfig(
            epsilon=0.05,
            window_size=32,
            high_severity_threshold=0.10,
            critical_severity_threshold=0.20,
        )
    )

    np.random.seed(42)
    phi_ref = 2.0 * math.pi * 3.0 / 12.0

    print(f"\n  Reference phase: {phi_ref:.6f} rad")
    print(f"  Threshold epsilon: {monitor.config.epsilon}")
    print()

    normal_noise = np.random.normal(0, 0.01, 40)
    intrusion_noise = np.random.normal(0.15, 0.03, 10)

    all_noise = np.concatenate([normal_noise, intrusion_noise])

    print(f"  {'Step':>5}  {'phi_hat':>10}  {'Delta_phi':>10}  {'Alert':>8}")
    print(f"  {'-'*5}  {'-'*10}  {'-'*10}  {'-'*8}")

    for i, noise in enumerate(all_noise):
        phi_hat = phi_ref + noise
        alert = monitor.observe(phi_hat, phi_ref, node_id="sensor-01")
        status = "NONE"
        if alert is not None:
            status = f"{alert.severity.value.upper():>5}"
            print(
                f"  {i+1:>5}  {phi_hat:>10.6f}  "
                f"{abs(noise):>10.6f}  {status:>8}"
            )
        elif (i + 1) % 10 == 0:
            print(
                f"  {i+1:>5}  {phi_hat:>10.6f}  "
                f"{abs(noise):>10.6f}  {status:>8}"
            )

    stats = monitor.get_statistics()
    print(f"\n  --- Window Statistics ---")
    print(f"  Mean deviation:   {stats['mean']:.6f} rad")
    print(f"  Std deviation:    {stats['std']:.6f} rad")
    print(f"  Max deviation:    {stats['max']:.6f} rad")
    print(f"  Adaptive epsilon: {monitor.adaptive_epsilon(k=3.0):.6f} rad")
    print(f"  Total alerts:     {monitor._total_alerts}")
    print(f"  Alert rate:       {monitor.alert_rate:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    simulate_intrusion_detection()