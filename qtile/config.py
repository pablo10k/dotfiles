# -*- coding: utf-8 -*-
import os
import re
import socket
import subprocess
from libqtile.config import KeyChord, Key, Screen, Group, Drag, Click, Match
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook, extension
#from libqtile.widget import Battery
from libqtile.lazy import lazy
from typing import List

from math import log
from typing import Tuple

import psutil

from libqtile.log_utils import logger
from libqtile.widget import base


class Net(base.ThreadedPollText):
    """
    Displays interface down and up speed


    Widget requirements: psutil_.

    .. _psutil: https://pypi.org/project/psutil/
    """
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ('format', '{interface}: {down} \u2193\u2191 {up}',
         'Display format of down-/upload speed of given interfaces'),
        ('interface', None, 'List of interfaces or single NIC as string to monitor, \
            None to displays all active NICs combined'),
        ('update_interval', 1, 'The update interval.'),
        ('use_bits', False, 'Use bits instead of bytes per second?'),
    ]

    def __init__(self, **config):
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(Net.defaults)
        if not isinstance(self.interface, list):
            if self.interface is None:
                self.interface = ["all"]
            elif isinstance(self.interface, str):
                self.interface = [self.interface]
            else:
                raise AttributeError("Invalid Argument passed: %s\nAllowed Types: List, String, None" % self.interface)
        self.stats = self.get_stats()

    def convert_b(self, num_bytes: float) -> Tuple[float, str]:
        """Converts the number of bytes to the correct unit"""
        factor = 1000.0

        if self.use_bits:
            letters = ["b", "kb", "Mb", "Gb", "Tb", "Pb", "Eb", "Zb", "Yb"]
            num_bytes *= 8
        else:
            letters = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

        if num_bytes > 0:
            power = int(log(num_bytes) / log(factor))
            power = max(min(power, len(letters) - 1), 0)
        else:
            power = 0

        converted_bytes = num_bytes / factor**power
        unit = letters[power]

        return converted_bytes, unit

    def get_stats(self):
        interfaces = {}
        if self.interface == ["all"]:
            net = psutil.net_io_counters(pernic=False)
            interfaces["all"] = {'down': net[1], 'up': net[0]}
            return interfaces
        else:
            net = psutil.net_io_counters(pernic=True)
            for iface in net:
                down = net[iface].bytes_recv
                up = net[iface].bytes_sent
                interfaces[iface] = {'down': down, 'up': up}
            return interfaces

    def _format(self, down, down_letter, up, up_letter):
        max_len_down = 7 - len(down_letter)
        max_len_up = 7 - len(up_letter)
        down = '{val:{max_len}.2f}'.format(val=down, max_len=max_len_down)
        up = '{val:{max_len}.2f}'.format(val=up, max_len=max_len_up)
        return down[:max_len_down], up[:max_len_up]

    def poll(self):
        ret_stat = []
        try:
            for intf in self.interface:
                new_stats = self.get_stats()
                down = new_stats[intf]['down'] - \
                    self.stats[intf]['down']
                up = new_stats[intf]['up'] - \
                    self.stats[intf]['up']

                down = down / self.update_interval
                up = up / self.update_interval
                down, down_letter = self.convert_b(down)
                up, up_letter = self.convert_b(up)
                down, up = self._format(down, down_letter, up, up_letter)
                self.stats[intf] = new_stats[intf]
                ret_stat.append(
                    self.format.format(
                        **{
                            'interface': intf,
                            'down': down + down_letter,
                            'up': up + up_letter
                        }))

            return " ".join(ret_stat)
        except Exception as excp:
            logger.error('%s: Caught Exception:\n%s',
                         self.__class__.__name__, excp)
