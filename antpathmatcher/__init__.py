__version__ = "1.0.1"
__all__ = (
    "__version__",
    "AntPathMatcher",
)

import logging

from antpathmatcher.antpathmatcher import AntPathMatcher

logger = logging.getLogger("antpathmatcher")
logger.addHandler(logging.NullHandler())
