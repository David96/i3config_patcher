# i3config_patcher

This is a first, hacked together, version of a script to patch an i3 config file with the style of another one.
Keep in mind that it was written by me while sitting on the couch with a sore throat and a slight headache trying to stay awake with a lot of black tea.

I had the idea as I saw [Simon Hofmann](https://plus.google.com/u/0/106199511786508687538) on G+ posting about his new service http://tiling-styles.org/ (https://plus.google.com/106199511786508687538/posts/YF8dPe6xeDF).
The plan is to make it possible to browse the provided styles and merge them with the current config, taking only the style information.


## The current state:
It currently supports the following i3 style attributes:
```font, client.*, new_window, new_float, hide_edge_borders.```
If any of those is found in the new config, all occurences of it in the old one are replaced by the ones in the new one.

Furthermore it supports replacing whole blocks, currently set to the "bar" block - supports replacing nested blocks like the "colors" block inside "bar", too.

The script looks for variables in the new config and adds them right before a usage of them in the merged config.
Existing variables or variables not used in the newly added parts aren't replaced.


### Usage:
./i3config \<path/to/old/config\> \<path/to/old/config\>

# Important note!!!!
This script does **NO BACKUP** of your current config yet, moreover it **OVERRIDES** it with the new, merged one.

**YOU ARE RESPONSIBLE FOR CREATING THAT BACKUP YOUR SELF. YOU'RE RESPONSIBLE FOR ALL HARM THE PROVIDED SOFTWARE MIGHT CAUSE,
BE IT STARTING WWIII OR JUST BLOWING UP YOUR MACHINE!**
