# FF7R_text_mod_tools
Subtitle modding tools for FF7R (Final Fantasy VII Remake)<br>

<img src = "image/ff7r_dualsub_sample.jpg" width=600>

There are 3 tools I made.

- make_dualsub_mod.exe: Merges (or swaps) subtitle data between 2 languages.
- uexp_to_json.exe: Exports subtitle data as .json.
- json_to_uexp.exe: Swaps subtitle data with .json.

## make_dualsub_mod.exe
`make_dualsub_mod.exe` is a tool for merging (or swapping) subtitle data.<br>
You can make a mod to display 2 languages in the game.<br>
<br>
I made [dualsub mod](https://www.nexusmods.com/finalfantasy7remake/mods/57) by this tool.<br>

### Usage

```
make_dualsub_mod.exe pak_dir lang1 lang2 [options]
```
- pak_dir: where unpacked files are (e.g. D:\quickbms\pakchunk0_s24-WindowsNoEditor)
- lang1: a language you want to display
- lang2: another language you want to display
- --mod_name: specifies mod name
- --just_swap: swaps subtitles instead of merging them
- --save_as_json: not only makes mod files, but also exports as json

If you run `make_dualsub_mod.exe`, a mod folder (like `.\dualsub_mod_US_JP`) will be generated .

## uexp_to_json.exe
`uexp_to_json.exe` is a tool for exporting subtitle data as .json.<br>
This tool can use for only subtitle data (`End\Content\GameContents\Text\*\*.uexp`).<br>
Also, the output json file will not be compatible with other tools<br>
### Usage

```
make_dualsub_mod.exe uexp --out_dir="json"
```
- uexp: uexp file (e.g. `D:\quickbms\pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text\US\010-MAKO1_TxtRes.uexp`)
- --out_dir: save folder

## json_to_uexp.exe
`json_to_uexp.exe` is a tool for replacing subtitle data with .json.<br>

### Usage

```
make_dualsub_mod.exe uexp json --out_dir="new_uexp"
```
- uexp: uexp file you want to mod (e.g. `D:\quickbms\pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text\US\010-MAKO1_TxtRes.uexp`)
- json: json file (e.g. .\json\010-MAKO1_TxtRes.json)
- --out_dir: save folder

## .uexp Format Specifications
Here is my analysis of .uexp format for subtitle data.<br>
[.uexp Format for Subtitle Data · matyalatte/FF7R_text_mod_tools Wiki](https://github.com/matyalatte/FF7R_text_mod_tools/wiki/.uexp-Format-for-Subtitle-Data)
