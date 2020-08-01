from collections import OrderedDict
import dataclasses as dc
from itertools import chain, zip_longest
import regex
from typing import Set

from swtor_settings_updater.color import Color
from swtor_settings_updater.util import *

CUSTOM_CHANNEL_IXS = range(22, 28 + 1)
MAXIMUM_IX = 37

DEFAULT_COLOR = Color(238, 238, 0)


@dc.dataclass
class Channel:
    name: str
    ix: int
    color: Color = dc.field(default_factory=lambda: DEFAULT_COLOR.copy())


@dc.dataclass
class StandardChannels:
    # Global Channels
    trade: Channel = dc.field(
        default_factory=lambda: Channel("Trade", 7, (Color(179, 236, 255)))
    )
    pvp: Channel = dc.field(
        default_factory=lambda: Channel("PvP", 8, (Color(179, 236, 255)))
    )
    general: Channel = dc.field(
        default_factory=lambda: Channel("General", 6, (Color(179, 236, 255)))
    )

    # Player Channels
    emote: Channel = dc.field(
        default_factory=lambda: Channel("Emote", 2, (Color(255, 128, 34)))
    )
    yell: Channel = dc.field(
        default_factory=lambda: Channel("Yell", 1, (Color(255, 115, 151)))
    )
    officer: Channel = dc.field(
        default_factory=lambda: Channel("Officer", 11, (Color(255, 0, 255)))
    )
    guild: Channel = dc.field(
        default_factory=lambda: Channel("Guild", 10, (Color(130, 236, 137)))
    )
    say: Channel = dc.field(
        default_factory=lambda: Channel("Say", 0, (Color(179, 236, 255)))
    )
    whisper: Channel = dc.field(
        default_factory=lambda: Channel("Whisper", 3, (Color(165, 159, 243)))
    )
    ops: Channel = dc.field(
        default_factory=lambda: Channel("Ops", 12, (Color(239, 188, 85)))
    )
    ops_leader: Channel = dc.field(
        default_factory=lambda: Channel("Ops Leader", 29, (Color(255, 84, 0)))
    )
    group: Channel = dc.field(
        default_factory=lambda: Channel("Group", 9, (Color(29, 140, 254)))
    )
    ops_announcement: Channel = dc.field(
        default_factory=lambda: Channel("Ops Announcement", 33, (Color(160, 0, 0)))
    )
    ops_officer: Channel = dc.field(
        default_factory=lambda: Channel("Ops Officer", 13, (Color(49, 122, 60)))
    )

    # System Channels
    combat_information: Channel = dc.field(
        default_factory=lambda: Channel("Combat Information", 37, (Color(255, 102, 0)))
    )
    conversation: Channel = dc.field(
        default_factory=lambda: Channel("Conversation", 19, (Color(238, 238, 0)))
    )
    character_login: Channel = dc.field(
        default_factory=lambda: Channel("Character Login", 20, (Color(238, 238, 0)))
    )
    ops_information: Channel = dc.field(
        default_factory=lambda: Channel("Ops Information", 34, (Color(201, 46, 86)))
    )
    system_feedback: Channel = dc.field(
        default_factory=lambda: Channel("System Feedback", 18, (Color(238, 238, 0)))
    )
    guild_information: Channel = dc.field(
        default_factory=lambda: Channel("Guild Information", 36, (Color(31, 171, 41)))
    )
    group_information: Channel = dc.field(
        default_factory=lambda: Channel("Group Information", 35, (Color(187, 79, 210)))
    )

    # Not shown in the UI. The default General panel and any panel you
    # create displays these, but the default Other panel does not.
    error: Channel = dc.field(
        default_factory=lambda: Channel("Error", 15, (Color(255, 0, 0)))
    )
    server_admin: Channel = dc.field(
        default_factory=lambda: Channel("Server Admin", 17, (Color(255, 127, 127)))
    )

    def __iter__(self):
        return (getattr(self, f.name) for f in dc.fields(self))


