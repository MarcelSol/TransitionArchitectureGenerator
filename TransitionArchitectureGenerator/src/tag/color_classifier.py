"""
color_classifier.py

Converts Draw.io fill colors into architectural node categories.
"""

from __future__ import annotations

from tag.transition_model import NodeCategory


class ColorClassifier:

    COLOR_MAPPING = {
        "#E51400": NodeCategory.TRANSACTIONAL,
        "#F8CECC": NodeCategory.TRANSACTIONAL,
        "#E3C800": NodeCategory.MASTER_DATA,
        "#FFE6CC": NodeCategory.MASTER_DATA,
        "#008A00": NodeCategory.EXTERNAL,
        "#D5E8D4": NodeCategory.EXTERNAL,
        "": NodeCategory.INTEGRATION,     # transparent colors
        "#FFFFFF": NodeCategory.INTEGRATION,
    }

    @classmethod
    def classify(cls, style: dict[str, str]) -> NodeCategory:

        color = style.get("fillColor", "").upper()

        return cls.COLOR_MAPPING.get(
            color,
            NodeCategory.UNKNOWN,
        )
