from __future__ import annotations

from collections import namedtuple, OrderedDict
from typing import Any, Iterable, List, Optional

from hypothesis import assume, given
import hypothesis.stateful as sta
import hypothesis.strategies as st
import pytest
import regex

from swtor_settings_updater.chat import (
    Channel,
    Chat,
    CUSTOM_CHANNEL_IXS,
    CustomChannel,
    MAXIMUM_CHANNEL_IX,
    Panel,
    UNUSED_CHANNEL_IXS,
)
from swtor_settings_updater.color import Color
from swtor_settings_updater.util.character_class import (
    CP1252_PRINTABLE,
    regex_character_class,
)
from swtor_settings_updater.util.swtor_case import swtor_lower, swtor_upper
from .test_color import valid_rgb


valid_color = valid_rgb().map(lambda rgb: Color(*rgb))

# See chat_channels.txt
all_channel_ixs = set(range(MAXIMUM_CHANNEL_IX + 1)) - set(UNUSED_CHANNEL_IXS)
default_colors = (
    "b3ecff;ff7397;ff8022;a59ff3;eeee00;eeee00;b3ecff;b3ecff;b3ecff;1d8cfe;"
    "82ec89;ff00ff;efbc55;317a3c;eeee00;ff0000;eeee00;ff7f7f;eeee00;eeee00;"
    "eeee00;eeee00;eeee00;eeee00;eeee00;eeee00;eeee00;eeee00;eeee00;ff5400;"
    "eeee00;eeee00;eeee00;a00000;c92e56;bb4fd2;1fab29;ff6600;"
)
num_custom_channels = len(CUSTOM_CHANNEL_IXS)

valid_channel_ix = st.sampled_from(list(all_channel_ixs))
valid_panel_name = st.from_regex(Panel.NAME_REGEX, fullmatch=True)
valid_custom_channel_name = st.from_regex(CustomChannel.NAME_REGEX, fullmatch=True)
valid_custom_channel_password = st.one_of(
    st.none(), st.from_regex(CustomChannel.PASSWORD_REGEX, fullmatch=True)
)
valid_custom_channel_id = st.one_of(
    st.none(), st.from_regex(CustomChannel.ID_REGEX, fullmatch=True)
)


