@echo off

REM Drop uexp file onto this (resize_subtitle_box.bat)

REM New .uexp will be generated in ./

@if "%~1"=="" goto skip

@pushd %~dp0
FF7R_text_mod_tools.exe --mode=resize --uexp="%~1" --width=1170 --height=260
@popd

pause

:skip