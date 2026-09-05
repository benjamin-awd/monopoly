from monopoly.statements import BaseStatement


class ConcreteStatement(BaseStatement):
    """
    Minimal concrete statement for tests exercising `BaseStatement` itself.

    `BaseStatement` is abstract, so it cannot be instantiated directly. Tests
    covering shared behaviour (multiline handling, match processing, naming)
    need an instance without caring how safety checks work.
    """

    def perform_safety_check(self) -> bool:
        return True
