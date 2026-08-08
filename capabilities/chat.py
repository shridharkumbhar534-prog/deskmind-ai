from brain.capability import Capability

class ChatCapability(Capability):

    def execute(self, request, context):
        return "Chat capability Executed"