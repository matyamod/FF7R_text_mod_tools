@echo off

REM Drop uexp file onto this (resize_subtitle_box.bat)

REM New .uexp will be generated in ./

@if "%~1"=="" goto skip

@pushd %~dp0
resize_subtitle_box.exe %~1
@popd

pause

:skip