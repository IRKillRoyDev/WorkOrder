"""Work order totals and the two-column split."""

from workorder.state import AppState, MajorDefect, split_columns


def test_split_fills_left_column_first():
    left, right = split_columns(["a", "b", "c", "d", "e"])
    assert left == ["a", "b", "c"]
    assert right == ["d", "e"]


def test_estimate_adds_system_averages_and_names_gaps():
    state = AppState()
    state.add_system("Engine")
    state.add_system("Transmission")
    state.set_average("Engine", "Repair", 4)
    order = state.new_work_order()
    order.major_defects.append(MajorDefect("Engine", "No Crank, No Start", "Repair"))
    order.major_defects.append(MajorDefect("Transmission", "won't shift into 4th gear", "Diagnose"))

    estimate = order.estimate()

    assert estimate.total_days is None
    assert estimate.missing == ["Transmission Diagnose"]

    state.set_average("Transmission", "Diagnose", 1.5)
    estimate = order.estimate()
    assert estimate.ready
    assert estimate.total_days == 5.5


def test_other_is_not_a_system_name():
    state = AppState()
    assert not state.add_system("Other")
    assert not state.add_system("  ")


def test_qc_lines_put_major_defects_before_other():
    order = AppState().new_work_order()
    order.major_defects.append(MajorDefect("Engine", "No Crank, No Start", "Repair"))
    order.add_other_defect("leaking hose")
    labels = [label for _kind, label in order.qc_lines()]
    assert labels == ["Engine - No Crank, No Start", "Other - leaking hose"]


def test_unchecked_defect_leaves_the_list_and_the_estimate():
    state = AppState()
    state.add_system("Engine")
    state.set_average("Engine", "Repair", 4)
    order = state.new_work_order()
    order.major_defects.append(MajorDefect("Engine", "No Crank, No Start", "Repair", included=False))
    order.add_other_defect("leaking hose")
    order.set_other_included(0, False)

    assert order.qc_lines() == []
    assert order.estimate().lines == []
    assert order.estimate().total_days is None


def test_turned_off_action_stays_on_the_defect_list():
    state = AppState()
    state.add_system("Engine")
    state.set_average("Engine", "Repair", 4)
    state.set_action_on("Engine", "Repair", False)
    order = state.new_work_order()
    order.major_defects.append(MajorDefect("Engine", "No Crank, No Start", "Repair"))

    assert order.qc_lines() == [("major", "Engine - No Crank, No Start")]
    estimate = order.estimate()
    assert estimate.lines == []
    assert estimate.total_days is None
    assert estimate.turned_off == ["Engine Repair"]
