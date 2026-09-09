from brain.bootstrap import register_capabilities
from brain.context import SEARCH_DIRECTORY
from brain.dispatcher import Dispatcher
from brain.errors import InvalidRequestError
from brain.intent import IntentDetector
from brain.registry import CapabilityRegistry
from brain.workflow import (
    Workflow,
    WorkflowEngine,
    build_pdf_to_note_workflow,
)


class Brain:

    def __init__(self):
        self.intent_detector = IntentDetector()

        self.registry = CapabilityRegistry()
        register_capabilities(self.registry)

        self.dispatcher = Dispatcher(self.registry)
        self.workflow_engine = WorkflowEngine(self.dispatcher)

    def process(self, message: str, context=None):
        if not message or not message.strip():
            raise InvalidRequestError()

        context = context or {}

        if SEARCH_DIRECTORY in context:
            intent = "file_search"
        else:
            intent = self.intent_detector.detect(message)

        return self.dispatcher.dispatch(
            intent,
            message,
            context
        )

    def run_workflow(self, workflow: Workflow, context: dict | None = None) -> dict:
        """Execute a multi-step workflow, passing each step's result
        into the next step's context.  Does not affect single-intent
        ``process`` behavior.
        """
        return self.workflow_engine.run(workflow, context)

    def save_active_pdf_as_note(
        self,
        context: dict | None = None,
        summary_request: str = "Summarize this PDF",
    ) -> dict:
        """Summarize the active PDF and save the generated content as a note."""
        return self.run_workflow(
            build_pdf_to_note_workflow(summary_request),
            context,
        )