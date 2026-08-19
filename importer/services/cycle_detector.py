from enum import IntEnum


class VisitState(IntEnum):
    UNVISITED = 0
    VISITING = 1
    COMPLETED = 2


def detect_cycles(
    manager_of: dict[str, str],
) -> list[list[str]]:
    """
    Detect reporting cycles in the employee hierarchy.

    manager_of represents the reporting relationship:

        employee_id -> manager_id

    Example:

        {
            "E001": "E002",
            "E002": "E003",
            "E003": "E001",
        }

    Returns:
        A list of cycles.

        Example:

        [
            ["E001", "E002", "E003", "E001"]
        ]
    """

    states = {}
    cycles = []

    # ---------------------------------------------------------
    # DFS helper
    # ---------------------------------------------------------

    def dfs(
        employee_id: str,
        path: list[str],
        path_index: dict[str, int],
    ) -> None:

        states[employee_id] = VisitState.VISITING

        path.append(employee_id)
        path_index[employee_id] = len(path) - 1

        manager_id = manager_of.get(employee_id)

        # -----------------------------------------------------
        # Employee has no manager.
        #
        # This is a normal endpoint.
        # -----------------------------------------------------

        if manager_id is None:
            states[employee_id] = VisitState.COMPLETED

            path.pop()
            path_index.pop(employee_id, None)

            return

        manager_state = states.get(
            manager_id,
            VisitState.UNVISITED,
        )

        # -----------------------------------------------------
        # Manager hasn't been visited.
        # Continue DFS.
        # -----------------------------------------------------

        if manager_state == VisitState.UNVISITED:

            dfs(
                manager_id,
                path,
                path_index,
            )

        # -----------------------------------------------------
        # Manager is currently being visited.
        #
        # This means we've reached a node already present
        # in the current DFS path.
        #
        # Therefore, we found a cycle.
        # -----------------------------------------------------

        elif manager_state == VisitState.VISITING:

            cycle_start = path_index[manager_id]

            cycle = (
                path[cycle_start:]
                + [manager_id]
            )

            cycles.append(cycle)

        # -----------------------------------------------------
        # COMPLETED means that branch was already processed.
        # No new cycle is created here.
        # -----------------------------------------------------

        states[employee_id] = VisitState.COMPLETED

        path.pop()
        path_index.pop(employee_id, None)

    # ---------------------------------------------------------
    # Start DFS from every employee.
    # ---------------------------------------------------------

    employees = set(manager_of.keys())

    # Managers may not appear as keys because they don't have
    # managers themselves.
    #
    # Add them so every node in the graph is considered.
    employees.update(manager_of.values())

    for employee_id in employees:

        if states.get(employee_id, VisitState.UNVISITED) == (
            VisitState.UNVISITED
        ):
            dfs(
                employee_id,
                [],
                {},
            )

    return cycles