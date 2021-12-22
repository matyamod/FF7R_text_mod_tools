# FF7R Text Mod Tools
Subtitle modding tools for FF7R (Final Fantasy VII Remake)<br>

<img src = "image/ff7r_dualsub_sample.jpg" width=600>

There are 5 functions in my tools.

- Make dualsub mod: Merges subtitle data between 2 languages.
- Make swapsub mod: Swaps subtitle data between 2 languages.
- .uexp to .json: Exports subtitle data as .json.
- .json to .uexp: Swaps subtitle data with .json.
- .uexp to .txt: Exports subtitle data as .txt.


## Make Dualsub Mod
`make_dualsub_mod.exe` is a tool for merging subtitle data.<br>
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
- --mod_name= : specifies mod name
- --just_swap: swaps subtitles instead of merging them
- --save_as_json: not only makes mod files, but also exports as json
- --save_as_txt: not only makes mod files, but also exports as txt

If you run `make_dualsub_mod.exe`, a mod folder (like `.\dualsub_mod_US_JP`) will be generated .
## Make Swapsub Mod
If you run `make_dualsub_mod.exe` with `--just_swap` otption, subtitle data will be swapped between 2 languages.


## .uexp to .json
`uexp_to_json.exe` is a tool for exporting subtitle data as .json.<br>
This tool can use for only subtitle data (`End\Content\GameContents\Text\*\[0-9]{3}-*.uexp`).<br>
Also, the output json file will not be compatible with other tools<br>
### Usage

```
uexp_to_json.exe uexp --mode="uexp2json" [options]
```
- uexp: uexp file (e.g. `D:\quickbms\pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text\US\010-MAKO1_TxtRes.uexp`)
- --mode="uexp2json"
- --out_dir= : save folder

## .json to .uexp
If you run `uexp_to_json.exe` with `--mode="json2uexp"` option, subtitle data will be replaced with .json.<br>

### Usage

```
uexp_to_json.exe uexp --mode="json2uexp" --json=json [options]
```
- uexp: uexp file (e.g. `D:\quickbms\pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text\US\010-MAKO1_TxtRes.uexp`)
- --mode="json2uexp"
- --json=: json file (e.g. `.\json\010-MAKO1_TxtRes.json`)
- --out_dir= : save folder

## .uexp to .txt
If you run `uexp_to_json.exe` with `--mode="uexp2txt"` option, subtitle data will be exported as .txt.<br>

### Usage

```
uexp_to_json.exe uexp --mode="uexp2txt" [options]
```
- uexp: uexp file (e.g. `D:\quickbms\pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text\US\010-MAKO1_TxtRes.uexp`)
- --mode="uexp2txt"
- --out_dir= : save folder



## .uexp Format Specifications
Here is my analysis of .uexp format for subtitle data.<br>
[.uexp Format for Subtitle Data · matyalatte/FF7R_text_mod_tools Wiki](https://github.com/matyalatte/FF7R_text_mod_tools/wiki/.uexp-Format-for-Subtitle-Data)
