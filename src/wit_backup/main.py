#!/usr/bin/env python3

# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

""" Main program entry points.
"""

import logging
import sys

from .args import (
    parse_args,
    validate_origin_target,
    validate_password,
)
from .constants import Mode
from .core import (
    backup,
    clean_target,
    restore,
)
from .log import (
    configure_logging,
)

logger = logging.getLogger(__name__)


def main () -> int: 
    """ Standard entrypoint
    """
    try:
        args = parse_args()
        validate_origin_target(args.origin, args.target)
        pwd = validate_password(args.password)

        configure_logging(
            target=args.target,
            verbose=args.verbose, 
            quiet=args.quiet, 
            log=args.log,
            log_file=args.log_file,
            )

        # Clean target if enabled, ensure target exists
        if args.delete:
            logger.debug("===== Delete option active; nuking target.")
            clean_target(args.target)

        if args.mode == Mode.RESTORE:
            restore(
                args.origin, 
                args.target,
                wary=args.wary,
                timestamp=args.timestamp,
                password=pwd,
                )
        else:
            backup(
                args.origin, 
                args.target, 
                wary=args.wary, 
                timestamp=args.timestamp,
                password=pwd,
                )

    except Exception:
        # unexpected issues; extra logging for debugging
        logger.exception("Unexpected error")
        return 1

    return 0


def run ():
    sys.exit(main())


if __name__ == "__main__":
    run()
