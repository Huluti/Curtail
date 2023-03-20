# apply.py
#
# Copyright 2019 Hugo Posnic
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

from gi.repository import Gtk, Gio


UI_PATH = '/com/github/huluti/Curtail/ui/'


@Gtk.Template(resource_path=UI_PATH + 'apply.ui')
class CurtailApplyDialog(Gtk.Dialog):
    __gtype_name__ = 'CurtailApplyDialog'

    file_list = Gtk.Template.Child()


    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.set_transient_for(parent)
        self.set_modal(True)

    def set_file_list(self, filenames):
        text = ''
        for filename in filenames:
            text = text + '- ' + filename + '\n'
        self.file_list.set_markup(text)
