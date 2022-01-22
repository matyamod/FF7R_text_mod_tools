# FF7R Text Mod Tools ver 1.4.2
Text modding tools for FF7R (Final Fantasy VII Remake)<br>


<img src = "image/ff7r_dualsub_sample.jpg" width=600>

There are 4 features in my tool.
- Exports text data
- Imports text data
- Makes dualsub mod
- Resizes subtitle widget

## Download
Download `FF7R_text_mod_tools_*.zip` from here.<br>
[Releases · matyalatte/FF7R_text_mod_tools](https://github.com/matyalatte/FF7R_text_mod_tools/releases)<br>
<br>

## Tutorial
[Text Mod Tutorial · matyalatte/FF7R_text_mod_tools Wiki](https://github.com/matyalatte/FF7R_text_mod_tools/wiki/Text-Mod-Tutorial)<br>
<br>

## GUI Manual
FF7R Text Mod Tools has GUI support now!<br>
<br>
![gui_export](https://user-images.githubusercontent.com/69258547/148523887-4649f924-a467-4f55-bbdf-f36717eb99b0.png)<br>
<br>
Here is the GUI manual.<br>
[GUI Manual · matyalatte/FF7R_text_mod_tools Wiki](https://github.com/matyalatte/FF7R_text_mod_tools/wiki/GUI-Manual)<br>
<br>

## CLI Manual
You can also use the tool with Command-Line.<br>
Here is the CLI manual.<br>
[CLI Manual · matyalatte/FF7R_text_mod_tools Wiki](https://github.com/matyalatte/FF7R_text_mod_tools/wiki/CLI-Manual)<br>
<br>

## Tips on Text Modding
I posted some tips (format specification, text decoration, etc.) here.<br>
[Home · matyalatte/FF7R_text_mod_tools Wiki](https://github.com/matyalatte/FF7R_text_mod_tools/wiki)<br>
<br>

## Q&A

### Is the .exe file malware? My antivirus reports it as virus.
No, it is a false positive caused by pyinstaller.<br>
<br>
[AVG (and other antiviruses) reports exe file as containing virus · Issue #603 · pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller/issues/603)<br>
<br>
I recompiled the bootloader of pyinstaller to reduce false positives, but it will not completely solve the issue.<br>
If you are worried about the security, please run [the Python scripts](https://github.com/matyalatte/FF7R_text_mod_tools/tree/main/src) instead of the .exe file.<br>
<br>

### Is there any way to import font data? The game does not support some characters in my language.
Use my font modding tools.<br>
[matyalatte/FF7R-font-mod-tools: Font modding tools for FF7R (Final Fantasy VII Remake)](https://github.com/matyalatte/FF7R-font-mod-tools)<br>
