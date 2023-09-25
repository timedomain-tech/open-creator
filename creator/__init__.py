from .schema.library import config as _config
from .core import Creator
from .cli import cli


# to save a step, we can directly `import creator` and use its interface
create = Creator.create
save = Creator.save
search = Creator.search

config = _config
cli = cli

