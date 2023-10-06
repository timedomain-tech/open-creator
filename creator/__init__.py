from .core import Creator
import sys


# to save a step, we can directly `import creator` and use its interface
sys.modules["creator"] = Creator()

