"""
Utilities for converting labels from Draw.io into a clean,
consistent representation for the Transition Model.
"""

from html import unescape
import re


class LabelNormalizer:

    TAG_RE = re.compile(r"<[^>]+>")
    SPACE_RE = re.compile(r"\s+")

    #
    # Words that should always remain uppercase.
    #
    ACRONYMS = {
        "API",
        "JMP",
        "JCP",
        "JCR",
        "JCT",
        "KLM",
        "KLC",
        "HR",
        "XML",
        "JSON",
        "SQL",
        "FTP",
        "SFTP",
        "CSV",
        "PDF",
    }

    NORMALIZATION_DICTIONARY = {
        "Crewplanner": "Crew Planner",
        "Crewhr": "Crew HR",
        "Fileadapter": "File Adapter",
        "Crewcheck-in": "Crew Check-in",
        "Icrew": "ICrew",
        "Apis": "APIs",
    }

    @classmethod
    def normalize(cls, label: str) -> str:

        if not label:
            return ""

        #
        # Replace line breaks before removing tags.
        #
        label = re.sub(
            r"<br\s*/?>",
            " ",
            label,
            flags=re.IGNORECASE,
        )

        #
        # Remove all remaining HTML tags.
        #
        label = cls.TAG_RE.sub("", label)

        #
        # Decode HTML entities (&nbsp;, &amp;, ...)
        #
        label = unescape(label)

        #
        # Convert non-breaking spaces.
        #
        label = label.replace("\xa0", " ")

        #
        # Collapse whitespace.
        #
        label = cls.SPACE_RE.sub(" ", label)

        label = label.strip()

        #
        # Normalize capitalization.
        #
        words = []

        for word in label.split():

            upper = word.upper()

            if upper in cls.ACRONYMS:
                words.append(upper)
            else:
                words.append(
                    word[:1].upper() +
                    word[1:].lower()
                )

        normalized = " ".join(words)

        for old, new in cls.NORMALIZATION_DICTIONARY.items():
            normalized = normalized.replace(old, new)

        return normalized
