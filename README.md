# Skin Titan BINGIE MOD

Titan BINGIE MOD for Kodi Omega.

#IMPORTANT NOTE FOR USERS# 
Install the skin through the official titan bingie mod repository for updates and the supported addons required!
The content here is for developing purposes!
https://github.com/AchillesPunks/repository.titan.bingie.mod

Join the official thread for updates: https://forum.kodi.tv/showthread.php?tid=355993

Special Thanks to @marcelveldt and @cartman.dos for all of his work on the original code for Titan and Titan BINGIE skin & addons 
and everyone else who have helped or contributed in any way!

## Extended Movies and TV Shows hubs

The existing eight hub rows remain the default. To use up to 24 rows, enable **Extended Movies and TV Shows hubs (24 rows)** under Skin settings > Configure shortcuts. The skin reloads when this option changes.

Unlock hub widgets, open Movies or TV Shows, and use each row's existing widget picker to choose its source and label. For example, assign Continue Watching, Trending, New Releases and individual genre lists from the add-ons you already use. No provider or account is required by the skin change itself, and no personal feed choices are included.

Extended hubs load the first three rows, then prefetch two rows ahead as you move down. Configured rows that are empty or still loading remain reachable, including after gaps between configured rows. Other hubs and the Home layout keep their existing behaviour.

Turn the option off to return to eight rows. Additional row settings are retained for the next time you enable it.

## Optional TMDb New & Popular shelves

Under Skin settings > Configure shortcuts, choose **Apply TMDb New & Popular shelves** to configure New movies, New TV shows, Popular movies and Popular TV shows. This uses the existing TMDb Helper add-on and works without a Kodi video library. It is separate from the 24-row Movies and TV Shows option.

The preset asks before replacing the first four New & Popular rows. Existing library defaults remain until you apply it; other rows, hubs and views are preserved. You can edit the four rows with the normal widget picker afterwards. New titles are released within the last 180 days, with a minimum of 20 movie votes or 10 TV votes; Popular TV shows are ranked by popularity among shows aired in the last week.

Choose **Restore previous New & Popular shelves** to undo the preset. The previous labels, sources, targets and sorting are saved in `special://profile/addon_data/skin.titan.bingie.mod/new-popular-preset-backup.json`. Reapplying an unchanged preset keeps that backup; applying it after editing the rows saves their latest configuration instead. Keep this file private because custom source URLs can contain account information.
