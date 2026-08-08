from brain import capability, intent


class CapabilityRegistry:

    def __init__(self):

        self._factories = {}

        self._instances = {}     

    def register(self, name, factory):
        """
        Register a capability class.
        Example:
            registry.register("pdf", PDFCapability)
        """   

        self._factories[intent] = capability._class


        