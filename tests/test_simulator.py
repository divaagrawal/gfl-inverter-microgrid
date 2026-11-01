import numpy as np
import pytest

from src.simulator import CASES, event_label, metrics, simulate


@pytest.mark.parametrize("case", CASES)
def test_each_declared_case_completes(case):
    frame = simulate(case)
    assert len(frame) == 3001
    assert frame.case.nunique() == 1
    assert set(frame.event.unique()) == {"black_start", "grid_connected", "islanded", "load_step", "reconnected"}


def test_unknown_case_is_rejected():
    with pytest.raises(ValueError, match="unknown case"):
        simulate("mystery")


def test_invalid_timestep_is_rejected():
    with pytest.raises(ValueError, match="positive"):
        simulate("gfm_droop", dt=0)


def test_grid_following_cannot_serve_island_without_reference():
    frame = simulate("grid_following")
    island = frame[(frame.time_s >= 10) & (frame.time_s < 48)]
    assert island.served_fraction.max() == 0
    assert island.voltage_pu.iloc[-1] == 0


@pytest.mark.parametrize("case", ("gfm_droop", "gfm_vsm"))
def test_grid_forming_cases_keep_the_synthetic_island_energised(case):
    frame = simulate(case)
    island = frame[(frame.time_s >= 10) & (frame.time_s < 48)]
    assert island.served_fraction.min() > 0.75
    assert island.voltage_pu.min() > 0.80


def test_current_never_exceeds_declared_cap():
    assert np.max(simulate("gfm_vsm").current_pu) <= 1.20


def test_metric_output_records_completion_and_case():
    summary = metrics(simulate("gfm_droop"))
    assert summary["status"] == "completed"
    assert summary["case"] == "gfm_droop"
    assert summary["unserved_energy_pu_s"] >= 0


def test_unserved_energy_integrates_event_specific_net_demand():
    summary = metrics(simulate("gfm_droop"))
    assert summary["unserved_energy_pu_s"] == pytest.approx(0.91, abs=0.02)


def test_event_phases_are_explicit():
    assert [event_label(t) for t in (0, 4, 10, 22, 35, 48)] == [
        "black_start", "grid_connected", "islanded", "load_step", "islanded", "reconnected"
    ]


@pytest.mark.parametrize("case", CASES)
def test_synthetic_reconnection_pulls_each_case_toward_nominal(case):
    frame = simulate(case)
    at_reconnect = frame[frame.time_s >= 48].iloc[0]
    final = frame.iloc[-1]
    assert abs(final.frequency_hz - 50) <= abs(at_reconnect.frequency_hz - 50) + 1e-9
    assert abs(final.voltage_pu - 1) <= abs(at_reconnect.voltage_pu - 1) + 1e-9
