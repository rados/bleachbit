# vim: ts=4:sw=4:expandtab
# -*- coding: UTF-8 -*-

# BleachBit
# Copyright (C) 2008-2020 Andrew Ziem
# https://www.bleachbit.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Test case for application level functions
"""

import unittest.mock as mock
import os
import sys
import unittest
import time
import types
import winreg

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib, GObject
    from bleachbit.GUI import Bleachbit
    HAVE_GTK = True
except ImportError:
    HAVE_GTK = False

import bleachbit
from bleachbit import _
from bleachbit.GuiPreferences import PreferencesDialog
from bleachbit.Options import options, Options
from bleachbit import Cleaner, CleanerML
from bleachbit.Cleaner import backends
from windows.setup_py2exe import SHRED_REGEX_KEY
from tests import common

bleachbit.online_update_notification_enabled = False


@unittest.skipUnless(HAVE_GTK, 'requires GTK+ module')
class GUITestCase(common.BleachbitTestCase):
    """Test case for application level functions"""
    
    @classmethod
    def setUpClass(cls):
        cls.old_language = common.get_env('LANGUAGE')
        common.put_env('LANGUAGE', 'en')
        super(GUITestCase, GUITestCase).setUpClass()
        options.set('first_start', False)
        options.set('check_online_updates', False)  # avoid pop-up window

    @classmethod
    def tearDownClass(cls):
        super(GUITestCase, GUITestCase).tearDownClass()
        common.put_env('LANGUAGE', cls.old_language)
    
    #@common.skipUnlessWindows
    def test_windows_explorer_context_menu_command(self):
        def set_curdir_to_bleachbit():
            os.curdir = os.path.split(__file__)[0]
            os.curdir = os.path.split(os.curdir)[0]
            
        file_to_shred = self.mkstemp(prefix="file_to_shred_with_context_menu_command")
        self.assertExists(file_to_shred)
        options.set('delete_confirmation', False, commit=False)
        shred_command_key = '{}\\command'.format(SHRED_REGEX_KEY)
        shred_command_string = self.get_winregistry_value(winreg.HKEY_CLASSES_ROOT,  shred_command_key)
        
        if shred_command_string is None:
            shred_command_string = r"{} bleachbit.py --gui --no-uac --shred {}".format(sys.executable, file_to_shred)
            set_curdir_to_bleachbit()
        else:
            self.assertTrue('"%1"' in shred_command_string)
            shred_command_string = shred_command_string.replace('"%1"', file_to_shred)
        
        os.system(shred_command_string)
        self.assertNotExists(file_to_shred)