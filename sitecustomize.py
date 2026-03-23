from __future__ import annotations

import sys
import warnings


def _running_unittests() -> bool:
    argv = " ".join(sys.argv).lower()
    return "unittest" in argv or "python -m unittest" in argv


if _running_unittests():
    warnings.filterwarnings("ignore", category=ResourceWarning, module=r"anyio(\..*)?$")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"httpx(\..*)?$")

