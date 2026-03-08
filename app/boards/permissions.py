from dataclasses import dataclass

# Permission names
PERM_BOARD_VIEW = "board.view"
PERM_BOARD_UPDATE = "board.update"
PERM_BOARD_DELETE = "board.delete"
PERM_BOARD_MANAGE_MEMBERS = "board.manage_members"
PERM_TAG_MANAGE = "tag.manage"
PERM_TASK_CREATE = "task.create"
PERM_TASK_UPDATE = "task.update"
PERM_TASK_DELETE = "task.delete"


@dataclass
class PermissionContext:
    """
    Context object used during permission checks.

    Holds the current board and role involved in the permission evaluation.

    The type hints use forward references ("Board", "Role") to avoid
    circular imports between entities. The actual imports are placed
    inside a TYPE_CHECKING block so they are only evaluated by static
    type checkers (e.g. mypy, pyright) and not at runtime.
    """
    
    board: "Board"  # actual Board instance
    role: "Role"    # actual Role instance


# Late imports for type checking / runtime without circular issues
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.entities.board import Board
    from app.entities.role import Role
