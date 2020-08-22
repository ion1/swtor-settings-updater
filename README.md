# Star Wars: The Old Republic Settings Updater

A library to update the `*_PlayerGUIState.ini` settings for all your characters.

## Usage

* **Create a backup of `%LOCALAPPDATA%\SWTOR\swtor\settings`.**
* Run `pip install swtor-settings-updater`.
* Create a `my_settings.py` corresponding to the settings you want to apply
  to your characters (an example follows).
* Run the script.

```python
import logging
from swtor_settings_updater import Character, Chat, default_settings_dir


def my_settings(character, s):
    # swtor_settings_updater.Chat sets the ChatChannels, Chat_Custom_Channels
    # and ChatColors settings.
    chat = Chat()
    chn = chat.standard_channels

    chn.group.color = chn.ops.color

    chat.panel("General")
    other = chat.panel("Other")

    # Any channels not explicitly displayed on a panel will be displayed on
    # the first panel (General).
    other.display(
        # chn.trade,
        # chn.pvp,
        # chn.general,
        chn.emote,
        chn.yell,
        chn.officer,
        chn.guild,
        chn.say,
        chn.whisper,
        chn.ops,
        chn.ops_leader,
        chn.group,
        chn.ops_announcement,
        chn.ops_officer,
        # chn.combat_information,
        # chn.conversation,
        chn.character_login,
        chn.ops_information,
        # chn.system_feedback,
        chn.guild_information,
        chn.group_information,
        chn.error,
        # chn.server_admin,
    )

    if character.name not in ["Kai Zykken", "Plagueis"]:
        chat.custom_channel("Gsf")

        if character.server_id == "he4000":
            chat.custom_channel("Redleader")
            chat.custom_channel("Narwhal")

            myguild = chat.custom_channel("Myguild")
            myguild.color = chn.guild.color
            other.display(myguild)

        elif character.server_id in ["he3000", "he3001"]:
            chat.custom_channel("Endgame")

    chat.apply(s)

    s["Show_Chat_TimeStamp"] = "true"
    s["GUI_Current_Profile"] = "myprofile"
    s["GUI_WelcomeWindowIsOpen"] = "false"
    s["GUI_ShowCompletedReputations"] = "false"
    s["GUI_ShowUnstartedReputations"] = "false"
    s["GUI_ShowAlignment"] = "true"
    s["GUI_InvitesAsSocialMessage"] = "true"
    s["GUI_ShowCooldownText"] = "true"
    s["GUI_CooldownStyle"] = "3"
    s["GUI_GCDStyle"] = "1"
    s["GUI_MiniMapZoom"] = "0.842999994755"
    s["GUI_MapFadeTo"] = "50.0"
    s["GUI_GCConfirmOpenPack"] = "false"
    s["GUI_ConfirmAmplifierCharge"] = "false"
    s["GUI_InventoryAutoCloseBank"] = "false"
    s["GUI_InventoryAutoCloseVendor"] = "false"
    s["GUI_QuickslotLockState"] = "true"
    s["GUI_WhoListNumberInChat"] = "0"
    s["GroupFinder_Operation_InProgress"] = "true"
    s["GUI_CraftingMoveQuality"] = "6"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Character().update_all(default_settings_dir(), my_settings)
```
