@echo off

REM Drop uexp file onto this (uexp_to_txt.bat)

REM New .txt will be generated in FF7R_text_mod_tools\txt

@if "%~1"=="" goto skip

@pushd %~dp0
FF7R_text_mod_tools.exe --mode=uexp2txt --uexp="%~1" --out_dir=txt
@popd

pause

:skip