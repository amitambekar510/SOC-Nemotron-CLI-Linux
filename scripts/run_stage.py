"""Compatibility entry point for one CTI stage."""
import sys
try:
    from .run_chain import main
except ImportError:
    from run_chain import main

if __name__ == '__main__':
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        raise SystemExit(main(['--chain', sys.argv[1], *sys.argv[2:]]))
    raise SystemExit(main(sys.argv[1:]))
