from brain.bootstrap import register_capabilities
from brain.registry import CapabilityRegistry


def main():
    registry = CapabilityRegistry()
    register_capabilities(registry)

    first = registry.get("chat")
    second = registry.get("chat")

    assert first is second
    print("Bootstrap registration and lazy singleton creation work.")


if __name__ == "__main__":
    main()
