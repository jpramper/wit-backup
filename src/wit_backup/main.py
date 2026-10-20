#!/usr/bin/env python3

# Copyright 2026 Juan Pablo Ramirez
# SPDX-License-Identifier: MIT

import logging

from .constants import Mode
from .args import (
    parse_args, 
    validate_origin_target,
)
from .core import (
    clean_target,
    backup,
    restore,
)
from .log import (
    configure_logging,
)


def main () -> int: # pragma: no cover
    """ Standard entrypoint
    """
    try:
        args = parse_args()
        validate_origin_target(args.origin, args.target)

        configure_logging(
            target=args.target,
            verbose=args.verbose, 
            quiet=args.quiet, 
            log=args.log,
            log_file=args.log_file,
            )

        # Clean target if enabled, ensure target exists
        if args.delete:
            logging.debug("===== Delete option active; nuking target.")
            clean_target(args.target)

        if args.mode == Mode.RESTORE:
            restore(
                args.origin, 
                args.target,
                wary=args.wary,
                timestamp=args.timestamp,
                )
        else:
            backup(
                args.origin, 
                args.target, 
                wary=args.wary, 
                timestamp=args.timestamp
                )

    except Exception as e:
        # unexpected issues; extra logging for debugging
        logging.exception("Unexpected error")
        return 1

    return 0


def run (): # pragma: no cover
    exit(main())


if __name__ == "__main__": # pragma: no cover
    run()
