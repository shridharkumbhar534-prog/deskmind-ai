from abc import ABC, abstractmethod

class Capability(ABC):
    @abstractmethod

    def execute(self, request, context):
        """
        Execute the capability.

        Parameters:
            request: The user's request.
            context: Additional information from the Brain.

        Returns:
            A result object or response.
        """
        pass