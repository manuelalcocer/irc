# -*- coding: utf-8 -*-
# icecast stats parser for weechat - ver 0.1
#
# nashgul <m.alcocer1978@gmail.com>   :-D
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
SCRIPT_DESC = 'icecast stats parser (usage: /%s)' % SCRIPT_COMMAND

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
            'strings' : ['url', 'streams', 'stream_options', 'format']
            #'integers' : ['time_delay']
            }
    # Available colors
    global colors
    colors = ['white' , 'black', 'blue', 'green', 'lighred', 'red',
            'magenta', 'brown', 'yellow', 'lightgreen', 'cyan',
            'lightcyan', 'lightblue', 'lightmagenta', 'darkgray', 'gray']

    if not config_file:
        return
    section = weechat.config_new_section(config_file, 'config', 0,0, '', '', '', '', '', '', '', '', '', '')
    config['url'] = weechat.config_new_option(config_file, section,
            'icecast_json_url', 'string', 'http directory for /status-json.xsl',
            '', 0, 0,
            'http://icecast.nashgul.com.es/status-json.xsl', 'http://icecast.nashgul.com.es/status-json.xsl', 1,
            '', '',
            'load_str_vars_cb', '',
            '', '')
    config['streams'] = weechat.config_new_option(config_file, section,
            'streams', 'string', 'mounts to show (without slash and separated by commas)',
            '', 0, 0,
            'nashgul', 'nashgul', 1,
            'check_mounts_cb', '',
            'load_str_vars_cb', '',
            '', '')
    config['stream_options'] = weechat.config_new_option(config_file, section,
            'stream_options', 'string', 'stream options to show',
            '', 0, 0,
            'url,artist,title,listeners', 'url,artist,title,listeners', 1,
            '', '',
            'load_str_vars_cb', '',
            '', '')
    config['format'] = weechat.config_new_option(config_file, section,
            'output_format', 'string', 'Output string format (%s: attribute, %\'color\'; i.e.: Now playing on %red%s: %blue%s - %s - %s)',
            '', 0, 0,
            '%redAhora suena en %cyan%s%yellow: %lightblue%s %yellow- %lightblue%s %yellow( %magentaOyentes%yellow: %lightblue%s %yellow)', '%lightredAhora suena en %cyan%s%yellow: %lightblue%s %yellow- %lightblue%s %yellow( %magentaOyentes%yellow: %lightblue%s %yellow)', 1,
            '', '',
            'load_str_vars_cb', '',
            '', '')

def check_mounts_cb(data_ptr, option_ptr, new_value):
    # checks if mount list contains spaces
    if len(new_value.split()) > 1:
        # error if mounts contain spaces
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
        create_dict(status_dict)
        if len(streams_dict) >= 1:
            # mounts available
            scroll_stats()
            show_stats(buffer_exec, streams_dict)
        else:
            # no mounts available
            no_mounts_message = 'No hay radios disponibles'
            weechat.command(buffer_exec, '/print %s' % no_mounts_message)
    return weechat.WEECHAT_RC_OK

def create_dict(status_dict):
    global streams_dict
    streams_dict = status_dict['server']['streams'].copy()

def show_stats(buffer_exec, streams_dict):
    for mount in streams_dict.keys():
        if mount.lstrip('/') in config_values['streams']:
            # shows stats only for streams added to config['streams']
            info = create_string(mount)
            weechat.command(buffer_exec, '/me %s' % info)

def create_string(mount):
    string = config_values['format']
    for color in colors:
        color_index = colors.index(color)
        color = '%' + color
        color_replace = u'\x03%d' % color_index
        string = string.replace(color, color_replace)
    values = []
    for value in config_values['stream_options'].split(','):
        values += [streams_dict.get(mount)[value]]
    values = tuple(values)
    string = string % values
    return string

def scroll_stats():
    if timer_ptr:
        stop_timer()
    window_size = weechat.window_get_integer(weechat.current_window(), 'win_width')
    string = ''
    for key in streams_dict.keys():
        string += key.decode('utf-8').lstrip('/') + ' => '
        for subkey, value in streams_dict[key].items():
            string += '%s: %s, ' % (subkey.decode('utf-8'), value.decode('utf-8'))

def stop_timer():
    weechat.unhook(timer_ptr)

if __name__ == '__main__' and import_ok:
    weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', '')
    initialize_config(SCRIPT_NAME)
    config_read()
    global timer_ptr
    timer_ptr = False
    # add icecast stats parser command
    weechat.hook_command(SCRIPT_COMMAND, SCRIPT_DESC, '', '', '', 'icecast_cmd_cb', '')
