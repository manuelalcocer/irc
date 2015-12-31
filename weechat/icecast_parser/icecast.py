# -*- coding: utf-8 -*-
# icecast stats parser for weechat - ver 0.1
#
# nashgul <m.alcocer1978@gmail.com>
# freenode: #debian-es-offtopic, #birras



# Compatibility with non-ascii chars on weechat
import sys
reload(sys)
sys.setdefaultencoding("utf8")

SCRIPT_NAME = 'icecast'
SCRIPT_AUTHOR = 'nashgul'
SCRIPT_VERSION = '0.1'
SCRIPT_LICENSE = 'GPL2'

SCRIPT_COMMAND = 'ice'
SCRIPT_DESC = 'icecast stats parser (usage: /%s)' % SCRIPT_NAME

import_ok = True

try:
    import weechat
except:
    print 'This script must be run under WeeChat.'
    print 'Get Weechat now at: http://www.weechat.org/'
    import_ok = False

try:
    from urllib2 import urlopen
    from json import loads

except ImportError as message:
    print 'Missing package(s) for %s: %s' % (SCRIPT_NAME, message)
    import_ok = False

def fetch_vars():
    webpage = config_values['url']
    return webpage

def icecast_cmd_cb(data_ptr, buffer_exec, args):
    webpage = fetch_vars()
    try:
        status_page = urlopen(webpage)
        radio_online = True
    except:
        radio_online = False
    if radio_online:
        status_dict = loads(status_page.read())
        global streams_list
        streams_list = status_dict['server']['streams']
        if streams_list:
            # mounts available
            show_stats()
        else:
            # no mounts available
            pass
    return weechat.WEECHAT_RC_OK

def show_stats():
    pass

def initialize_config(name):
    global config
    global config_file
    config = {}
    config_file = weechat.config_new(name, 'my_config_reload_cb', '')
    if not config_file:
        return
    section = weechat.config_new_section(config_file, 'config', 0,0, '', '', '', '', '', '', '', '', '', '')
    config['url'] = weechat.config_new_option(config_file, section,
            'icecast_json_url', 'string', 'http directory for /status-json.xsl',
            '', 0, 0, '', '', 1,
            '', '',
            'load_vars_cb', '',
            '', '')
    config['streams'] = weechat.config_new_option(config_file, section,
            'streams', 'string', 'mounts to show (without slash and separated by commas)',
            '', 0, 0, '', '', 1,
            'check_mounts_cb', '',
            'load_vars_cb', '',
            '', '')

def check_mounts_cb(data_ptr, option_ptr, new_value):
    if ',' in new_value:
        mounts = new_value.split(',')
        for mount in mounts:
            if mount.startswith('/') or mount.endswith('/'):
                return 0
        return 1

def load_vars_cb(data_ptr, option_ptr):
    global config_values
    config_values = {}
    for key, pointer in config.items():
        config_values[key] = weechat.config_string(pointer)
    return weechat.WEECHAT_RC_OK

def my_config_reload_cb():
    return weechat.config_reload(config_file)

def config_read():
    return weechat.config_read(config_file)

if __name__ == '__main__' and import_ok:
    weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_LICENSE, '', '')
    initialize_config(SCRIPT_NAME)
    config_read()
    # add icecast stats parser command
    weechat.hook_command(
            SCRIPT_COMMAND,
            SCRIPT_DESC,
            '',
            '',
            '',
            'icecast_cmd_cb',
            '')


