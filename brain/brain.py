from brain.bootstrap import register_capabilities
from brain.context import SEARCH_DIRECTORY
from brain.dispatcher import Dispatcher
from brain.errors import InvalidRequestError, WorkflowStepError
from brain.intent import IntentDetector
from brain.registry import CapabilityRegistry
from brain.workflow import (
    Workflow,
    WorkflowEngine,
    build_pdf_to_note_workflow,
)
from brain.workflow_router import (
    WorkflowRouter,
    has_required_context,
)


class Brain:

    def __init__(self):
        self.intent_detector = IntentDetector()

        self.registry = CapabilityRegistry()
        register_capabilities(self.registry)

        self.dispatcher = Dispatcher(self.registry)
        self.workflow_engine = WorkflowEngine(self.dispatcher)
        self.workflow_router = WorkflowRouter()

    def process(self, message: str, context=None):
        if not message or not message.strip():
            raise InvalidRequestError()

        context = context or {}

        # Workflow routing takes precedence for multi-step requests.
        # When a workflow is recognized but its required context is
        # missing, return a safe message rather than falling through
        # to a single capability that would also fail.
        workflow = self.workflow_router.route(message, context)
        if workflow is not None:
            if not has_required_context(workflow, context):
                return self._missing_context_message(workflow)
            return self._run_workflow_safely(workflow, context)

        if SEARCH_DIRECTORY in context:
            intent = "file_search"
        else:
            intent = self.intent_detector.detect(message)

        return self.dispatcher.dispatch(
            intent,
            message,
            context
        )

    def _missing_context_message(self, workflow: Workflow) -> str:
        """Return a user-safe message when workflow context is missing."""
        if workflow.name == "pdf-to-note":
            return "Please select a PDF first."
        if workflow.name == "file-search-to-pdf":
            return "Please select a folder to search first."
        return "Please provide the required context for this workflow."

    def _run_workflow_safely(self, workflow: Workflow, context: dict) -> str:
        """Run a workflow and return a user-safe string.

        Workflow failures are caught and returned as plain messages
        rather than propagated, so Brain.process never raises an
        obscure workflow error to the UI.
        """
        try:
            result = self.workflow_engine.run(workflow, context)
        except WorkflowStepError as exc:
            return exc.user_message
        except Exception as exc:
            return "The requested workflow could not be completed."

        results = result.get("results", [])
        if results:
            return results[-1]
        return "The workflow completed."


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