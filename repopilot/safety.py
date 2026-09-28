from dataclasses import dataclass

@dataclass(frozen=True)
class SafetyPolicy:
    allow_file_writes: bool = False
    allow_shell: bool = False
    allow_network: bool = False

    def check(self, action: str) -> bool:
        return {
            "write_file": self.allow_file_writes,
            "shell": self.allow_shell,
            "network": self.allow_network,
        }.get(action, False)

def require_approval(action: str, approved: bool) -> None:
    if not approved:
        raise PermissionError(f"Approval required for action: {action}")
