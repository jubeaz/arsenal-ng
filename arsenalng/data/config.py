import configparser
import os
from os.path import dirname, abspath, expanduser, join
from ast import literal_eval

# Base paths
DATAPATH = join(dirname(dirname(abspath(__file__))), 'data')
BASEPATH = dirname(dirname(dirname(abspath(__file__))))
DEFAULT_CONFIG_PATH = join(DATAPATH, "arsenal-ng.conf")
CONFIG_PATH = expanduser("~/.arsenal-ng.conf")
HOMEPATH = expanduser("~")

DEFAULT_CHEATS_PATHS = [join(DATAPATH, "cheats")]
messages_error_missing_arguments = 'Error missing arguments'
# set lower delay to use ESC key (in ms)
os.environ.setdefault('ESCDELAY', '25')
os.environ['TERM'] = 'xterm-256color'

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
use_builtin_cheats = arsenal_config.getboolean("arsenal-ng", "use_builtin_cheats")
user_cheats_paths = literal_eval(arsenal_config.get("arsenal-ng", "user_cheats_paths"))

for p in user_cheats_paths:
    CHEATS_PATHS.append(expanduser(p))
if use_builtin_cheats:
    CHEATS_PATHS += DEFAULT_CHEATS_PATHS

savevarfile = expanduser(literal_eval(arsenal_config.get("arsenal-ng", "savevarfile")))
FORMATS = literal_eval(arsenal_config.get("arsenal-ng", "formats"))
EXCLUDE_LIST = literal_eval(arsenal_config.get("arsenal-ng", "exclude_list"))
FUZZING_DIRS = literal_eval(arsenal_config.get("arsenal-ng", "fuzzing_dirs"))
PREFIX_GLOBALVAR_NAME = arsenal_config.get("arsenal-ng", "prefix_globalvar_name")

BASIC_COLOR = arsenal_config.getint("colors", "basic_color")
COL1_COLOR = arsenal_config.getint("colors", "col1_color")
COL2_COLOR = arsenal_config.getint("colors", "col2_color")
COL3_COLOR = arsenal_config.getint("colors", "col3_color")
COL4_COLOR = arsenal_config.getint("colors", "col4_color")
COL5_COLOR = arsenal_config.getint("colors", "col5_color")
COL1_COLOR_SELECT = arsenal_config.getint("colors", "col1_color_select")
COL2_COLOR_SELECT = arsenal_config.getint("colors", "col2_color_select")
COL3_COLOR_SELECT = arsenal_config.getint("colors", "col3_color_select")
COL4_COLOR_SELECT = arsenal_config.getint("colors", "col4_color_select")
CURSOR_COLOR_SELECT = arsenal_config.getint("colors", "cursor_color_select")
PROMPT_COLOR = arsenal_config.getint("colors", "prompt_color")
INFO_NAME_COLOR = arsenal_config.getint("colors", "info_name_color")
INFO_DESC_COLOR = arsenal_config.getint("colors", "info_desc_color")
INFO_CMD_COLOR = arsenal_config.getint("colors", "info_cmd_color")
ARG_NAME_COLOR = arsenal_config.getint("colors", "arg_name_color")