class ChatRules(sta.RuleBasedStateMachine):
    chat: Chat
    panels: OrderedDict[str, PanelSetting]
    custom_channels: OrderedDict[str, CustomChannelsSetting]
    colors: List[Color]

    def __init__(self) -> None:
        super(ChatRules, self).__init__()

        self.chat = Chat()

        self.panels = OrderedDict()
        self.custom_channels = OrderedDict()
        self.colors = parse_colors(default_colors)

    panel_refs = sta.Bundle("panels")
    custom_channel_refs = sta.Bundle("custom_channels")

    # Will be initialized once and stay fixed.
    standard_channel_refs = sta.Bundle("standard_channels")

    @sta.initialize(target=standard_channel_refs)
    def init_standard_channels(self) -> Any:
        return sta.multiple(*self.chat.standard_channels)

    # Panels

    @sta.invariant()
    def expected_number_of_panels(self) -> None:
        assert len(self.chat.panels) == len(self.panels)

    @sta.rule(target=panel_refs, name=valid_panel_name)
    def new_panel(self, name: str) -> Panel:
        name_lower = swtor_lower(name)
        assume(name_lower not in self.panels.keys())

        num = len(self.panels) + 1
        self.panels[name_lower] = PanelSetting(num, name, set())

        return self.chat.panel(name)

    @sta.rule(panel_c=panel_refs)
    def existing_panel(self, panel_c: Panel) -> None:
        with pytest.raises(ValueError):
            self.chat.panel(panel_c.name)
        with pytest.raises(ValueError):
            self.chat.panel(swtor_lower(panel_c.name))
        with pytest.raises(ValueError):
            self.chat.panel(swtor_upper(panel_c.name))

    # Custom channels

    @sta.invariant()
    def expected_number_of_custom_channels(self) -> None:
        assert len(self.chat.custom_channels) == len(self.custom_channels)
        assert len(self.chat.custom_channels) <= num_custom_channels

    @sta.precondition(lambda self: len(self.custom_channels) < num_custom_channels)
    @sta.rule(
        target=custom_channel_refs,
        name=valid_custom_channel_name,
        password=valid_custom_channel_password,
        id=valid_custom_channel_id,
    )
    def new_custom_channel(
        self, name: str, password: Optional[str], id: Optional[str]
    ) -> CustomChannel:
        name_lower = swtor_lower(name)
        assume(name_lower not in self.custom_channels)

        num = len(self.custom_channels) + 1
        self.custom_channels[name_lower] = CustomChannelsSetting(
            name,
            password if password is not None else "",
            num,
            id if id is not None else f"usr.{name_lower}",
        )

        return self.chat.custom_channel(name, password=password, id=id)

    @sta.precondition(lambda self: len(self.custom_channels) == num_custom_channels)
    @sta.rule(
        name=valid_custom_channel_name,
        password=valid_custom_channel_password,
        id=valid_custom_channel_id,
    )
    def new_custom_channel_too_many(
        self, name: str, password: Optional[str], id: Optional[str]
    ) -> None:
        name_lower = swtor_lower(name)
        assume(name_lower not in self.custom_channels)

        with pytest.raises(RuntimeError):
            self.chat.custom_channel(name, password=password, id=id)

    @sta.rule(custom_channel_c=custom_channel_refs)
    def existing_custom_channel(self, custom_channel_c: CustomChannel) -> None:
        with pytest.raises(ValueError):
            self.chat.custom_channel(custom_channel_c.name)
        with pytest.raises(ValueError):
            self.chat.custom_channel(swtor_lower(custom_channel_c.name))
        with pytest.raises(ValueError):
            self.chat.custom_channel(swtor_upper(custom_channel_c.name))

    # Displaying channels

    @sta.rule(
        panel_c=panel_refs,
        channels_c=st.lists(st.one_of(standard_channel_refs, custom_channel_refs)),
    )
    def panel_display_channel(
        self, panel_c: Panel, channels_c: Iterable[Channel]
    ) -> None:
        for channel_c in channels_c:
            self.panels[swtor_lower(panel_c.name)].channel_ixs.add(channel_c.ix)

        panel_c.display(*channels_c)

    # Setting colors

    @sta.rule(
        channel_c=st.one_of(standard_channel_refs, custom_channel_refs),
        color=valid_color,
    )
    def replace_channel_color(self, channel_c: Channel, color: Color) -> None:
        self.colors[channel_c.ix] = color
        channel_c.color = color

    @sta.rule(
        channel_c=st.one_of(standard_channel_refs, custom_channel_refs),
        color=valid_color,
    )
    def mutate_channel_color(self, channel_c: Channel, color: Color) -> None:
        self.colors[channel_c.ix].r = color.r
        self.colors[channel_c.ix].g = color.g
        self.colors[channel_c.ix].b = color.b
        channel_c.color.r = color.r
        channel_c.color.g = color.g
        channel_c.color.b = color.b

    @sta.rule(
        source_channel_c=st.one_of(standard_channel_refs, custom_channel_refs),
        target_channel_c=st.one_of(standard_channel_refs, custom_channel_refs),
    )
    def link_channel_color(
        self, source_channel_c: Channel, target_channel_c: Channel
    ) -> None:
        self.colors[target_channel_c.ix] = self.colors[source_channel_c.ix]
        target_channel_c.color = source_channel_c.color

    # Applying the settings

    @sta.invariant()
    def apply_applies_settings(self) -> None:
        settings = {"foo": "bar"}
        self.chat.apply(settings)

        assert set(settings.keys()) == {
            "foo",
            "ChatChannels",
            "Chat_Custom_Channels",
            "ChatColors",
        }

        parse_panels(settings["ChatChannels"])
        parse_custom_channels(settings["Chat_Custom_Channels"])
        parse_colors(settings["ChatColors"])

    # The panels setting (ChatChannels)

    @sta.precondition(lambda self: not self.panels)
    @sta.invariant()
    def channels_setting_has_a_default_panel(self) -> None:
        setting = self.chat.panels_setting()
        # note(f"panels_setting: {setting!r}")

        panels_s = parse_panels(setting)

        assert panels_s == [PanelSetting(1, "General", all_channel_ixs)]

    @sta.precondition(lambda self: self.panels)
    @sta.invariant()
    def channels_setting_is_correct(self) -> None:
        setting = self.chat.panels_setting()
        # note(f"channels_setting: {setting!r}")

        panels_s = parse_panels(setting)

        assert len(panels_s) == len(self.panels)

        displayed_ixs = set()
        for panel_s in panels_s:
            displayed_ixs |= panel_s.channel_ixs

        missing_ixs = all_channel_ixs - displayed_ixs
        extra_ixs = displayed_ixs - all_channel_ixs

        assert not missing_ixs, "A channel is not displayed in any panel"
        assert not extra_ixs, "An impossible channel is displayed in a panel"

        for (panel_s, panel) in zip(panels_s, self.panels.values()):
            assert panel_s.number == panel.number
            assert panel_s.name == panel.name

            missing_ixs = panel.channel_ixs - panel_s.channel_ixs
            extra_ixs = panel_s.channel_ixs - panel.channel_ixs

            assert not missing_ixs, "Fewer channels are displayed than expected"

            # The first panel should have the explicitly displayed channel
            # and possibly more. The other panels should only have the
            # explicitly displayed channels.
            if panel.number != 1:
                assert not extra_ixs, "More channels are displayed than expected"

    # The Chat_Custom_Channels setting

    @sta.invariant()
    def custom_channels_setting_is_correct(self) -> None:
        setting = self.chat.custom_channels_setting()
        # note(f"custom_channels_setting: {setting!r}")

        custom_channels_s = parse_custom_channels(setting)

        assert len(custom_channels_s) == len(self.custom_channels)

        for cc_s, cc in zip(custom_channels_s, self.custom_channels.values()):
            assert cc_s == cc

    # The ChatColors setting

    @sta.invariant()
    def colors_setting_is_correct(self) -> None:
        setting = self.chat.colors_setting()
        # note(f"colors_setting: {setting!r}")

        colors_s = parse_colors(setting)

        assert colors_s == self.colors


