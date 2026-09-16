Option Explicit
Dim shell, fso, appDir, command, argument
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ _
    & appDir & "\launch_home.ps1"""
For Each argument In WScript.Arguments
    command = command & " """ & argument & """"
Next
shell.Run command, 0, False
