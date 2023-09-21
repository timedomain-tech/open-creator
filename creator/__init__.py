from .schema.library import config as _config
from .creator import Creator

# to save a step, we can directly `import creator` and use its interface
create = Creator.create
save = Creator.save
search = Creator.search

config = _config

#   ___                      ____                _             
#  / _ \ _ __   ___ _ __    / ___|_ __ ___  __ _| |_ ___  _ __ 
# | | | | '_ \ / _ \ '_ \  | |   | '__/ _ \/ _` | __/ _ \| '__|
# | |_| | |_) |  __/ | | | | |___| | |  __/ (_| | || (_) | |   
#  \___/| .__/ \___|_| |_|  \____|_|  \___|\__,_|\__\___/|_|   
#       |_|                                                   