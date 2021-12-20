REM Place a josn file into FF7R_text_mod_tools\json
REM and drop a uexp file onto this (json_to_uexp.bat)

REM New .uexp and .uasset will be generated in FF7R_text_mod_tools\new_uexp

@if "%~1"=="" goto skip

@pushd %~dp0
json_to_uexp.exe %~1 json\%~n1.json --out_dir=new_uexp
@popd

pause

:skip