class Chat:
    """Manage chat panels, custom channels and colors."""

    def __init__(self):
        self.standard_channels = StandardChannels()

        self.panels = OrderedDict()

        self.custom_channel_ixs_available = []
        for ix in CUSTOM_CHANNEL_IXS:
            self.custom_channel_ixs_available.append(ix)

        self.custom_channels = OrderedDict()

    def panel(self, name):
        """Create a chat panel."""
        name_lower = swtor_lower(name)

        if name_lower in self.panels:
            raise ValueError(f"Panel already exists: {name!r}")

        t = Panel(name)
        self.panels[name_lower] = t

        return t

    def custom_channel(self, name, password=None, id=None):
        """Create a custom chat channel."""
        name_lower = swtor_lower(name)

        if name_lower in self.custom_channels:
            raise ValueError(f"Custom channel already exists: {name!r}")

        if not self.custom_channel_ixs_available:
            raise RuntimeError("Maximum number of custom channels reached")
        ix = self.custom_channel_ixs_available.pop(0)

        cc = CustomChannel(name, ix, password=password, id=id)
        self.custom_channels[name_lower] = cc

        return cc

    def apply(self, settings):
        """Apply the chat settings to a configuration object."""
        settings["ChatChannels"] = self.panels_setting()
        settings["Chat_Custom_Channels"] = self.custom_channels_setting()
        settings["ChatColors"] = self.colors_setting()

    def panels_setting(self):
        """Compute the value for the panels setting (ChatChannels)."""
        if self.panels:
            panels = self.panels.values()
        else:
            # Ensure at least one panel exists.
            panels = [Panel("General")]

        # Add undisplayed channels (if any) to the first panel.
        undisplayed_ixs = self.undisplayed_channel_ixs()

        channels = []
        for num, (panel_orig, ixs) in enumerate(
            zip_longest(panels, [undisplayed_ixs]), start=1
        ):
            if ixs:
                panel = Panel(panel_orig.name, panel_orig.channel_ixs | ixs)
            else:
                panel = panel_orig
            channels.append(f"{num}.{panel.name}.{panel.channel_bitmask()};")
        return "".join(channels)

    def undisplayed_channel_ixs(self):
        """Compute the indices of channels not displayed on any panel."""
        ixs = set()

        for c in self.standard_channels:
            ixs.add(c.ix)

        for ix in CUSTOM_CHANNEL_IXS:
            ixs.add(ix)

        for panel in self.panels.values():
            ixs -= panel.channel_ixs

        return ixs

    def custom_channels_setting(self):
        """Compute the value for the Chat_Custom_Channels setting."""
        custom_channels = []
        for num, cc in enumerate(self.custom_channels.values(), start=1):
            password = "" if cc.password is None else cc.password
            custom_channels.append(f"{cc.name};{password};{num};{cc.id}")
        return ";".join(custom_channels)

    def colors_setting(self):
        """Compute the value for the ChatColors setting."""
        colors = [DEFAULT_COLOR.copy() for _ in range(MAXIMUM_IX + 1)]
        for c in chain(self.standard_channels, self.custom_channels.values()):
            colors[c.ix] = c.color
        return "".join(map(lambda c: f"{c.hex()};", colors))


@dc.dataclass
class Panel:
    name: str
    channel_ixs: Set[int] = dc.field(default_factory=set)

    # . and ; are separators.
    NAME_REGEX = regex.compile(f'[{regex_character_class(CP1252_PRINTABLE, ".;")}]+')

    def __post_init__(self):
        if not regex.fullmatch(Panel.NAME_REGEX, self.name):
            raise ValueError(f"Invalid name {self.name!r}")

    def display(self, *channels):
        """Display the given channel(s) on the panel."""
        for c in channels:
            self.channel_ixs.add(c.ix)

    def channel_bitmask(self):
        bitmask = 0
        for ix in self.channel_ixs:
            bitmask |= 1 << ix
        return bitmask


@dc.dataclass
class CustomChannel(Channel):
    password: str = None
    id: str = None

    NAME_REGEX = regex.compile(r"[A-Za-z0-9_]+")
    # Spaces are not allowed, ; is a separator, and "&<> seem to be encoded by
    # the game as XML entities (wat).
    PASSWORD_REGEX = regex.compile(
        f"""[{regex_character_class(CP1252_PRINTABLE, ' ;"&<>')}]+"""
    )
    ID_REGEX = regex.compile(r"usr\.[a-z0-9_]+")

    def __post_init__(self):
        if not regex.fullmatch(CustomChannel.NAME_REGEX, self.name):
            raise ValueError(f"Invalid name {self.name!r}")

        if self.password is not None and not regex.fullmatch(
            CustomChannel.PASSWORD_REGEX, self.password
        ):
            raise ValueError(f"Invalid password {self.password!r}")

        if self.id is not None and not regex.fullmatch(CustomChannel.ID_REGEX, self.id):
            raise ValueError(f"Invalid id {id!r}")

        if self.id is None:
            self.id = f"usr.{swtor_lower(self.name)}"
