from monopoly.statements import BaseStatement


class StubStatement(BaseStatement):
    """
    Minimal instantiable `BaseStatement` for tests of shared base behaviour.

    `BaseStatement` is abstract, so it cannot be instantiated directly. Tests
    covering shared behaviour (multiline handling, match processing, naming)
    need an instance without caring how safety checks work, so the one abstract
    method is stubbed with a canned pass.
    """

    def perform_safety_check(self) -> bool:
        return True
