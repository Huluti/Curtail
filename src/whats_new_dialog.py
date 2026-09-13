from gi.repository import Gtk, Adw, GLib

from .release_notes import RELEASE_NOTES, release_notes_since


class WhatsNewDialog(Adw.Dialog):
    def __init__(self, version, last_version="", **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("What's New"))
        self.set_content_width(420)
        self.set_content_height(480)

        headerbar = Adw.HeaderBar()
        close_button = Gtk.Button(
            icon_name="window-close-symbolic", valign=Gtk.Align.CENTER
        )
        close_button.add_css_class("flat")
        close_button.connect("clicked", lambda *_: self.close())
        headerbar.pack_end(close_button)

        label = Gtk.Label(
            wrap=True,
            selectable=True,
            hexpand=True,
            halign=Gtk.Align.START,
            max_width_chars=45,
            margin_top=12,
            margin_bottom=12,
            margin_start=18,
            margin_end=18,
        )
        label.set_markup(self._build_markup(version, last_version))

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_child(label)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.append(headerbar)
        content.append(scrolled)
        self.set_child(content)

    @staticmethod
    def _build_markup(current_version, last_version):
        notes = (
            release_notes_since(last_version) if last_version else RELEASE_NOTES
        )
        parts = []
        for release in notes:
            version = GLib.markup_escape_text(release["version"])
            if release["version"] == current_version:
                header = f"<b><big>{version}</big></b>"
            else:
                header = f'<span size="small">{version}</span>'
            changes = "\n".join(
                f"• {GLib.markup_escape_text(change)}"
                for change in release["changes"]
            )
            parts.append(f"{header}\n{changes}")
        return "\n\n".join(parts)
