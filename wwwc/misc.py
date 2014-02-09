"""misc functions for wilmaa tv"""

import sys
import logging as log


def die(rc, message):
    """print message and exit"""
    log.error(message)
    sys.exit(rc)



