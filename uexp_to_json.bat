@if "%~1"=="" goto skip

@pushd %~dp0
uexp_to_json.exe %~1 --out_dir=json
@popd

pause

:skip