TestChat = ChatRules.TestCase


PanelSetting = namedtuple("PanelSetting", ["number", "name", "channel_ixs"])


def parse_panels(setting: str) -> List[PanelSetting]:
    match = regex.fullmatch(
        r"""
            (?:
                (?P<number>[0-9]+)\.
                (?P<name>[^.;]+)\.
                (?P<channel_bitmask>[0-9]+);
            )+
        """,
        setting,
        regex.VERBOSE,
    )
    if match is None:
        raise ValueError(f"Failed to parse ChatChannels: {setting!r}")
    result = []
    for number_s, name, channel_bitmask_s in zip(
        match.captures("number"),
        match.captures("name"),
        match.captures("channel_bitmask"),
    ):
        channel_bitmask = int(channel_bitmask_s)
        channel_ixs = set()
        n = 0
        while channel_bitmask >> n:
            if (channel_bitmask >> n) & 1:
                channel_ixs.add(n)
            n += 1

        result.append(PanelSetting(int(number_s), name, channel_ixs))
    return result


CustomChannelsSetting = namedtuple(
    "CustomChannelsSetting", ["name", "password", "number", "id"]
)


def parse_custom_channels(setting: str) -> List[CustomChannelsSetting]:
    match = regex.fullmatch(
        r"""
            (?:
                (?:\A|;)(?P<name>[^;]+)
                ;(?P<password>[^;]*)
                ;(?P<number>[0-9]+)
                ;(?P<id>[^;]+)
            )*
        """,
        setting,
        regex.VERBOSE,
    )
    if match is None:
        raise ValueError(f"Failed to parse Chat_Custom_Channels: {setting!r}")
    result = []
    for name, password, number, id in zip(
        match.captures("name"),
        match.captures("password"),
        match.captures("number"),
        match.captures("id"),
    ):
        result.append(CustomChannelsSetting(name, password, int(number), id))
    return result


def parse_colors(setting: str) -> List[Color]:
    match = regex.fullmatch(
        r"""
            (?:
                (?P<r>[0-9a-fA-F]{2})
                (?P<g>[0-9a-fA-F]{2})
                (?P<b>[0-9a-fA-F]{2});
            ){38}
        """,
        setting,
        regex.VERBOSE,
    )
    if match is None:
        raise ValueError(f"Failed to parse ChatColors: {setting!r}")
    return [
        Color(int(r, 16), int(g, 16), int(b, 16))
        for r, g, b in zip(
            match.captures("r"), match.captures("g"), match.captures("b")
        )
    ]


