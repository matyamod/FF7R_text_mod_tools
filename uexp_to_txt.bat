REM Drop uexp file onto this (uexp_to_txt.bat)

REM New .txt will be generated in FF7R_text_mod_tools\txt

@if "%~1"=="" goto skip

@pushd %~dp0
uexp_to_json.exe %~1 --mode=uexp2txt --out_dir=txt
@popd

pause

:skip