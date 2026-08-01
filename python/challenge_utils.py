"""Test-support helper for loading per-challenge solution modules.

Every challenge keeps its solution in a file named ``stdlib.py`` (and sometimes
``scratch.py``). Those names repeat across challenge folders, so a *full*
``pytest`` run can't import them by bare name: ``sys.modules`` has a single
``stdlib`` slot, and the second challenge's ``from stdlib import ...`` would
resolve to whichever challenge's ``stdlib`` was imported first.

``load_solution`` sidesteps that by importing a challenge's sibling module under
a name derived from its folder, so every challenge's ``stdlib`` can coexist.

Importable because ``pyproject.toml`` puts ``python/`` on pytest's ``pythonpath``.
"""
import importlib.util
import sys
from pathlib import Path


def load_solution(test_file: str, module_name: str = "stdlib"):
    """Import ``<dir of test_file>/<module_name>.py`` under a folder-unique name.

    :param test_file: pass ``__file__`` from the calling test module.
    :param module_name: solution file to load, e.g. ``"stdlib"`` or ``"scratch"``.
    :returns: the loaded module object (access functions as attributes).
    """
    path = Path(test_file).resolve().parent / f"{module_name}.py"
    unique_name = f"_sol_{path.parent.name}_{module_name}"
    spec = importlib.util.spec_from_file_location(unique_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = module
    spec.loader.exec_module(module)
    return module
