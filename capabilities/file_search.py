from pathlib import Path

from brain.capability import Capability


class FileSearchCapability(Capability):
    """Search text files in a selected local folder."""

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".py",
        ".md",
        ".csv",
        ".json",
        ".sql",
        ".log",
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

    def execute(self, request, context=None):
        if not context or "search_directory" not in context:
            raise ValueError("No folder was selected for file search.")

        directory = Path(context["search_directory"])

        if not directory.exists():
            raise ValueError("The selected folder does not exist.")

        if not directory.is_dir():
            raise ValueError("The selected path is not a folder.")

        query = request.strip()

        if not query:
            return "Please enter something to search for."

        results = []

        for path in directory.rglob("*"):

            # Ignore unwanted directories
            if any(
                ignored in path.parts
                for ignored in self.IGNORED_DIRECTORIES
            ):
                continue

            if not path.is_file():
                continue

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            # Ignore very large files
            try:
                if path.stat().st_size > self.MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                continue

            if query.lower() in text.lower():
                results.append(path)

        if not results:
            return f'No files found containing "{query}".'

        output = [
            f'Files containing "{query}" ({len(results)} found):'
        ]

        for path in results[:50]:
            try:
                relative_path = path.relative_to(directory)
            except ValueError:
                relative_path = path

            output.append(f"- {relative_path}")

        if len(results) > 50:
            output.append(
                f"\n...and {len(results) - 50} more files."
            )

        return "\n".join(output)