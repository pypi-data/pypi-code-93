#!/usr/bin/env python3

import sys
import os
sys.path.append(os.getcwd())

import fuzzycompare

rc, maxerr, _ = fuzzycompare.file('query', 'reference', '1')
print(f"{True if rc == 0 else False}, maxerr:{maxerr}")