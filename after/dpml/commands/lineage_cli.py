"""

TextAttack CLI main class
==============================

"""


# !/usr/bin/env python
import argparse

from .infer_trace_command import InferTraceCommand


def main():
    parser = argparse.ArgumentParser(
        "DPML CLI",
        usage="[python -m] dpml <command> [<args>]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(help="dpml command helpers")

    # Register commands
    InferTraceCommand.register_subcommand(subparsers)

    # Let's go
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)

    # Run
    func = args.func
    del args.func
    func.run(args)


if __name__ == "__main__":
    main()