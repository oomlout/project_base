# SolidCraft output cleanup

Run `action_delete_solidcraft_files.bat` from the project root, or double-click it. It locates the project relative to the batch file, regardless of the current directory. Add `-DryRun` to list targets without deleting.

Deletes only the published true/3dpr native, STEP, SolidCraft STL, PNG and metadata filenames directly in part folders. This clears the native existence check so the next SolidCraft run regenerates them. It does not recurse into manual folders, delete SCAD outputs or build history, or alter part definitions. Sealed parts and filesystem links are preserved.

Cleanup uses the generator's writer locks and refuses active builds. Its implementation lives in working.ps1 and requires only the Windows PowerShell included with Windows. The batch wrapper returns its exit code.
