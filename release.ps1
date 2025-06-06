# Company Logo Scraper Release Script
# This PowerShell script helps automate parts of the release process

param(
    [Parameter(Mandatory = $false)]
    [string]$Version,
    
    [Parameter(Mandatory = $false)]
    [switch]$RunTests,
    
    [Parameter(Mandatory = $false)]
    [switch]$CleanUp,
    
    [Parameter(Mandatory = $false)]
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Write-Host "Company Logo Scraper Release Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\release.ps1 -Version 1.2.0                # Update version to 1.2.0"
    Write-Host "  .\release.ps1 -RunTests                     # Run all tests"
    Write-Host "  .\release.ps1 -CleanUp                      # Clean up temp files"
    Write-Host "  .\release.ps1 -Version 1.2.0 -RunTests     # Update version and run tests"
    Write-Host "  .\release.ps1 -Help                         # Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\release.ps1 -Version 1.2.0 -RunTests -CleanUp"
    Write-Host ""
    exit 0
}

Write-Host "🚀 Company Logo Scraper Release Helper" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Function to update version in __version__.py
function Update-Version {
    param([string]$NewVersion)
    
    Write-Host "📝 Updating version to $NewVersion..." -ForegroundColor Yellow
    
    $versionFile = "src\__version__.py"
    if (Test-Path $versionFile) {
        $content = Get-Content $versionFile
        $content = $content -replace '__version__ = "[^"]*"', "__version__ = `"$NewVersion`""
        $content = $content -replace '__build_date__ = "[^"]*"', "__build_date__ = `"$(Get-Date -Format 'yyyy-MM-dd')`""
        Set-Content -Path $versionFile -Value $content
        Write-Host "✅ Version updated in $versionFile" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Version file not found: $versionFile" -ForegroundColor Red
        exit 1
    }
}

# Function to run tests
function Run-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    
    # Run pytest
    Write-Host "Running pytest..." -ForegroundColor Cyan
    python -m pytest src/tests/ -v
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ pytest failed" -ForegroundColor Red
        return $false
    }
    
    # Run configuration tests
    Write-Host "Running configuration flow tests..." -ForegroundColor Cyan
    python test_config_flow.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Configuration flow tests failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Running CLI configuration tests..." -ForegroundColor Cyan
    python test_cli_config.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ CLI configuration tests failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Running end-to-end configuration tests..." -ForegroundColor Cyan
    python test_end_to_end_config.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ End-to-end configuration tests failed" -ForegroundColor Red
        return $false
    }
    
    # Test CLI help
    Write-Host "Testing CLI help..." -ForegroundColor Cyan
    python main.py --help | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ CLI help test failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    return $true
}

# Function to clean up temporary files
function Clean-Up {
    Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
    
    # Remove __pycache__ directories
    Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        $path = $_
        Write-Host "Removing $path" -ForegroundColor Cyan
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Remove .pyc files
    Get-ChildItem -Path . -Recurse -File -Name "*.pyc" | ForEach-Object {
        Write-Host "Removing $_" -ForegroundColor Cyan
        Remove-Item -Path $_ -Force -ErrorAction SilentlyContinue
    }
    
    # Clean temp directory
    if (Test-Path "temp") {
        Write-Host "Cleaning temp directory..." -ForegroundColor Cyan
        Get-ChildItem -Path "temp" -Exclude ".gitkeep" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Clean src/temp directory
    if (Test-Path "src/temp") {
        Write-Host "Cleaning src/temp directory..." -ForegroundColor Cyan
        Get-ChildItem -Path "src/temp" -Exclude ".gitkeep" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ Cleanup completed!" -ForegroundColor Green
}

# Function to check git status
function Check-GitStatus {
    Write-Host "🔍 Checking git status..." -ForegroundColor Yellow
    
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "⚠️  Warning: There are uncommitted changes:" -ForegroundColor Yellow
        Write-Host $gitStatus
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y") {
            Write-Host "❌ Release cancelled" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "✅ Git working directory is clean" -ForegroundColor Green
    }
}

# Main execution
try {
    # Update version if specified
    if ($Version) {
        Update-Version -NewVersion $Version
    }
    
    # Run tests if specified
    if ($RunTests) {
        $testsPassed = Run-Tests
        if (-not $testsPassed) {
            Write-Host "❌ Tests failed, stopping release process" -ForegroundColor Red
            exit 1
        }
    }
    
    # Clean up if specified
    if ($CleanUp) {
        Clean-Up
    }
    
    # Check git status
    Check-GitStatus
    
    # Show next steps
    Write-Host ""
    Write-Host "🎉 Release preparation completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Review RELEASE_CHECKLIST.md" -ForegroundColor White
    Write-Host "2. Commit your changes: git add -A && git commit -m 'Prepare release v$Version'" -ForegroundColor White
    Write-Host "3. Create release branch: git checkout -b release/v$Version" -ForegroundColor White
    Write-Host "4. Push to GitHub: git push origin release/v$Version" -ForegroundColor White
    Write-Host "5. Create GitHub release with tag v$Version" -ForegroundColor White
    Write-Host ""
    
}
catch {
    Write-Host "❌ Error during release preparation: $_" -ForegroundColor Red
    exit 1
}
