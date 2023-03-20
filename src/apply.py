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

    dynamic_label = Gtk.Template.Child()
    apply_to_queue = Gtk.Template.Child()
    compress_button = Gtk.Template.Child()
    skip_button = Gtk.Template.Child()


    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.set_transient_for(parent)
        self.set_modal(True)

        self.build_ui()

    def build_ui(self):
        self.apply_to_queue.set_active(False)
        self.apply_to_queue.connect('toggled', self.on_apply_to_queue_toggled)

    def set_dynamic_label(self, filename):
        text = _("The file <b>{}</b> already exists.\n" \
            "Do you want to compress the image anyway?".format(filename))
        self.dynamic_label.set_markup(text)

    def on_apply_to_queue_toggled(self, widget):
        state = widget.get_active()
        self.parent.apply_to_queue = state
