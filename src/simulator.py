from __future__ import annotations

"""Transparent reduced-order synthetic microgrid event simulation.

This is intentionally a teaching model, not an EMT, RMS, protection, or
hardware-in-the-loop study.  Its purpose is to make the control distinctions
between a grid-following and grid-forming inverter inspectable end-to-end.
"""
import numpy as np
import pandas as pd

CASES = ("grid_following", "gfm_droop", "gfm_vsm")
DT = 0.02


def event_label(time_s: float) -> str:
    """Return the active, deliberately synthetic event phase."""
    if time_s < 4:
        return "black_start"
    if time_s < 10:
        return "grid_connected"
    if time_s < 22:
        return "islanded"
    if time_s < 35:
        return "load_step"
    if time_s < 48:
        return "islanded"
    return "reconnected"


def simulate(case: str, dt: float = DT, duration_s: float = 60.0) -> pd.DataFrame:
    """Simulate one synthetic 60 second microgrid event trace.

    Power is per-unit on a notional 500 kVA inverter base.  The deliberately
    simple plant captures controller-facing behaviour only: GFL needs a grid
    reference, while GFM forms voltage and frequency subject to a current cap.
    """
    if case not in CASES:
        raise ValueError(f"unknown case {case}")
    if dt <= 0 or duration_s <= 0:
        raise ValueError("dt and duration_s must be positive")
    t = np.arange(0, duration_s + dt, dt)
    f = np.full_like(t, 50.0)
    v = np.zeros_like(t)
    soc = np.full_like(t, 0.62)
    p = np.zeros_like(t)
    current = np.zeros_like(t)
    served = np.zeros_like(t)
    load_profile = 0.34 + np.where((t >= 22) & (t < 35), 0.30, 0.0)
    solar_profile = np.where((t >= 12) & (t < 42), 0.12, 0.03)
    net_demand = load_profile - solar_profile
    H = 1.7 if case == "gfm_droop" else 4.8
    damping = 1.5 if case == "gfm_droop" else 2.8
    for k in range(1, len(t)):
        now = t[k]
        phase = event_label(now)
        grid_available = phase in {"grid_connected", "reconnected"}
        # The 0.30 pu step deliberately takes net demand above the 0.45 pu
        # inverter limit so the controller responses are distinguishable.
        if case == "grid_following" and not grid_available:
            # A GFL controller loses its voltage-angle reference in the island.
            v[k] = max(0.0, v[k - 1] - 0.12 * dt)
            f[k] = max(0.0, f[k - 1] - 6 * dt)
            served[k] = 0.0
            p[k] = 0.0
            current[k] = 0.0
            soc[k] = soc[k - 1]
            continue
        demand = net_demand[k]
        command = demand + 1.8 * (50 - f[k - 1]) / 50
        p[k] = np.clip(command, -0.45, 0.45)
        current[k] = min(1.20, abs(p[k]) / max(v[k - 1], 0.70))
        limited = abs(command) > 0.45
        delivered = np.sign(command) * min(abs(command), 0.45)
        mismatch = delivered - demand
        if grid_available:
            # Simplified synthetic reconnection: the restored stiff grid pulls
            # each mode back to nominal. This is not a synchronisation study.
            f[k] = f[k - 1] + dt * 3.0 * (50.0 - f[k - 1])
            v[k] = v[k - 1] + dt * 3.0 * (1.0 - v[k - 1])
            served[k] = 1.0
        else:
            f[k] = np.clip(
                f[k - 1] + dt * (mismatch * 50 / (2 * H) - damping * (f[k - 1] - 50)),
                45,
                52,
            )
            target_v = min(1.0, now / 2.0) if phase == "black_start" else 1.0
            v[k] = np.clip(
                v[k - 1] + dt * (0.75 * mismatch - 1.4 * (v[k - 1] - target_v)),
                0.82 if phase != "black_start" else 0.0,
                1.08,
            )
            served[k] = min(1.0, max(0.0, abs(delivered) / max(demand, .01)))
        soc[k] = np.clip(soc[k - 1] - max(delivered, 0) * dt / 1.8, 0.15, 0.90)
        if limited:
            current[k] = 1.20
    return pd.DataFrame(
        {
            "time_s": t,
            "frequency_hz": f,
            "voltage_pu": v,
            "battery_power_pu": p,
            "current_pu": current,
            "soc": soc,
            "served_fraction": served,
            "load_demand_pu": load_profile,
            "solar_pu": solar_profile,
            "net_demand_pu": net_demand,
            "event": [event_label(x) for x in t],
            "case": case,
        }
    )


def metrics(frame: pd.DataFrame) -> dict[str, float | str]:
    """Summarise the 10--48 s islanding window without hiding failures."""
    island = frame[(frame.time_s >= 10) & (frame.time_s < 48)]
    dt = float(frame.time_s.iloc[1] - frame.time_s.iloc[0])
    return {
        "case": str(frame.case.iloc[0]),
        "status": "completed",
        "frequency_nadir_hz": round(float(island.frequency_hz.min()), 3),
        "voltage_nadir_pu": round(float(island.voltage_pu.min()), 3),
        "minimum_served_fraction": round(float(island.served_fraction.min()), 3),
        "current_limit_seconds": round(float((island.current_pu >= 1.20 - 1e-8).sum() * dt), 2),
        "unserved_energy_pu_s": round(
            float(((1 - island.served_fraction) * island.net_demand_pu).sum() * dt), 3
        ),
    }
