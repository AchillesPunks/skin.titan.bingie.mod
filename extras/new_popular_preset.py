"""Apply or restore the optional TMDb shelves without resetting other hubs."""

import json
import os
import sys
import tempfile

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs


SKIN = "skin.titan.bingie.mod"
FIELDS = ("label", "path", "target", "sortby", "sortorder")
ROWS = (510, 520, 530, 540)
KEYS = tuple("bingiehub-new-{}.{}".format(row, field)
             for row in ROWS for field in FIELDS)
FEEDS = (
    "info=discover&tmdb_type=movie&with_id=True&sort_by=primary_release_date.desc"
    "&primary_release_date.gte=t-180&primary_release_date.lte=t-0&vote_count.gte=20",
    "info=discover&tmdb_type=tv&sort_by=first_air_date.desc"
    "&first_air_date.gte=t-180&first_air_date.lte=t-0&vote_count.gte=10",
    "info=popular&tmdb_type=movie",
    "info=discover&tmdb_type=tv&sort_by=popularity.desc"
    "&air_date.gte=t-7&air_date.lte=t-0&vote_count.gte=10",
)


def current_values():
    return {key: xbmc.getInfoLabel("Skin.String({})".format(key)) for key in KEYS}


def read_backup(path):
    with open(path, encoding="utf-8") as handle:
        values = json.load(handle)
    if not isinstance(values, dict) or set(values) != set(KEYS):
        raise ValueError("Unexpected shelf backup keys")
    if not all(isinstance(value, str) for value in values.values()):
        raise ValueError("Unexpected shelf backup values")
    return values


def save_backup(path, values):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory,
                                     prefix=".new-popular-", delete=False) as handle:
        temporary = handle.name
        try:
            json.dump(values, handle, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def set_values(values):
    for key in KEYS:
        value = values[key]
        if value:
            quoted = value.replace("\\", "\\\\").replace('"', '\\"')
            command = 'Skin.SetString({},"{}")'.format(key, quoted)
        else:
            command = "Skin.Reset({})".format(key)
        xbmc.executebuiltin(command, wait=True)
    if current_values() != values:
        raise RuntimeError("Shelf settings did not match")


def main(mode="apply"):
    if mode not in ("apply", "restore") or xbmc.getSkinDir() != SKIN:
        return
    addon = xbmcaddon.Addon(SKIN)
    localize = addon.getLocalizedString
    dialog = xbmcgui.Dialog()
    heading = localize(320032)
    backup = xbmcvfs.translatePath(
        "special://profile/addon_data/{}/new-popular-preset-backup.json".format(SKIN))
    try:
        if mode == "restore":
            if not os.path.isfile(backup):
                dialog.ok(heading, localize(320252))
                return
            values = read_backup(backup)
        else:
            values = {key: "" for key in KEYS}
            for row, label_id, feed in zip(ROWS, range(320253, 320257), FEEDS):
                prefix = "bingiehub-new-{}.".format(row)
                values[prefix + "label"] = localize(label_id)
                values[prefix + "target"] = "videos"
                values[prefix + "path"] = (
                    "plugin://plugin.video.themoviedb.helper/?" + feed + "&widget=true")
        if not dialog.yesno(heading, localize(320250 if mode == "restore" else 320249)):
            return
        if mode == "apply":
            current = current_values()
            if current != values or not os.path.isfile(backup):
                save_backup(backup, current)
            else:
                read_backup(backup)  # Keep the original undo state when reapplying.
        set_values(values)
        dialog.notification(heading, localize(320258 if mode == "restore" else 320257))
    except (OSError, ValueError, TypeError, RuntimeError) as error:
        xbmc.log("BINGIE New & Popular preset: {}".format(type(error).__name__), xbmc.LOGERROR)
        dialog.ok(heading, localize(320251))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "apply")
