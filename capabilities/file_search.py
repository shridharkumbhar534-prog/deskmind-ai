from pathlib import Path

from brain.capability import Capability
from brain.context import SEARCH_DIRECTORY


# Key under which FileSearchCapability stores structured results in the
# workflow context so downstream capabilities can read resolved paths
# without parsing the human-readable display string.
FILE_SEARCH_RESULTS = "file_search_results"


class FileSearchResult:
    """Structured, machine-readable result for workflow consumers."""

    def __init__(self, query: str, matches: list[Path], directory: Path):
        self.query = query
        self.matches = [path.resolve() for path in matches]
        self.directory = directory.resolve()

    @property
    def is_ambiguous(self) -> bool:
        """True when more than one file matched the search query."""
        return len(self.matches) > 1

    @property
    def has_matches(self) -> bool:
        return len(self.matches) > 0

    def resolved_paths(self) -> list[str]:
        """Return absolute path strings for all matches."""
        return [str(p.resolve()) for p in self.matches]

    def first_resolved_path(self) -> str | None:
        """Return the absolute path of the first match, or None."""
        if not self.matches:
            return None
        return str(self.matches[0].resolve())

    def format(self) -> str:
        """Human-readable display string, identical to the original
        FileSearch output format for UI backward compatibility.
        """
        if not self.matches:
            return f'No files found containing "{self.query}".'

        output = [
            f'Files containing "{self.query}" ({len(self.matches)} found):'
        ]

        for path in self.matches[:50]:
            try:
                relative_path = path.relative_to(self.directory)
            except ValueError:
                relative_path = path

            output.append(f"- {relative_path}")

        if len(self.matches) > 50:
            output.append(
                f"\n...and {len(self.matches) - 50} more files."
            )

        return "\n".join(output)

    def __repr__(self):
        return (
            f"FileSearchResult(query={self.query!r}, "
            f"matches={len(self.matches)})"
        )


class FileSearchCapability(Capability):
    """Search text files in a selected local folder.

    For workflow consumers, a structured :class:`FileSearchResult` is
    stored in the context under ``FILE_SEARCH_RESULTS``.  The
    human-readable display string is still returned from
    :meth:`execute` for UI backward compatibility.
    """

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".py",
        ".md",
        ".csv",
        ".json",
        ".sql",
        ".log",
        ".pdf",
    }

    IGNORED_DIRECTORIES = {
        "venv",
        ".venv",
        "env",
        ".env",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".idea",
        ".vscode",
    }

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    MAX_PDF_PAGES = 100

    def execute(self, request, context=None):
        if not context or SEARCH_DIRECTORY not in context:
            raise ValueError("No folder was selected for file search.")

        directory = Path(context["search_directory"])

        if not directory.exists():
            raise ValueError("The selected folder does not exist.")

        if not directory.is_dir():
            raise ValueError("The selected path is not a folder.")

        query = request.strip()

        if not query:
            return "Please enter something to search for."

        matches = self._search(directory, query)

        result = FileSearchResult(query, matches, directory)

        # Store structured result for workflow consumers.
        context[FILE_SEARCH_RESULTS] = result

        return result.format()

    def _search(self, directory: Path, query: str) -> list[Path]:
        """Return matching file paths (absolute) in traversal order."""
        results: list[Path] = []

        for path in directory.rglob("*"):

            if any(
                ignored in path.parts
                for ignored in self.IGNORED_DIRECTORIES
            ):
                continue

            if not path.is_file():
                continue

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            try:
                if path.stat().st_size > self.MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            if path.suffix.lower() == ".pdf":
                if not self._pdf_contains(path, query):
                    continue
            else:
                try:
                    text = path.read_text(
                        encoding="utf-8",
                        errors="ignore",
                    )
                except Exception:
                    continue

                if query.lower() not in text.lower():
                    continue

            results.append(path)

        return results

    def _pdf_contains(self, path: Path, query: str) -> bool:
        """Check whether a PDF file contains the query text.

        Respects the same safety limits as PDFCapability: max file size
        and max page count.  Text extraction failures are treated as
        non-matches rather than errors.
        """
        try:
            if path.stat().st_size > self.MAX_FILE_SIZE:
                return False
        except OSError:
            return False

        try:
            import pymupdf
        except ImportError:
            return False

        try:
            document = pymupdf.open(path)

            if len(document) > self.MAX_PDF_PAGES:
                document.close()
                return False

            for page in document:
                text = page.get_text()
                if query.lower() in text.lower():
                    document.close()
                    return True

            document.close()
            return False

        except Exception:
            return False
