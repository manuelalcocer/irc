# -*- coding: utf-8 -*-
# icecast stats parser for weechat - ver 0.1
#
# nashgul <m.alcocer1978@gmail.com>   :-D
# freenode: #debian-es-offtopic, #birras



# Compatibility with non-ascii chars on weechat
import sys
reload(sys)
sys.setdefaultencoding('utf8')

SCRIPT_NAME = 'tscroll'
SCRIPT_AUTHOR = 'nashgul'
SCRIPT_VERSION = '0.1'
SCRIPT_LICENSE = 'GPL2'

SCRIPT_COMMAND = 'tscroll'
SCRIPT_DESC = 'Scroll function for title in current window' % SCRIPT_NAME

import_ok = True
try:
    import weechat
except:
    print 'This script must be run under WeeChat.'
    print 'Get Weechat now at: http://www.weechat.org/'
    import_ok = False

def scroll_topic_cb(data_ptr, buffer_ptr, args):
    # enciende el scroll
    window_size = weechat.window_get_integer(weechat.current_window(), 'win_width')
    texto = u'\x03c12' + 'Texto de prueba'
    display_vect = [' '] * window_size
    texto_vect = []
    for character in texto:
        texto_vect += [character]
    global display_fin
    display_fin = display_vect + texto_vect
    timer_ptr = weechat.hook_timer(300, 0, len(display_fin), 'scroll_cb', '')
    return weechat.WEECHAT_RC_OK

def scroll_cb(data_ptr, remaining_calls):
    display_fin.pop(0)
    cadena = ''
    for character in display_fin:
        cadena += character
    weechat.buffer_set(weechat.current_buffer(), 'title', cadena)
    return weechat.WEECHAT_RC_OK

def main():
    weechat.register('tscroll', 'nashgul', '0.1', 'GPL2.0', 'scroll title bar', '', '')
    weechat.hook_command('tscroll', 'title scroll', '', '', '', 'scroll_topic_cb', '')

if __name__ == '__main__':
    main()

