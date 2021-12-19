rem PAK_DIR: where unpacked files are

set PAK_DIR=D:\quickbms\pakchunk0_s24-WindowsNoEditor
rem (pakchunk0_s24-WindowsNoEditor\End\Content\GameContents\Text...)

set LANG1=US
set LANG2=JP
rem Language list: BR, CN, DE, ES, FR, IT, JP, KR, MX, TW, US

make_dualsub_mod.exe %PAK_DIR% %LANG1% %LANG2% --just_swap

pause