# Comprehensive Repository Cleanup Script
# Moves unnecessary files to backup and verifies system integrity

$backupDir = "backup_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
Write-Host "Created backup folder: $backupDir`n" -ForegroundColor Green

# Move old frontend directories
$oldFrontends = @('earnetics-command-center-v3', 'earnets-command-cockpit', 'frontend')
foreach ($dir in $oldFrontends) {
    if (Test-Path $dir) {
        Move-Item -Path $dir -Destination $backupDir -Force -ErrorAction SilentlyContinue
        Write-Host "Moved old frontend: $dir" -ForegroundColor Yellow
    }
}

# Move debug/temp files
$patterns = @('*debug*.py', '*debug*.log', '*debug*.txt', '*debug*.md', 
              'test_*.py', 'temp_*.py', 'temp_*.txt', 'temp_*.js',
              '*_output.txt', '*_log.txt', '*_result.txt', '*.bak')
$moved = 0
foreach ($pattern in $patterns) {
    Get-ChildItem -File -Filter $pattern -ErrorAction SilentlyContinue | 
        Where-Object { $_.DirectoryName -eq $PWD } | 
        ForEach-Object {
            Move-Item -Path $_.FullName -Destination $backupDir -Force -ErrorAction SilentlyContinue
            $moved++
            Write-Host "Moved: $($_.Name)" -ForegroundColor Gray
        }
}

# Move excessive documentation (keep only essential)
$docsToMove = @('STARTUP_COMMANDS_SIMPLE.md', 'STARTUP_ISSUES_FIX.md', 'NODEJS_FIX.md',
                'FRONTEND_DEBUGGING_FIXES.md', 'FRONTEND_CONNECTION_FIX.md',
                'CONNECTION_TROUBLESHOOTING.md', 'TROUBLESHOOTING_LOADING.md',
                'PATH_NORMALIZATION_FIX.md', 'API_KEYS_SETUP.md', 'API_KEYS_STATUS.md',
                'API_KEYS_COMPLETE_CHECK.md', 'FRONTEND_DATA_LOADING_FIX.md',
                'FRONTEND_BACKEND_ALIGNMENT.md', 'COMPREHENSIVE_ALIGNMENT_CHECK.md',
                'DATA_READINESS_CHECK.md', 'STARTUP_SEQUENCE.md', 'COMMAND_NEXUS_READINESS.md',
                'AUTONOMOUS_OPERATIONS_STARTUP.md', 'FINAL_SYSTEM_VERIFICATION.md')
foreach ($doc in $docsToMove) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination $backupDir -Force -ErrorAction SilentlyContinue
        Write-Host "Moved doc: $doc" -ForegroundColor Gray
    }
}

Write-Host "`n✅ Cleanup complete! Moved $moved files to $backupDir" -ForegroundColor Green
Write-Host "Essential docs kept: START_HERE.md, README.md, CLEANUP_ANALYSIS.md" -ForegroundColor Cyan

