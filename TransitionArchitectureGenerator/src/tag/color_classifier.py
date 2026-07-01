"""
color_classifier.py

Converts Draw.io fill colours into architectural node categories.
"""

from __future__ import annotations

from tag.transition_model import NodeCategory


class ColorClassifier:

    COLOR_MAPPING = {
        "#D5E8D4": NodeCategory.EXTERNAL,
        "#FFFFFF": NodeCategory.INTEGRATION,
        "#F8CECC": NodeCategory.TRANSACTIONAL,
        "#FFE6CC": NodeCategory.MASTER_DATA,
    }

    @classmethod
    def classify(cls, style: dict[str, str]) -> NodeCategory:

        colour = style.get("fillColor", "").upper()

        return cls.COLOR_MAPPING.get(
            colour,
            NodeCategory.UNKNOWN,
        )
