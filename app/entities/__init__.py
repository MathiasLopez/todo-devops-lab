"""
Convenience imports to ensure SQLAlchemy mappers are registered.
Importing this package will load all entity modules so that
relationship() string lookups (e.g., "RolePermission") resolve correctly.
"""
from .boardColumn import BoardColumn  # noqa: F401
from .priority import Priority  # noqa: F401
from .tag import Tag  # noqa: F401
from .role import Role  # noqa: F401
from .permission import Permission  # noqa: F401
from .rolePermission import RolePermission  # noqa: F401
