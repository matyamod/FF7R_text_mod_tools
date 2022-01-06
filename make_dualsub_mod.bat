@echo off

rem PAK_DIR: where unpacked files are

set PAK_DIR=D:\quickbms\pakchunk0_s24-WindowsNoEditor
rem (pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text...)

set LANG1=US
set LANG2=JP
rem Language list: BR, CN, DE, ES, FR, IT, JP, KR, MX, TW, US

FF7R_text_mod_tools.exe --mode=dualsub --pak_dir="%PAK_DIR%" --lang1=%LANG1% --lang2=%LANG2%

pause