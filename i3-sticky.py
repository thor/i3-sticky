#!/usr/bin/env python3
# vim:ts=4:sw=4:expandtab
import i3ipc
import json
import re

"""
Implements sticky groups, i.e., sticky tiling windows for i3.

A sticky group has a specific single-digit number (0–9). The actual sticky container must be marked with '_sticky_x' where »x« is the number of the sticky group. On each workspace the container should stick to, some placeholder container must exist and be tagged with '_sticky_x_y' where »x« is again the sticky group and »x« some suffix. The suffix will be ignored and can be freely chosen; it is simply required because marks must be unique within i3.

Run this script in the background and the sticky container will be swapped into the placeholder container whenever you switch workspaces.

(C) 2016 Ingo Bürk
Licensed under The MIT License (https://opensource.org/licenses/MIT), see LICENSE.

Requires i3 >= 4.14
"""

# TODO XXX Doesn't have to be restricted to numbers.
STICKY_GROUP = re.compile(r'^_sticky_(\d+)$')

def get_marks(i3):
    """ Returns a list of all currently used marks. """
    return json.loads(i3.message(i3ipc.MessageType.GET_MARKS, ''))

def get_groups(i3):
    """ Returns a list of sticky groups currently in use. """
    matches = [ STICKY_GROUP.match(mark) for mark in get_marks(i3) ]
    return [ match.group(1) for match in matches if match is not None ]

def swap(i3, _):
    """ Swaps each sticky container into the current workspace if possible. """

    # For each sticky group, try swapping the sticky container into this
    # workspace.
    for group in get_groups(i3):
        # TODO XXX For the (technically invalid) case of the placeholder being
        # on the same workspace as the sticky container, perhaps we should
        # first look up the sticky container by mark, check that it's on a
        # different workspace and then execute the command.
        i3.command('[workspace="__focused__" con_mark="^_sticky_%s_"] swap container with mark "_sticky_%s"' % (group, group))

if __name__ == '__main__':
    i3 = i3ipc.Connection()
    i3.on('workspace::focus', swap)
    i3.on('window::fullscreen_mode', swap)
    # TODO XXX Handle window::mark (does not yet exist)
    i3.main()
