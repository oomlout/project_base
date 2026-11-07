param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$guards = @()
try {
    $projectPath = (Resolve-Path -LiteralPath $ProjectRoot).ProviderPath.TrimEnd('\')
    $partsPath = Join-Path $projectPath 'parts'
    if (-not (Test-Path -LiteralPath $partsPath -PathType Container)) {
        Write-Host 'No parts folder; nothing to delete.'
        exit 0
    }
    if ((Get-Item -LiteralPath $partsPath).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'Refusing to clean a linked parts folder.'
    }

    # Use the same byte locks as the generator. Keep guard files in place.
    foreach ($relative in @('build\solidcraft', 'build\solidcraft\runs')) {
        $lockRoot = Join-Path $projectPath $relative
        foreach ($segment in @('build', 'build\solidcraft', $relative)) {
            $segmentPath = Join-Path $projectPath $segment
            if ((Test-Path -LiteralPath $segmentPath) -and ((Get-Item -LiteralPath $segmentPath).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                throw 'Refusing to use a linked build directory.'
            }
        }
        [void][IO.Directory]::CreateDirectory($lockRoot)
        $guardPath = Join-Path $lockRoot '.writer.guard'
        if ((Test-Path -LiteralPath $guardPath) -and ((Get-Item -LiteralPath $guardPath).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Refusing to use a linked writer guard.'
        }
        $stream = [IO.File]::Open($guardPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::ReadWrite)
        try {
            $stream.Lock(0, 1)
        } catch {
            $stream.Dispose()
            throw 'SolidCraft is currently building. Let it finish or stop it before cleanup.'
        }
        $guards += $stream
        $marker = Join-Path $lockRoot '.writer.lock'
        if (Test-Path -LiteralPath $marker -PathType Leaf) {
            $writerId = 0
            if (-not [int]::TryParse([IO.File]::ReadAllText($marker).Trim(), [ref]$writerId) -or $writerId -le 0) {
                throw 'Cannot establish ownership of the existing writer lock.'
            }
            if (Get-Process -Id $writerId -ErrorAction SilentlyContinue) {
                throw "SolidCraft writer $writerId is still running. Cleanup cancelled."
            }
        }
    }

    # Only the generator's published names, directly inside each part folder.
    $names = foreach ($mode in @('true', '3dpr')) {
        "$mode.solidcraft"
        "$mode.step"
        "${mode}_solidcraft.stl"
        "${mode}_solidcraft.png"
        "${mode}_solidcraft_step.png"
        "${mode}_solidcraft_measurements.json"
        "${mode}_solidcraft_definition.json"
        "${mode}_solidcraft_structure.json"
        "${mode}_solidcraft_manifest.json"
        "${mode}_solidcraft_exports_manifest.json"
    }
    $deleted = 0
    foreach ($folder in Get-ChildItem -LiteralPath $partsPath -Directory) {
        if ($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
        if (Test-Path -LiteralPath (Join-Path $folder.FullName 'SEALED.json')) {
            Write-Host "Preserved sealed part: $($folder.Name)"
            continue
        }
        foreach ($name in $names) {
            $target = [IO.Path]::GetFullPath((Join-Path $folder.FullName $name))
            if (-not $target.StartsWith($partsPath + '\', [StringComparison]::OrdinalIgnoreCase)) {
                throw "Target is outside this project's parts folder: $target"
            }
            if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { continue }
            if ((Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            if ($DryRun) {
                Write-Host "Would delete: $target"
            } else {
                Remove-Item -LiteralPath $target -ErrorAction Stop
                Write-Host "Deleted: $target"
            }
            $deleted++
        }
    }
    if ($DryRun) {
        Write-Host "Dry run: $deleted generated files selected. Nothing deleted."
    } else {
        Write-Host "Deleted $deleted generated SolidCraft files. The next build will regenerate missing native files."
    }
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
} finally {
    foreach ($stream in $guards) {
        try { $stream.Unlock(0, 1) } finally { $stream.Dispose() }
    }
}