def invalid_string(
    invalid_strategy: Any, valid_strategy: Any, empty_is_invalid: bool = False
) -> Any:
    strategy = st.builds(
        lambda pre, sep, post: f"{pre}{sep}{post}",
        st.one_of(st.just(""), valid_strategy),
        invalid_strategy,
        st.one_of(st.just(""), valid_strategy),
    )
    if empty_is_invalid:
        return st.one_of(st.just(""), strategy)
    else:
        return strategy


invalid_channel_ix = st.one_of(
    st.sampled_from(UNUSED_CHANNEL_IXS),
    st.integers(max_value=-1),
    st.integers(min_value=MAXIMUM_CHANNEL_IX + 1),
)


@given(valid_channel_ix)
def test_channel_accepts_valid_ix(ix: int) -> None:
    assert Channel("", ix).ix == ix


@given(invalid_channel_ix)
def test_channel_rejects_invalid_ix(ix: int) -> None:
    with pytest.raises(ValueError):
        Channel("", ix)


@given(valid_panel_name)
def test_panel_accepts_valid_name(name: str) -> None:
    assert Panel(name).name == name


@given(
    invalid_string(
        st.from_regex(
            f"(?:[.;]|[^{regex_character_class(CP1252_PRINTABLE)}])+", fullmatch=True
        ),
        valid_panel_name,
        empty_is_invalid=True,
    )
)
def test_panel_rejects_invalid_name(name: str) -> None:
    with pytest.raises(ValueError):
        Panel(name)


@given(
    valid_custom_channel_name,
    valid_channel_ix,
    st.one_of(st.none(), valid_custom_channel_password),
    st.one_of(st.none(), valid_custom_channel_id),
)
def test_custom_channel_accepts_valid_parameters(
    name: str, ix: int, password: Optional[str], id: Optional[str]
) -> None:
    cc = CustomChannel(name, ix, password=password, id=id)
    assert cc.name == name
    assert cc.ix == ix
    assert cc.password == password
    if id is None:
        assert cc.id == f"usr.{swtor_lower(name)}"
    else:
        assert cc.id == id


@given(
    invalid_string(
        st.from_regex("[^A-Za-z0-9_]+", fullmatch=True),
        valid_custom_channel_name,
        empty_is_invalid=True,
    ),
    valid_channel_ix,
)
def test_custom_channel_rejects_invalid_name(name: str, ix: int) -> None:
    with pytest.raises(ValueError):
        CustomChannel(name, ix)


@given(valid_custom_channel_name, invalid_channel_ix)
def test_custom_channel_rejects_invalid_ix(name: str, ix: int) -> None:
    with pytest.raises(ValueError):
        Channel(name, ix)


@given(
    valid_custom_channel_name,
    valid_channel_ix,
    invalid_string(
        st.from_regex(
            f"""(?:[ ;"&<>]|[^{regex_character_class(CP1252_PRINTABLE)}])+""",
            fullmatch=True,
        ),
        valid_custom_channel_password,
        empty_is_invalid=True,
    ),
)
def test_custom_channel_rejects_invalid_password(
    name: str, ix: int, password: str
) -> None:
    with pytest.raises(ValueError):
        CustomChannel(name, ix, password=password)


@given(
    valid_custom_channel_name,
    valid_channel_ix,
    st.one_of(
        st.from_regex(r"[a-z0-9_]+", fullmatch=True),  # Missing the usr. prefix
        invalid_string(
            st.from_regex(
                f"""(?:[ ;"&<>'!]|[^{regex_character_class(CP1252_PRINTABLE)}])+""",
                fullmatch=True,
            ),
            st.from_regex(r"[a-z0-9_]+", fullmatch=True),
            empty_is_invalid=True,
        ).map(lambda s: f"usr.{s}"),
    ),
)
def test_custom_channel_rejects_invalid_id(name: str, ix: int, id: str) -> None:
    with pytest.raises(ValueError):
        CustomChannel(name, ix, id=id)
