param(
    [string]$SsdRoot = $env:AGERE_SSD_ROOT
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'Continue'

if ([string]::IsNullOrWhiteSpace($SsdRoot)) {
    throw 'Set AGERE_SSD_ROOT to the mounted external SSD path before downloading.'
}

$SsdRoot = [IO.Path]::GetFullPath($SsdRoot)
if (-not (Test-Path -LiteralPath $SsdRoot -PathType Container)) {
    throw "AGERE_SSD_ROOT does not exist or is not mounted: $SsdRoot"
}
$expectedWeights = Join-Path $SsdRoot 'weights\hf'
if (-not (Test-Path -LiteralPath $expectedWeights -PathType Container)) {
    throw "AGERE_SSD_ROOT is not the configured Agere SSD (expected weights/hf): $SsdRoot"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$ssdDatasets = Join-Path $SsdRoot 'datasets'
New-Item -ItemType Directory -Force -Path $ssdDatasets | Out-Null

$datasets = @(
    @{
        Id = 'mortarbench'
        Repo = 'ManavMunjal/MortarBench'
        Revision = 'ab3421d6b1a9f0cedbb9f98d34a4e1eb4473532f'
        License = 'CC-BY-4.0'
        Include = '^data/|^raw/'
        Destination = Join-Path $ssdDatasets 'external\MortarBench\ab3421d6b1a9f0cedbb9f98d34a4e1eb4473532f'
    },
    @{
        Id = 'frames-benchmark'
        Repo = 'google/frames-benchmark'
        Revision = '58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef'
        License = 'Apache-2.0'
        Include = '^test\.tsv$'
        Destination = Join-Path $ssdDatasets 'external\FRAMES\58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef'
    }
)

$manifest = [ordered]@{
    generated_utc = [DateTime]::UtcNow.ToString('o')
    ssd_subdir = 'datasets/'
    policy = 'Dataset files are on the SSD; this manifest stays in the repository.'
    datasets = @()
}

foreach ($dataset in $datasets) {
    Write-Host "`nDataset: $($dataset.Id) [$($dataset.Repo)@$($dataset.Revision)]"
    $api = "https://huggingface.co/api/datasets/$($dataset.Repo)/revision/$($dataset.Revision)"
    $metadata = Invoke-RestMethod -Uri $api -TimeoutSec 60
    if ($metadata.sha -ne $dataset.Revision) {
        throw "Revision mismatch for $($dataset.Repo): expected $($dataset.Revision), got $($metadata.sha)"
    }

    New-Item -ItemType Directory -Force -Path $dataset.Destination | Out-Null
    $files = @($metadata.siblings | Where-Object { $_.rfilename -match $dataset.Include })
    if ($files.Count -eq 0) { throw "No allowlisted files found for $($dataset.Id)" }
    $entries = @()
    foreach ($file in $files) {
        $relative = [string]$file.rfilename
        $safeRelative = $relative.Replace('/', [IO.Path]::DirectorySeparatorChar)
        $destination = [IO.Path]::GetFullPath((Join-Path $dataset.Destination $safeRelative))
        if (-not $destination.StartsWith([IO.Path]::GetFullPath($dataset.Destination), [StringComparison]::OrdinalIgnoreCase)) {
            throw "Unsafe upstream path: $relative"
        }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
        $encodedPath = (($relative -split '/') | ForEach-Object { [Uri]::EscapeDataString($_) }) -join '/'
        $url = "https://huggingface.co/datasets/$($dataset.Repo)/resolve/$($dataset.Revision)/${encodedPath}?download=true"
        if (Test-Path -LiteralPath $destination -PathType Leaf) {
            Write-Host "Already present: $relative"
        } else {
            Write-Host "Downloading: $relative"
            try {
                Invoke-WebRequest -Uri $url -OutFile $destination -TimeoutSec 600
            } catch {
                throw "Download failed for upstream URL $url : $($_.Exception.Message)"
            }
        }
        $hash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
        $relativeDestination = [IO.Path]::GetRelativePath($SsdRoot, $destination).Replace('\', '/')
        $entries += [ordered]@{ path = $relativeDestination; upstream_path = $relative; sha256 = $hash; bytes = (Get-Item -LiteralPath $destination).Length }
    }
    $manifest.datasets += [ordered]@{
        id = $dataset.Id
        repo = $dataset.Repo
        revision = $dataset.Revision
        license = $dataset.License
        files = $entries
    }
}

$manifestPath = Join-Path $repoRoot 'manifests\downloaded_datasets.json'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $manifestPath) | Out-Null
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8
Write-Host "`nDataset downloads and SHA-256 checks complete. Repository manifest: $manifestPath"
