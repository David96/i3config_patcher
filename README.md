# i3config_patcher

This is a first, hacked together, version of a script to patch an i3 config file with the style of another one.
Keep in mind that it was written by me while ~~sitting on the couch with a sore throat and a slight headache trying to stay awake with a lot of black tea~~ (Update: I'm fine now, I still don't guarantee anything about the code quality).

I had the idea as I saw [Simon Hofmann](https://plus.google.com/u/0/106199511786508687538) on G+ posting about his new service http://tiling-styles.org/ (https://plus.google.com/106199511786508687538/posts/YF8dPe6xeDF).
The plan is to make it possible to browse the provided styles and merge them with the current config, taking only the style information.

## Documentation:
The documentation is generated by sphinx and can be found here: https://david96.github.io/

### Themes:
The script looks for themes in XDG_DATA_HOME/config_patcher. For details about structure etc. see https://david96.github.io/themes.html
Example themes can be found [here](https://github.com/David96/i3config_patcher/tree/master/examples). Copy them to XDG_DATA_HOME/config_patcher to test them.

### Backups:
The script backups files to the »originals« theme before patching them, see https://david96.github.io/themes.html for details.

### Usage:
./i3config \<theme-name\>

### Important note:
After being patched, your original config files can be found at XDG_DATA_HOME/config_patcher/originals (usually ~/.local/share/config_patcher/originals). If a new theme is applied, those config files are used to patch against, so instead of editing the config files of the actual software (e.g ~/.config/i3/config) you should edit the files in the originals theme (e.g. ~/.local/share/config_patcher/originals/i3/config) as the actual config files will be overwritten.

## The current state:
The script supports replacing occurrences of patterns in the old config with the ones in the new one
based on which block they're in.

The patterns to be replaced are currently set as:
```python
"root" : ["^\s*font\s", "^\s*client\.\w+", "^\s*new_window\s", "^\s*new_float\s", "^\s*hide_edge_borders\s"],
"bar": ["^\s*strip_workspace_numbers\s", "^\s*font\s", "^\s*mode\s"],
"colors": [".*"]
```
"root" representing every match without an associated block.

It is planned to make those patterns configurable within a config file.

The script looks for variables in the new config and adds them right before a usage of them in the merged config.
Existing variables or variables not used in the newly added parts aren't replaced.
If a variable used in the new config already exists in the old one the user is asked whether to override.


**YOU'RE RESPONSIBLE FOR ALL HARM THE PROVIDED SOFTWARE MIGHT CAUSE,
BE IT STARTING WWIII OR JUST BLOWING UP YOUR MACHINE!**
