"""Phase 4 -- minimal multi-step workflow orchestration.

A workflow is an ordered list of steps.  Each step runs an existing
capability (by its registered intent name) with a fixed request string
and the shared context dictionary.  The string result of each step is
fed into the next step's context under the key ``STEP_RESULT`` so
capabilities that understand it can use it; the result is also
returned to the caller at the end.

Design constraints:
- No changes to Brain, IntentDetector, Registry, Dispatcher,
  Capability, Context, or the database.
- No LLM autonomy -- workflows are explicit, hand-defined sequences.
- Single-intent ``Brain.process`` behavior is untouched.
"""


from brain.errors import WorkflowStepError

# Key under which a step's result is passed to the next step's context.
STEP_RESULT = "previous_step_result"


class WorkflowStep:
    """One step in a multi-step workflow.

    Parameters:
        intent:   Registered intent name, e.g. ``"notes"``.
        request:  The request string to pass to the capability.
        result_key (optional): Context key to store this step's result
                  under for the *next* step.  Defaults to
                  ``STEP_RESULT``.
    """

    def __init__(self, intent: str, request: str, result_key: str = STEP_RESULT):
        self.intent = intent
        self.request = request
        self.result_key = result_key

    def __repr__(self):
        return f"WorkflowStep({self.intent!r}, {self.request!r})"


class Workflow:
    """An ordered, named sequence of :class:`WorkflowStep` objects."""

    def __init__(self, name: str, steps: list[WorkflowStep]):
        if not name or not name.strip():
            raise ValueError("Workflow name must not be empty.")
        if not steps:
            raise ValueError("Workflow must contain at least one step.")
        self.name = name
        self.steps = list(steps)

    def __repr__(self):
        return f"Workflow({self.name!r}, {len(self.steps)} steps)"


class WorkflowEngine:
    """Execute a :class:`Workflow` step-by-step using a Dispatcher.

    The engine is deliberately simple:
    - It runs each step via ``dispatcher.dispatch``.
    - It stores the result of each step into the shared workflow context
      under ``result_key`` so the next step can read it.
    - Context values written by a capability remain available to later
      steps, while the caller's original context is not mutated.
    - If a step raises, the engine stops and re-raises.
    - The original context keys (active_note, active_pdf,
      search_directory) are preserved; step results use a separate key.
    """

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def run(self, workflow: Workflow, context: dict | None = None) -> dict:
        """Execute *workflow* and return a result dict.

        Returns:
            ``{"workflow": name, "results": [step1_result, ...]}``

        Raises:
            WorkflowStepError: if any step raises an exception.
        """
        workflow_context = dict(context) if context else {}

        results = []

        for i, step in enumerate(workflow.steps):
            if i > 0:
                previous_step = workflow.steps[i - 1]
                workflow_context[previous_step.result_key] = results[-1]

            try:
                result = self.dispatcher.dispatch(
                    step.intent,
                    step.request,
                    workflow_context,
                )
            except Exception as exc:
                raise WorkflowStepError(workflow.name, i, str(exc)) from exc

            results.append(result)

        return {
            "workflow": workflow.name,
            "results": results,
        }
