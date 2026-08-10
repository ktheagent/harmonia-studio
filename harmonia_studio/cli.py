import argparse, json
from .diagnostics import diagnostics
from .version import VERSION

def main(argv=None):
    p = argparse.ArgumentParser(prog="harmonia")
    p.add_argument("--version", action="store_true")
    p.add_argument("--diagnostics", action="store_true")
    args = p.parse_args(argv)
    if args.version:
        print(VERSION)
        return 0
    if args.diagnostics:
        print(json.dumps(diagnostics(), indent=2))
        return 0
    p.print_help()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
