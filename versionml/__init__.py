from .iteration import load, State
import sys

__version__ = "1.0.0"

RUN_ACTION = None

# Default cli argument added to user's python file.
if len(sys.argv) > 1:
	RUN_ACTION = sys.argv[1]


# State action method.
def state(): return State.action(RUN_ACTION)


# Methods exposed for using directly on code.
__all__ = [load, state]

