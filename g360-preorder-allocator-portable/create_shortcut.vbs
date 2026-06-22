Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strCurrentPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
strDesktop = objShell.SpecialFolders("Desktop")
strBatPath = strCurrentPath & "\run.bat"
strIconPath = strCurrentPath & "\assets\images\cipsa.ico"

If objFSO.FileExists(strDesktop & "\PreOrder Allocator.lnk") Then
    objFSO.DeleteFile strDesktop & "\PreOrder Allocator.lnk", True
End If

Set objShortcut = objShell.CreateShortcut(strDesktop & "\PreOrder Allocator.lnk")
objShortcut.TargetPath = strBatPath
objShortcut.WorkingDirectory = strCurrentPath
objShortcut.Description = "PreOrder Allocator - G360"
objShortcut.WindowStyle = 7

If objFSO.FileExists(strIconPath) Then
    objShortcut.IconLocation = strIconPath & ", 0"
Else
    objShortcut.IconLocation = "%SystemRoot%\system32\shell32.dll, 15"
End If

objShortcut.Save

objShell.Run "ie4uinit.exe -show", 0, True
