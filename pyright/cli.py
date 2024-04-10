import sys
import logging
import subprocess
from typing import List, NoReturn, Union, Any

from . import node
from ._utils import install_pyright


__all__ = (
    "run",
    "main",
)

log: logging.Logger = logging.getLogger(__name__)


def main(args: List[str], **kwargs: Any) -> int:
    return run(*args, **kwargs).returncode


def run(
    *args: str, **kwargs: Any
) -> Union["subprocess.CompletedProcess[bytes]", "subprocess.CompletedProcess[str]"]:
    pkg_dir = install_pyright(args, quiet=None)
    script = pkg_dir / "index.js"
    if not script.exists():
        raise RuntimeError(f"Expected CLI entrypoint: {script} to exist")

    import os

    VENV = os.environ.get("VIRTUAL_ENV", None)
    deleted = False
    if VENV is not None:
        pathes = os.environ["PATH"].split(":")
        if pathes[0] == os.path.join(VENV, "bin"):
            deleted = True
            os.environ["PATH"] = ":".join(pathes[1:])

    output = node.run("node", str(script), *args, **kwargs)
    if deleted and VENV is not None:
        os.environ["PATH"] = ":".join([os.path.join(VENV, "bin")] + pathes)
    return output


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
