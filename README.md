# FF7R_text_mod_tools
Subtitle modding tools for FF7R (Final Fantasy VII Remake)
<img src = "image/ff7r_dualsub_sample.jpg" width=600>
## make_dualsub_mod.exe
`make_dualsub_mod.exe` is a tool for merging subtitle data.<br>
You can make a mod to display 2 languages in the game.<br>
<br>
I made [dualsub mod](https://www.nexusmods.com/finalfantasy7remake/mods/57) by this tool.<br>

### Usage

```
make_dualsub_mod.exe pak_dir lang1 lang2
```
- pak_dir: where unpacked files are (e.g. D:\quickbms\pakchunk0_s24-WindowsNoEditor)
- lang1: a language you want to display
- lang2: another language you want to display

If you run `make_dualsub_mod.exe`, a mod folder will be generated (like `dualsub_mod_US_JP`).

## uexp_to_json.exe
`uexp_to_json.exe` is a tool to export subtitle data as .json.<br>
This tool can use for only subtitle data (End\Content\GameContents\Text\\\*\\\*.uexp).<br>
Also, the output json file will not be compatible with other tools<br>
### Usage

```
make_dualsub_mod.exe uexp --out_dir="json"
```
- uexp: uexp file (e.g. D:\quickbms\pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text\US\010-MAKO1_TxtRes.uexp)
- --out_dir: save folder
