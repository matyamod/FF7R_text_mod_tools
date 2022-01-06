@echo off

REM Place a josn file into FF7R_text_mod_tools\json
REM and drop a uexp file onto this (json_to_uexp.bat)

REM New .uexp and .uasset will be generated in FF7R_text_mod_tools\new_uexp

@if "%~1"=="" goto skip

@pushd %~dp0
FF7R_text_mod_tools.exe --mode=json2uexp --uexp="%~1" --json=json\%~n1.json --out_dir=new_uexp
@popd

pause

:skip