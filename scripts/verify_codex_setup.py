#!/usr/bin/env python3
"""Compatibility entry point; now performs full asset validation."""
import sys
from assets import main

if __name__ == '__main__':
    sys.argv = [sys.argv[0], 'validate', *sys.argv[1:]]
    raise SystemExit(main())
