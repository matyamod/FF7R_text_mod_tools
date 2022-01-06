@echo off

REM Drop uexp file onto this (uexp_to_json.bat)

REM New .json will be generated in FF7R_text_mod_tools\json

@if "%~1"=="" goto skip

@pushd %~dp0
FF7R_text_mod_tools.exe --mode=uexp2json --uexp="%~1" --out_dir=json
@popd

pause

:skip