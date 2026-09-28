from dataclasses import dataclass

@dataclass(frozen=True)
class TestProposal:
    path: str
    content: str
    reason: str

def propose_python_test(module_path: str, symbol: str) -> TestProposal:
    stem = module_path.rsplit("/", 1)[-1].removesuffix(".py")
    path = f"tests/test_{stem}_{symbol.lower()}.py"
    content = (
        f"from {module_path.removesuffix('.py').replace('/', '.')} import {symbol}\n\n"
        f"def test_{symbol.lower()}_behavior():\n"
        f"    # TODO: replace with behavior-specific assertions.\n"
        f"    assert {symbol} is not None\n"
    )
    return TestProposal(path, content, f"Starter test proposal for {symbol}.")