mod = "mod4"
myTerminal = "alacritty"
myBrowser = "sidekick-browser"
myConfig = "/home/pablo/.config/qtile/config.py"

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "Tab", lazy.layout.next(),
        desc="Move window focus to other window"),
        
    # Switch focus to specific monitors
    Key([mod], "7",
             lazy.to_screen(0),
             desc='Keyboard focus to monitor 1'
             ),
    Key([mod], "8",
             lazy.to_screen(1),
             desc='Keyboard focus to monitor 2'
             ),
	# Floating / Unfloating
	Key([mod], "f",
             lazy.window.toggle_floating(),
             desc='toggle floating'
             ),
	Key([mod, "shift"], "m",
             lazy.window.toggle_fullscreen(),
             desc='toggle fullscreen'
             ),
    
    
    # Stack controls
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "shift"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "shift"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "shift"], "j", lazy.layout.grow_down(),
        desc="Grow window down"),
    Key([mod, "shift"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),
    
    Key([mod, "shift"], "Return", lazy.spawn(myTerminal), desc="Launch terminal"),

    # Toggle between different layouts as defined below
    Key([mod], "space", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "c", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "shift"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "shift"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "p", lazy.spawncmd(),
        desc="Spawn a command using a prompt widget"),    
        
    ###### GROUPS #####
    # Notes
	Key([mod], "1", lazy.group["Notes"].toscreen(),
		desc="Switch to group {}".format("")),
	Key([mod, "shift"], "1", lazy.window.togroup("Notes"),
		desc="move focused window to group {}".format("")),
	
	# Browser
	Key([mod], "2", lazy.group["Browser"].toscreen(),
		desc="Switch to group {}".format("")),
	Key([mod, "shift"], "2", lazy.window.togroup("Browser"),
		desc="move focused window to group {}".format("")),
	
	# Projects
	Key([mod], "3", lazy.group["Projects"].toscreen(),
		desc="Switch to group {}".format("")),
	Key([mod, "shift"], "3", lazy.window.togroup("STUFF"),
		desc="move focused window to group {}".format("")),
	
	# Stuff
	Key([mod], "3", lazy.group["Stuff"].toscreen(),
		desc="Switch to group {}".format("")),
	Key([mod, "shift"], "3", lazy.window.togroup("Stuff"),
		desc="move focused window to group {}".format("")),
		
	## My own aps
	Key([mod, "control"], "a",
			lazy.spawn(myTerminal + "alsamixer"),
			desc="Launch alsamixer volume controler"
			),
	#Key([mod, ""])
]

groups = [Group("Notes"), Group("Browser"), Group("Projects"), Group("Stuff")]

layout_theme = {"border_width": 4,
                "margin": 6,
                "border_focus": "e1acff",
                "border_normal": "1D2330"
                }

layouts = [
	layout.MonadTall(**layout_theme),
    layout.Columns(border_focus_stack='#d75f5f'),
    layout.Max(),
    layout.MonadTall(**layout_theme),
    layout.Max(**layout_theme),
    layout.Tile(shift_windows=True, **layout_theme),
    layout.Stack(num_stacks=2),
    layout.TreeTab(
         font = "Ubuntu",
         fontsize = 10,
         sections = ["FIRST", "SECOND"],
         section_fontsize = 11,
         bg_color = "141414",
         active_bg = "90C435",
         active_fg = "000000",
         inactive_bg = "384323",
         inactive_fg = "a0a0a0",
         padding_y = 5,
         section_top = 10,
         panel_width = 320
         ),
    layout.Floating(**layout_theme)
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]



colors = [["#282c34", "#282c34"], # panel background
          ["#434758", "#434758"], # background for current screen tab
          ["#ffffff", "#ffffff"], # font color for group names
          ["#ff5555", "#ff5555"], # border line color for current tab
          ["#8d62a9", "#8d62a9"], # border line color for other tab and odd widgets
          ["#668bd7", "#668bd7"], # color for the even widgets
          ["#e1acff", "#e1acff"]] # window name

widget_defaults = dict(
    font="Hack Regular",
    fontsize = 12,
    padding = 12,
    background=colors[0]
)
extension_defaults = widget_defaults.copy()


prompt = "Launch: " 

