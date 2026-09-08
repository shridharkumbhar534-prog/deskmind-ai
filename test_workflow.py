"""Tests for Phase 4 -- multi-step workflow orchestration.

Covers:
- Sequential workflow execution
- Capability result propagation between steps
- Failure handling (step raises, engine stops)
- Backward compatibility (single-intent Brain.process unchanged)
- Workflow / step validation
"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from brain.brain import Brain
from brain.dispatcher import Dispatcher
from brain.errors import (
    DeskMindError,
    InvalidRequestError,
    WorkflowStepError,
)
from brain.registry import CapabilityRegistry
from brain.workflow import (
    STEP_RESULT,
    Workflow,
    WorkflowEngine,
    WorkflowStep,
)
from database.connection import Database


# ==================================================
# Helpers
# ==================================================

def make_fake_registry():
    """Registry with mock capabilities that record their calls."""
    registry = CapabilityRegistry()

    call_log = []

    class FakeCapability:
        def __init__(self, label, response):
            self.label = label
            self.response = response

        def execute(self, request, context=None):
            call_log.append({
                "label": self.label,
                "request": request,
                "context": dict(context) if context else {},
            })
            return self.response

    registry.register("step_a", lambda: FakeCapability("A", "result-A"))
    registry.register("step_b", lambda: FakeCapability("B", "result-B"))
    registry.register("step_c", lambda: FakeCapability("C", "result-C"))

    return registry, call_log


def make_failing_registry():
    """Registry with a capability that raises on execution."""
    registry = CapabilityRegistry()

    class FailingCapability:
        def execute(self, request, context=None):
            raise ValueError("Step failed on purpose")

    class OkCapability:
        def execute(self, request, context=None):
            return "ok"

    registry.register("fail_step", lambda: FailingCapability())
    registry.register("ok_step", lambda: OkCapability())

    return registry


# ==================================================
# Workflow / step validation
# ==================================================

def test_workflow_requires_name():
    try:
        Workflow("", [WorkflowStep("chat", "hi")])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty name")

    try:
        Workflow("   ", [WorkflowStep("chat", "hi")])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for whitespace name")
    print("Workflow name validation passed.")


def test_workflow_requires_steps():
    try:
        Workflow("test", [])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty steps")
    print("Workflow steps validation passed.")


def test_workflow_step_repr():
    step = WorkflowStep("notes", "list notes")
    assert "notes" in repr(step)
    assert "list notes" in repr(step)
    print("WorkflowStep repr passed.")


def test_workflow_repr():
    wf = Workflow("my-flow", [WorkflowStep("chat", "hi")])
    assert "my-flow" in repr(wf)
    assert "1 steps" in repr(wf)
    print("Workflow repr passed.")


# ==================================================
# Sequential execution
# ==================================================

def test_single_step_workflow():
    registry, call_log = make_fake_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    wf = Workflow("single", [WorkflowStep("step_a", "do something")])
    result = engine.run(wf)

    assert result["workflow"] == "single"
    assert len(result["results"]) == 1
    assert result["results"][0] == "result-A"
    assert len(call_log) == 1
    print("Single-step workflow passed.")


def test_multi_step_sequential():
    registry, call_log = make_fake_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    wf = Workflow("triple", [
        WorkflowStep("step_a", "first"),
        WorkflowStep("step_b", "second"),
        WorkflowStep("step_c", "third"),
    ])
    result = engine.run(wf)

    assert result["results"] == ["result-A", "result-B", "result-C"]
    assert len(call_log) == 3

    # Steps ran in order
    assert call_log[0]["label"] == "A"
    assert call_log[1]["label"] == "B"
    assert call_log[2]["label"] == "C"
    print("Multi-step sequential execution passed.")


# ==================================================
# Result propagation
# ==================================================

def test_result_propagation():
    registry, call_log = make_fake_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    wf = Workflow("propagation", [
        WorkflowStep("step_a", "first"),
        WorkflowStep("step_b", "second"),
    ])
    engine.run(wf)

    # First step has no previous result
    assert STEP_RESULT not in call_log[0]["context"]

    # Second step receives the first step's result
    assert call_log[1]["context"][STEP_RESULT] == "result-A"
    print("Result propagation passed.")


def test_custom_result_key():
    registry, call_log = make_fake_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    wf = Workflow("custom-key", [
        WorkflowStep("step_a", "first", result_key="my_key"),
        WorkflowStep("step_b", "second"),
    ])
    engine.run(wf)

    assert call_log[1]["context"]["my_key"] == "result-A"
    assert STEP_RESULT not in call_log[1]["context"]
    print("Custom result key passed.")


def test_context_preserved():
    registry, call_log = make_fake_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    ctx = {"existing_key": "existing_value"}
    wf = Workflow("ctx-test", [
        WorkflowStep("step_a", "first"),
        WorkflowStep("step_b", "second"),
    ])
    engine.run(wf, context=ctx)

    assert call_log[0]["context"]["existing_key"] == "existing_value"
    assert call_log[1]["context"]["existing_key"] == "existing_value"
    print("Context preservation passed.")


def test_context_not_mutated():
    registry, _ = make_fake_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    ctx = {"existing_key": "existing_value"}
    wf = Workflow("no-mutate", [
        WorkflowStep("step_a", "first"),
        WorkflowStep("step_b", "second"),
    ])
    engine.run(wf, context=ctx)

    # The caller's context dict should not have STEP_RESULT added
    assert STEP_RESULT not in ctx
    print("Context not mutated passed.")


def test_context_written_by_step_propagates():
    calls = []

    class ContextDispatcher:
        def dispatch(self, intent, request, context):
            calls.append(dict(context))
            if intent == "writer":
                context["written_by_step"] = "available"
                return "written"
            return context["written_by_step"]

    engine = WorkflowEngine(ContextDispatcher())
    wf = Workflow("context-chain", [
        WorkflowStep("writer", "write"),
        WorkflowStep("reader", "read"),
    ])

    result = engine.run(wf)

    assert result["results"] == ["written", "available"]
    assert calls[1]["written_by_step"] == "available"
    print("Capability context propagation passed.")


# ==================================================
# Failure handling
# ==================================================

def test_step_failure_stops_workflow():
    registry = make_failing_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    wf = Workflow("failing", [
        WorkflowStep("ok_step", "first"),
        WorkflowStep("fail_step", "second"),
        WorkflowStep("ok_step", "third"),
    ])

    try:
        engine.run(wf)
    except WorkflowStepError as exc:
        assert exc.workflow_name == "failing"
        assert exc.step_index == 1
        assert "Step failed" in exc.cause
    else:
        raise AssertionError("Expected WorkflowStepError")
    print("Step failure stops workflow passed.")


def test_step_failure_user_message():
    registry = make_failing_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    wf = Workflow("failing", [WorkflowStep("fail_step", "boom")])

    try:
        engine.run(wf)
    except WorkflowStepError as exc:
        assert "could not be completed" in exc.user_message
    else:
        raise AssertionError("Expected WorkflowStepError")
    print("Step failure user message passed.")


def test_first_step_failure():
    registry = make_failing_registry()
    engine = WorkflowEngine(Dispatcher(registry))

    wf = Workflow("fail-first", [
        WorkflowStep("fail_step", "only step"),
    ])

    try:
        engine.run(wf)
    except WorkflowStepError as exc:
        assert exc.step_index == 0
    else:
        raise AssertionError("Expected WorkflowStepError")
    print("First step failure passed.")


# ==================================================
# Backward compatibility -- Brain.process unchanged
# ==================================================

def test_brain_process_still_works():
    brain = Brain()

    with patch("capabilities.chat.ask_gemini", return_value="hello back"):
        result = brain.process("hello there")
    assert result == "hello back"
    print("Brain.process backward compatibility passed.")


def test_brain_process_empty_message():
    brain = Brain()
    try:
        brain.process("   ")
    except InvalidRequestError:
        pass
    else:
        raise AssertionError("Expected InvalidRequestError")
    print("Brain.process empty message still raises passed.")


def test_brain_process_notes_command():
    brain = Brain()
    result = brain.process("create note: workflow test note")
    assert "saved" in result.lower()
    print("Brain.process notes command passed.")


def test_brain_has_workflow_engine():
    brain = Brain()
    assert hasattr(brain, "workflow_engine")
    assert isinstance(brain.workflow_engine, WorkflowEngine)
    print("Brain has workflow_engine passed.")


def test_brain_run_workflow():
    brain = Brain()

    wf = Workflow("brain-flow", [
        WorkflowStep("notes", "create note: from workflow"),
        WorkflowStep("notes", "list notes"),
    ])
    result = brain.run_workflow(wf)

    assert result["workflow"] == "brain-flow"
    assert len(result["results"]) == 2
    assert "saved" in result["results"][0].lower()
    assert "from workflow" in result["results"][1]
    print("Brain.run_workflow passed.")


def test_brain_run_workflow_with_context():
    brain = Brain()

    wf = Workflow("ctx-flow", [
        WorkflowStep("notes", "list notes"),
    ])
    ctx = {"some_key": "some_value"}
    result = brain.run_workflow(wf, context=ctx)

    assert result["workflow"] == "ctx-flow"
    assert ctx == {"some_key": "some_value"}
    assert STEP_RESULT not in ctx
    print("Brain.run_workflow with context passed.")


# ==================================================
# Real capability integration
# ==================================================

def test_real_notes_workflow():
    """Create a note, then list notes -- the listing should include
    the note created in the first step.
    """
    brain = Brain()

    wf = Workflow("real-notes", [
        WorkflowStep("notes", "create note: workflow integration test"),
        WorkflowStep("notes", "list notes"),
    ])
    result = brain.run_workflow(wf)

    assert "saved" in result["results"][0].lower()
    assert "workflow integration test" in result["results"][1]
    print("Real notes workflow integration passed.")


def test_real_file_search_workflow():
    """File search with a real directory and context."""
    brain = Brain()

    with TemporaryDirectory() as directory:
        test_file = Path(directory) / "searchable.txt"
        test_file.write_text("findme keyword here")

        wf = Workflow("real-search", [
            WorkflowStep("file_search", "findme"),
        ])
        result = brain.run_workflow(
            wf,
            context={"search_directory": directory},
        )

        assert "searchable.txt" in result["results"][0]
    print("Real file search workflow integration passed.")


def main():
    test_workflow_requires_name()
    test_workflow_requires_steps()
    test_workflow_step_repr()
    test_workflow_repr()
    test_single_step_workflow()
    test_multi_step_sequential()
    test_result_propagation()
    test_custom_result_key()
    test_context_preserved()
    test_context_not_mutated()
    test_context_written_by_step_propagates()
    test_step_failure_stops_workflow()
    test_step_failure_user_message()
    test_first_step_failure()
    test_brain_process_still_works()
    test_brain_process_empty_message()
    test_brain_process_notes_command()
    test_brain_has_workflow_engine()
    test_brain_run_workflow()
    test_brain_run_workflow_with_context()
    test_real_notes_workflow()
    test_real_file_search_workflow()
    print("\nAll workflow tests passed.")


if __name__ == "__main__":
    main()
