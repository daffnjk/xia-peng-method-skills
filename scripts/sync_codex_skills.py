#!/usr/bin/env python3
"""Deprecated: .agents/skills is canonical; never copy 04_skills over it."""
import argparse
from assets import build
from assetlib import AssetError, Catalog

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--export', action='store_true')
    args = parser.parse_args()
    try:
        catalog = Catalog()
        if args.export:
            build(catalog)
            print('Exported dist/runtime; canonical Skills were not modified.')
        else:
            print('PASS: canonical Skills validated; 04_skills is no longer an editing source.')
    except (AssetError, OSError, ValueError) as exc:
        raise SystemExit(f'FAIL: {exc}')
