import os
import warnings

os.environ.setdefault("AGENTFORGE_RATE_LIMIT_ENABLED", "false")
warnings.simplefilter("ignore", ResourceWarning)
