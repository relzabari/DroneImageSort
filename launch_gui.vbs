Option Explicit

Dim shell, fileSystem, projectDirectory, guiPath, pythonwPath, command
Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

projectDirectory = fileSystem.GetParentFolderName(WScript.ScriptFullName)
guiPath = fileSystem.BuildPath(projectDirectory, "gui.py")

If Not fileSystem.FileExists(guiPath) Then
    MsgBox "Could not find gui.py in:" & vbCrLf & projectDirectory, _
        vbCritical, "Drone Image Sort"
    WScript.Quit 1
End If

pythonwPath = FindPythonw(shell, fileSystem)
If Len(pythonwPath) = 0 Then
    MsgBox "Python could not be found." & vbCrLf & vbCrLf & _
        "Install Python and enable the Add Python to PATH option, then try again.", _
        vbCritical, "Drone Image Sort"
    WScript.Quit 1
End If

shell.CurrentDirectory = projectDirectory
command = Quote(pythonwPath) & " " & Quote(guiPath)
shell.Run command, 0, False


Function FindPythonw(shellObject, fso)
    Dim path, baseFolders, baseFolder, folder, subfolder

    path = FindOnPath(shellObject, fso)
    If Len(path) > 0 Then
        FindPythonw = path
        Exit Function
    End If

    path = ReadAppPath(shellObject, fso, "HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\pythonw.exe\")
    If Len(path) = 0 Then
        path = ReadAppPath(shellObject, fso, "HKLM\Software\Microsoft\Windows\CurrentVersion\App Paths\pythonw.exe\")
    End If
    If Len(path) > 0 Then
        FindPythonw = path
        Exit Function
    End If

    baseFolders = Array( _
        shellObject.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python"), _
        shellObject.ExpandEnvironmentStrings("%ProgramFiles%"), _
        shellObject.ExpandEnvironmentStrings("%ProgramFiles(x86)%") _
    )

    For Each baseFolder In baseFolders
        If fso.FolderExists(baseFolder) Then
            Set folder = fso.GetFolder(baseFolder)

            path = fso.BuildPath(folder.Path, "pythonw.exe")
            If fso.FileExists(path) Then
                FindPythonw = path
                Exit Function
            End If

            For Each subfolder In folder.SubFolders
                If LCase(Left(subfolder.Name, 6)) = "python" Then
                    path = fso.BuildPath(subfolder.Path, "pythonw.exe")
                    If fso.FileExists(path) Then
                        FindPythonw = path
                        Exit Function
                    End If
                End If
            Next
        End If
    Next

    FindPythonw = ""
End Function


Function FindOnPath(shellObject, fso)
    Dim process, line
    On Error Resume Next
    Set process = shellObject.Exec("cmd.exe /d /c where pythonw.exe 2>nul")
    If Err.Number <> 0 Then
        Err.Clear
        FindOnPath = ""
        On Error GoTo 0
        Exit Function
    End If

    line = Trim(process.StdOut.ReadLine)
    On Error GoTo 0
    If Len(line) > 0 And fso.FileExists(line) Then
        FindOnPath = line
    Else
        FindOnPath = ""
    End If
End Function


Function ReadAppPath(shellObject, fso, registryPath)
    Dim value
    On Error Resume Next
    value = shellObject.RegRead(registryPath)
    If Err.Number <> 0 Then
        Err.Clear
        value = ""
    End If
    On Error GoTo 0

    value = Replace(value, Chr(34), "")
    If Len(value) > 0 And fso.FileExists(value) Then
        ReadAppPath = value
    Else
        ReadAppPath = ""
    End If
End Function


Function Quote(value)
    Quote = Chr(34) & value & Chr(34)
End Function
