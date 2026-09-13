import re
from pathlib import Path

VERSION_RE = re.compile(r"^##\s+v?(\d+\.\d+\.\d+)")
BULLET_RE = re.compile(r"^[-*]\s+(.+)$")
INLINE_BACKTICK_RE = re.compile(r"`([^`]*)`")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
BOLD_RE = re.compile(r"\*\*([^*]*)\*\*")


def _clean(line):
    line = LINK_RE.sub(r"\1", line)
    line = BOLD_RE.sub(r"\1", line)
    line = INLINE_BACKTICK_RE.sub(r"\1", line)
    return line.strip()


def _changelog_path():
    candidates = [
        Path(__file__).resolve().parent / "CHANGELOG.md",
        Path(__file__).resolve().parent.parent / "CHANGELOG.md",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def load_release_notes():
    notes = []
    current = None
    try:
        with open(_changelog_path(), encoding="utf-8") as changelog:
            for line in changelog:
                version_match = VERSION_RE.match(line)
                if version_match:
                    current = {
                        "version": version_match.group(1),
                        "changes": [],
                    }
                    notes.append(current)
                    continue
                if current is not None:
                    bullet_match = BULLET_RE.match(line)
                    if bullet_match:
                        current["changes"].append(_clean(bullet_match.group(1)))
    except OSError:
        return []
    return notes


def _version_key(version):
    return tuple(int(part) for part in version.split("."))


def release_notes_since(last_version):
    if not last_version:
        return list(RELEASE_NOTES)
    try:
        key = _version_key(last_version)
    except ValueError:
        return list(RELEASE_NOTES)
    return [
        release
        for release in RELEASE_NOTES
        if _version_key(release["version"]) > key
    ]


RELEASE_NOTES = load_release_notes()