screens = [
    Screen(
        top=bar.Bar(
            widgets=[
			               
				 widget.Battery(
					font = "Hack Bold",
					fontsize = 15,
					discharge_char = " ",
					charge_char = " ",
					full_char = " ",
					notify_below = 14,
					format = ' {char}{percent:2.0%}',
					background = "f72585", # ~~
					padding = 0,
					update_interval = 10,
                ),
                
                widget.TextBox(
					font = "Hack",
					fontsize = 37,
					text = "",
					foreground = "f72585", # Same that the background of ~~
					padding = 0,
					background = "7209b7"
					
                ),
                widget.WidgetBox(widgets=[
						
						widget.GroupBox(
							fontsize = 12,
							#margin_y = 3,
							#margin_x = 0,
							
							#padding_y = 5,
							#padding_x = 3,
							borderwidth = 2, # Barrita bajo el nombre del grupo
							
							active = colors[2], # Text
							inactive = colors[4], # Text
							rounded = False,
							
							highlight_color = "7209b7",
							highlight_method = "line",
							this_current_screen_border = colors[2], # Same
							this_screen_border = colors[4],
							
							other_current_screen_border = colors[2],
							other_screen_border = colors[0],
							
							foreground = colors[2],
							background = "7209b7" # Same					         
						)], 
						fontsize  = 20,
						text_closed = "  ",
						text_open = "  ",
						background = "7209b7",
						
						
					),
                
                widget.TextBox(
					font = "Hack",
					fontsize = 26,
					text = "",
					foreground = "7209b7",
					padding = 0,
					background = "3a0ca3"
                ),
                widget.WindowCount(
					fontsize = 15,
					background = "3a0ca3",
					text_format = " {num}"
                ),                
                widget.Prompt(
					prompt = prompt,
					font = "Hack Bold",
					padding = 10,
					foreground = "f72585",
					#foreground = colors[3],
					background = "3a0ca3",
                ),
                
                widget.TextBox(
					font = "Hack",
					fontsize = 26,
					text = "",
					foreground = "3a0ca3",
					padding = 0,
					background = "4361EE",
					opacity = 0
					
                ),
                
                widget.Pomodoro(
					font = "Hack Bold",
					fontsize = 20,
					background = "4361EE", # fondo azul
					
					color_active = colors[3], # Letras rojas
					color_break = "35E95F", # Letras verdes del break
					color_inactive = colors[2], # Letras blancas
					
					notification_on = False,
					
					prefix_inactive = "",
					prefix_active = " ", ## You are here
					prefix_paused = " PAUSED"
					
					
                ),
                widget.TextBox(
					font = "Hack",
					fontsize = 26,
					text = "",
					foreground = "4361EE",
					padding = 0,
					background = colors[0],
					
                ),
				
                #widget.WindowTabs(font="Hack Bold", background=colors[0],),
                
                widget.Spacer(),
                
                ###### RIGHT SIDE OF PANEL ######
                
                #widget.CurrentLayout(),
                #widget.Net(interface='wlp3s0'),
                
                
                widget.Wallpaper(
					directory="/home/pablo/wallpapers/",
					random_selection = True,
					
					),
                
                widget.TextBox(
					font = "Hack",
					fontsize = 26,
					text = "",
					foreground = "7209B7",
					padding = 1,
					background = colors[0],
				),
                
                widget.TextBox(
					text = "",
					fontsize = 30,
					background = "7209B7",
					padding = 2
                ),
                
                widget.Net(
					interface='wlp3s0', 
					graph_color = "F72585", 
					fill_color = "3A0CA3", 
					background="7209B7", 
					border_color="7209B7", 
					line_width=3, 
					margin_x=3, 
					margin_y=7,
					
					format = " {down}  {up}",

					
					),

                #widget.Systray(background="7209B7", icon_size=20, padding=6),
				
                widget.TextBox(
					font = "Hack",
					fontsize = 26,
					text = "",
					foreground = "F72585",
					padding = 1,
					background = "7209B7",
                ),
                widget.Clock(format='%a %d %H:%M:%S', background = "F72585", font = "Hack Bold"), 
					
				widget.TextBox(
					font = "Hack",
					fontsize = 26,
					text = "",
					foreground = colors[0],
					padding = 1,
					background = "F72585"
                ),
				
				widget.QuickExit(
					fontsize = 27,
					default_text = "",
					countdown_format = "{}",
					foreground = "F72585"
				),
				
            ],
            size=30,
            background=colors[0],
            opacity = 0.4,
        ),
	),
    
  
        Screen( ## Second monitor ##
           top=bar.Bar(
              widgets=[
                widget.GroupBox(
                    highlight_method='block',
                    inactive='999999',
            fontsize=11
                ),
                widget.Sep(),
                widget.WindowName(),
               ],
        size=24,
            background='#000000',
        ),
    ),
]
    

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod, "shift"], "Button1", lazy.window.toggle_floating())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None  # WARNING: this is deprecated and willh to & move focused window to group be removed soon
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False

floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    Match(wm_type='utility'),
    Match(wm_type='notification'),
    Match(wm_type='toolbar'),
    Match(wm_type='splash'),
    Match(wm_type='dialog'),
    Match(wm_class='file_progress'),
    Match(wm_class='confirm'),
    Match(wm_class='dialog'),
    Match(wm_class='download'),
    Match(wm_class='error'),
    Match(wm_class='notification'),
    Match(wm_class='splash'),
    Match(wm_class='toolbar'),
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
])
auto_fullscreen = True
focus_on_window_activation = "smart"

@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser('~')
    subprocess.call([home + '/.config/qtile/autostart.sh'])


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
