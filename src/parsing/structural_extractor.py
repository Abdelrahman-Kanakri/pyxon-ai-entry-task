"""
Structural Extractor

Extracts and analyzes document structure including headings,
sections, and hierarchy.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from src.ingestion.base import ExtractedContent

logger = logging.getLogger(__name__)


@dataclass
class Section:
    """Represents a document section."""

    level: int  # Heading level (1-6)
    title: str
    content: str
    start_pos: int
    end_pos: int
    subsections: List["Section"] = field(default_factory=list)


@dataclass
class DocumentStructure:
    """Complete document structure analysis."""

    sections: List[Section]
    has_hierarchy: bool
    max_depth: int
    outline: List[str]


class StructuralExtractor:
    """
    Extracts structural elements from documents.

    Identifies headings, sections, and builds a hierarchical
    representation of the document structure.
    """

    # Patterns for identifying headings in plain text
    HEADING_PATTERNS = [
        # Markdown-style headings
        (r"^#{1,6}\s+(.+)$", "markdown"),
        # All caps lines (likely headings)
        (r"^([A-Z][A-Z\s]{2,})$", "caps"),
        # Numbered sections (1. 1.1, etc.)
        (r"^(\d+\.)+\s*(.+)$", "numbered"),
        # Chapter/Section markers
        (r"^(Chapter|Section|Part)\s+\d+[:\s]+(.+)$", "chapter"),
    ]

    def __init__(self):
        """Initialize the structural extractor."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_structure(self, content: ExtractedContent) -> DocumentStructure:
        """
        Extract document structure from content.

        Args:
            content: Extracted document content

        Returns:
            DocumentStructure with hierarchical organization
        """
        self.logger.info("Extracting document structure")

        # Try to use pre-extracted structure if available
        if content.structured_data and content.structured_data.get("headings"):
            sections = self._build_from_metadata(content.structured_data)
        else:
            # Fallback: Analyze text to find structure
            sections = self._analyze_text_structure(content.cleaned_text)

        # Build hierarchy
        hierarchical_sections = self._build_hierarchy(sections)

        # Calculate metrics
        has_hierarchy = len(hierarchical_sections) > 0
        max_depth = self._calculate_max_depth(hierarchical_sections)
        outline = self._generate_outline(hierarchical_sections)

        structure = DocumentStructure(
            sections=hierarchical_sections,
            has_hierarchy=has_hierarchy,
            max_depth=max_depth,
            outline=outline,
        )

        self.logger.info(
            f"Structure extracted: {len(hierarchical_sections)} top-level sections, "
            f"max depth: {max_depth}"
        )

        return structure

    def _build_from_metadata(self, structured_data: Dict[str, Any]) -> List[Section]:
        """
        Build sections from pre-extracted metadata.

        Args:
            structured_data: Structured data from document

        Returns:
            List of Section objects
        """
        sections = []
        headings = structured_data.get("headings", [])

        for i, heading in enumerate(headings):
            level = heading.get("level", 1)
            title = heading.get("text", "")

            # Estimate content positions
            start_pos = heading.get("start_pos", i * 1000)
            end_pos = (
                headings[i + 1].get("start_pos", start_pos + 1000)
                if i + 1 < len(headings)
                else start_pos + 1000
            )

            section = Section(
                level=level,
                title=title,
                content="",  # Content will be filled later
                start_pos=start_pos,
                end_pos=end_pos,
            )
            sections.append(section)

        return sections

    def _analyze_text_structure(self, text: str) -> List[Section]:
        """
        Analyze plain text to identify structural elements.

        Args:
            text: Document text

        Returns:
            List of identified sections
        """
        sections = []
        lines = text.split("\n")
        current_pos = 0

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                current_pos += 1
                continue

            # Check each heading pattern
            for pattern, pattern_type in self.HEADING_PATTERNS:
                match = re.match(pattern, line, re.MULTILINE)
                if match:
                    # Determine heading level
                    level = self._determine_level(line, pattern_type, match)

                    # Extract title
                    title = self._extract_title(line, pattern_type, match)

                    # Create section
                    section = Section(
                        level=level,
                        title=title,
                        content="",
                        start_pos=current_pos,
                        end_pos=current_pos,  # Will be updated
                    )
                    sections.append(section)
                    break

            current_pos += len(line) + 1

        # Update end positions
        for i in range(len(sections) - 1):
            sections[i].end_pos = sections[i + 1].start_pos

        if sections:
            sections[-1].end_pos = current_pos

        return sections

    def _determine_level(self, line: str, pattern_type: str, match: re.Match) -> int:
        """
        Determine heading level from pattern match.

        Args:
            line: Text line
            pattern_type: Type of pattern matched
            match: Regex match object

        Returns:
            Heading level (1-6)
        """
        if pattern_type == "markdown":
            # Count # symbols
            return len(line) - len(line.lstrip("#"))

        elif pattern_type == "numbered":
            # Count dots in numbering
            dots = line.split()[0].count(".")
            return min(dots, 6)

        elif pattern_type == "chapter":
            return 1  # Top level

        elif pattern_type == "caps":
            return 2  # Second level guess

        return 1  # Default to top level

    def _extract_title(self, line: str, pattern_type: str, match: re.Match) -> str:
        """
        Extract heading title from matched line.

        Args:
            line: Text line
            pattern_type: Type of pattern matched
            match: Regex match object

        Returns:
            Extracted title
        """
        if pattern_type == "markdown":
            return line.lstrip("#").strip()

        elif pattern_type == "numbered":
            # Remove numbering
            parts = line.split(maxsplit=1)
            return parts[1] if len(parts) > 1 else line

        elif pattern_type == "chapter":
            return match.group(2).strip()

        elif pattern_type == "caps":
            return match.group(1).strip()

        return line.strip()

    def _build_hierarchy(self, sections: List[Section]) -> List[Section]:
        """
        Build hierarchical structure from flat section list.

        Args:
            sections: Flat list of sections

        Returns:
            Hierarchical section tree
        """
        if not sections:
            return []

        root_sections = []
        stack = []

        for section in sections:
            # Find parent section
            while stack and stack[-1].level >= section.level:
                stack.pop()

            if not stack:
                # Top-level section
                root_sections.append(section)
            else:
                # Add as subsection of parent
                stack[-1].subsections.append(section)

            stack.append(section)

        return root_sections

    def _calculate_max_depth(self, sections: List[Section]) -> int:
        """
        Calculate maximum nesting depth.

        Args:
            sections: Hierarchical sections

        Returns:
            Maximum depth level
        """
        if not sections:
            return 0

        max_depth = 0

        def traverse(section: Section, depth: int):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            for subsection in section.subsections:
                traverse(subsection, depth + 1)

        for section in sections:
            traverse(section, 1)

        return max_depth

    def _generate_outline(self, sections: List[Section]) -> List[str]:
        """
        Generate text outline from structure.

        Args:
            sections: Hierarchical sections

        Returns:
            List of outline lines
        """
        outline = []

        def add_section(section: Section, indent: int):
            prefix = "  " * indent
            outline.append(f"{prefix}- {section.title}")
            for subsection in section.subsections:
                add_section(subsection, indent + 1)

        for section in sections:
            add_section(section, 0)

        return outline
