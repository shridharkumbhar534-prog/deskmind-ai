from brain.registry import CapabilityRegistry


class Dispatcher:

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def dispatch(self, intent, request, context=None):

        capability = self.registry.get(intent)

        return capability.execute(request, context)