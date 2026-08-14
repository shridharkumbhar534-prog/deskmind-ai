
from brain.errors import CapabilityNotFoundError


class CapabilityRegistry:

    def __init__(self):
        # Intent -> Capability Class
        self._factories = {}

        # Intent -> Capability Instance
        self._instances = {}

    def register(self, intent, capability_class):
        """
        Register a capability class.
        """

        if intent in self._factories:
            raise ValueError(
                f"Capability '{intent}' is already registered."
            )

        self._factories[intent] = capability_class

    def get(self, intent):
        """
        Return a singleton capability instance.
        Creates it lazily on first use.
        """

        if intent not in self._factories:
            raise CapabilityNotFoundError(intent)

        # Already created?
        if intent in self._instances:
            return self._instances[intent]

        # Create lazily
        capability = self._factories[intent]()

        self._instances[intent] = capability

        return capability
