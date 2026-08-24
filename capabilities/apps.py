import re

from brain.capability import Capability
from services.apps.launcher import AppLauncher


class AppCapability(Capability):
    """Open supported Windows applications."""

    _COMMAND = re.compile(
        r"^(?:open|launch|start)\s+(?P<app>.+?)\s*$",
        re.IGNORECASE,
    )

    def __init__(self, launcher=None):
        self.launcher = launcher or AppLauncher()

    def execute(self, request, context=None):
        request = request.strip()

        match = self._COMMAND.match(request)

        if not match:
            return (
                "Use a command such as:\n"
                "open calculator\n"
                "open notepad\n"
                "open chrome"
            )

        app_name = match["app"].strip()

        return self.launcher.launch(app_name)