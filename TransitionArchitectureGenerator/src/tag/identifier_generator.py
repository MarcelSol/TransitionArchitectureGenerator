"""
identifier_generator.py

Generates stable, deterministic identifiers for objects in the
Transition Model.

These identifiers are independent of the Draw.io internal IDs and
remain stable across releases of the source architecture.
"""

from __future__ import annotations

import re


class IdentifierGenerator:
    """Utility class for generating stable identifiers."""

    @staticmethod
    def node_id(name: str) -> str:
        """
        Generate a deterministic node identifier from a node name.

        Examples
        --------
        Crew Planner          -> crew_planner
        SAP HR                -> sap_hr
        NetLine Crew          -> netline_crew
        Crew Journey APIs     -> crew_journey_apis
        """

        if not name:
            raise ValueError("Node name may not be empty.")

        identifier = name.lower()

        #
        # Replace every sequence of non-alphanumeric characters
        # with a single underscore.
        #
        identifier = re.sub(
            r"[^a-z0-9]+",
            "_",
            identifier,
        )

        #
        # Collapse repeated underscores.
        #
        identifier = re.sub(
            r"_+",
            "_",
            identifier,
        )

        #
        # Remove leading/trailing underscores.
        #
        identifier = identifier.strip("_")

        if not identifier:
            raise ValueError(
                f'Unable to generate identifier from "{name}".'
            )

        return identifier

    @staticmethod
    def interface_id(
        source_node_id: str,
        target_node_id: str,
    ) -> str:
        """
        Generate a deterministic interface identifier.

        Example
        -------
        crew_planner
        netline_crew

        ->
        IF-crew_planner-netline_crew
        """

        if not source_node_id:
            raise ValueError("Source node ID may not be empty.")

        if not target_node_id:
            raise ValueError("Target node ID may not be empty.")

        return f"IF-{source_node_id}-{target_node_id}"
