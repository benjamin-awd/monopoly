import importlib
import logging
from pathlib import Path

from .base import BankBase
from .detector import BankDetector

# Auto-discover all bank modules in this package
_banks_dir = Path(__file__).parent
for _path in sorted(_banks_dir.rglob("*.py")):
    _name = _path.stem
    if _name.startswith("_") or _name in ("base", "detector"):
        continue
    _rel_parts = _path.relative_to(_banks_dir).with_suffix("").parts
    importlib.import_module("." + ".".join(_rel_parts), package=__name__)

banks: list[type[BankBase]] = list(BankBase.registry)

# Make bank classes importable directly from monopoly.banks
for _cls in banks:
    globals()[_cls.__name__] = _cls

logger = logging.getLogger(__name__)

__all__ = ["BankDetector", "BankBase"] + [_cls.__name__ for _cls in banks]
