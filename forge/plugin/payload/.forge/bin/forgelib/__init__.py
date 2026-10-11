"""forgelib — shared library for the Forge scripts under .forge/bin/.

Pure standard library (Python >= 3.9). Every script does:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from forgelib import common

Modules:
  common   paths, JSON I/O, globbing, aliases, evidence/ledger/journal, git helpers
  status   the STATUS.json state machine (only writer of STATUS.json)
  gates    plan / handoff / verdict validators shared by hooks and forge-gate
  checks   runs binding.verify[] and brief checks, writes checks/ records (forge-check)
  hooks    the hook dispatcher (forge-hook)
"""

__version__ = "1.0.0"
