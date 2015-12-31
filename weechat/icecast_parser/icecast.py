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

def initialize_config(name):
    global config
    config = {}

    global config_file
    config_file = weechat.config_new(name, 'my_config_reload_cb', '')

    global config_values
    config_values = {}

    global config_keys
    config_keys = {
            'strings' : ['url', 'streams', 'stream_options'],
            'integers' : ['time_delay']
            }

    if not config_file:
        return

    section = weechat.config_new_section(config_file, 'config', 0,0, '', '', '', '', '', '', '', '', '', '')
    config['url'] = weechat.config_new_option(config_file, section,
            'icecast_json_url', 'string', 'http directory for /status-json.xsl',
            '', 0, 0, '', '', 1,
            '', '',
            'load_str_vars_cb', '',
            '', '')
    config['streams'] = weechat.config_new_option(config_file, section,
            'streams', 'string', 'mounts to show (without slash and separated by commas)',
            '', 0, 0, '', '', 1,
            'check_mounts_cb', '',
            'load_str_vars_cb', '',
            '', '')
    config['stream_options'] = weechat.config_new_option(config_file, section,
            'stream_options', 'string', 'stream options to show',
            '', 0, 0,
            'artist,title,listeners', 'artist,title,listeners', 1,
            '', '',
            'load_str_vars_cb', '',
            '', '')
    config['time_delay'] = weechat.config_new_option(config_file, section,
            'time_delay', 'integer', 'time delay between info show when streams > 1',
            '', 0, 0, '', '', 1,
            '', '',
            'load_int_vars_cb', '',
            '', '')

def check_mounts_cb(data_ptr, option_ptr, new_value):
    # checks if mount list contains spaces
    if len(new_value.split()) > 1:
        # error if mounts contain space
        return 0

    # prepares to check individually
    if ',' in new_value:
        mounts = new_value.split(',')
    else:
        mounts = new_value
    
    # checks mounts individually
    for mount in mounts:
        if mount.startswith('/') or mount.endswith('/'):
            # error if mount contains slashes
            return 0
        elif len(mount.split()) > 1:
            # error if mount contains space
            return 0
    # return ok if no errors in mount list
    return 1

def load_str_vars_cb(data_ptr, option_ptr):
    for key in config_keys['strings']:
        pointer = config[key]
        config_values[key] = weechat.config_string(pointer)
    return weechat.WEECHAT_RC_OK

def load_int_vars_cb(data_ptr, option_ptr):
    for key in config_keys['integer']:
        pointer = config[key]
        config_values[key] = weechat.config_string(pointer)
    return weechat.WEECHAT_RC_OK

def my_config_reload_cb():
    return weechat.config_reload(config_file)

def config_read():
    return weechat.config_read(config_file)

def icecast_cmd_cb(data_ptr, buffer_exec, args):
    try:
        status_page = urlopen(config_values['url'])
        radio_online = True
    except:
        radio_online = False
    if radio_online:
        status_dict = loads(status_page.read())
        global streams_dict
        streams_dict = status_dict['server']['streams'].copy()
        if len(streams_dict) >= 1:
            # mounts available
            show_stats(buffer_exec, streams_dict)
        else:
            # no mounts available
            no_mounts_message = 'No hay radios disponibles'
            weechat.command(buffer_exec, '/print %s' % no_mounts_message)
    return weechat.WEECHAT_RC_OK

def show_stats(buffer_exec, streams_dict):
    for mount in streams_dict.keys():
        if mount.lstrip('/') in config_values['streams']:
            info = create_string(mount)
            weechat.command(buffer_exec, '/print %s' % info)

def create_string(mount):
    counter = 0
    for option in config_values['stream_options'].split(','):
        if counter != 0:
            string = string + ' - ' + streams_dict.get(mount)[option]
        else:
            string = streams_dict.get(mount)[option]
        counter += 1
    return string

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


