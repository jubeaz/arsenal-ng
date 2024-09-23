import configparser
import os
from os.path import dirname, abspath, expanduser, join
from ast import literal_eval

# Base paths
DATAPATH = join(dirname(dirname(abspath(__file__))), "data")
BASEPATH = dirname(dirname(dirname(abspath(__file__))))
DEFAULT_CONFIG_PATH = join(DATAPATH, "arsenalng.conf")
CONFIG_PATH = expanduser("~/.arsenalng.conf")
HOMEPATH = expanduser("~")

DEFAULT_CHEATS_PATHS = [join(DATAPATH, "cheats")]
messages_error_missing_arguments = "Error missing arguments"
# set lower delay to use ESC key (in ms)
os.environ.setdefault("ESCDELAY", "25")
os.environ["TERM"] = "xterm-256color"

arsenal_default_config = configparser.ConfigParser()
arsenal_default_config.read(DEFAULT_CONFIG_PATH)

arsenal_config = configparser.ConfigParser()
arsenal_config.read(CONFIG_PATH)


# Update config in case default have been extended or use has removed required
config_updated = False
for section in arsenal_default_config.sections():
    if not arsenal_config.has_section(section):
        arsenal_config.add_section(section)
        config_updated = True
    for option in arsenal_default_config.options(section):
        if not arsenal_config.has_option(section, option):
            config_updated = True
            arsenal_config.set(section, option, arsenal_default_config.get(section, option))

if config_updated:
    with open(CONFIG_PATH, "w") as config_file:
        arsenal_config.write(config_file)

CHEATS_PATHS = []
use_builtin_cheats = arsenal_config.getboolean("arsenalng", "use_builtin_cheats")
user_cheats_paths = literal_eval(arsenal_config.get("arsenalng", "user_cheats_paths"))

for p in user_cheats_paths:
    CHEATS_PATHS.append(expanduser(p))
#CHEATS_PATHS = [expanduser(p) for p in user_cheats_paths]
if use_builtin_cheats:
    CHEATS_PATHS += DEFAULT_CHEATS_PATHS

savevarfile = expanduser(literal_eval(arsenal_config.get("arsenalng", "savevarfile")))
FORMATS = literal_eval(arsenal_config.get("arsenalng", "formats"))
EXCLUDE_LIST = literal_eval(arsenal_config.get("arsenalng", "exclude_list"))
FUZZING_DIRS = literal_eval(arsenal_config.get("arsenalng", "fuzzing_dirs"))
PREFIX_GLOBALVAR_NAME = arsenal_config.get("arsenalng", "prefix_globalvar_name")