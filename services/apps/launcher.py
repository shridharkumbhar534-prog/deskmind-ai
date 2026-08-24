import subprocess


class AppLauncher:
    """Launch a controlled set of supported Windows applications."""

    APPS = {
        "calculator": ["calc.exe"],
        "notepad": ["notepad.exe"],
        "chrome": ["cmd", "/c", "start", "", "chrome"],
        "edge": ["cmd", "/c", "start", "", "msedge"],
        "explorer": ["explorer.exe"],
        "cmd": ["cmd.exe"],
        "powershell": ["powershell.exe"],
    }

    ALIASES = {
        "calc": "calculator",
        "windows calculator": "calculator",
        "text editor": "notepad",
        "file explorer": "explorer",
        "terminal": "powershell",
        "command prompt": "cmd",
    }

    def launch(self, app_name: str) -> str:
        app_name = app_name.strip().lower()

        app_name = self.ALIASES.get(app_name, app_name)

        command = self.APPS.get(app_name)

        if command is None:
            supported = ", ".join(sorted(self.APPS))
            return (
                f"I don't know how to open '{app_name}'.\n"
                f"Supported apps: {supported}"
            )

        try:
            subprocess.Popen(command)
        except OSError as error:
            print(f"App launcher error: {error}")
            return f"Could not open {app_name}."

        return f"Opening {app_name}."