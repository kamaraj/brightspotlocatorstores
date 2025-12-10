# Childcare Location Intelligence - Automated Setup Script
# For Windows PowerShell

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Childcare Location Intelligence System                       ║" -ForegroundColor Cyan
Write-Host "║  Automated Setup Script                                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/6] Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
    
    # Extract version number
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "  ✗ Error: Python 3.10+ required" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  ✗ Error: Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ℹ Virtual environment already exists" -ForegroundColor Blue
} else {
    python -m venv venv
    if ($?) {
        Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "`n[3/6] Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "  Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

# Install agent framework with --pre flag (CRITICAL)
Write-Host "`n[4/6] Installing Microsoft Agent Framework (preview)..." -ForegroundColor Yellow
Write-Host "  ℹ This may take a few minutes..." -ForegroundColor Blue
pip install agent-framework-azure-ai --pre --quiet
if ($?) {
    Write-Host "  ✓ Agent Framework installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Error: Failed to install Agent Framework" -ForegroundColor Red
    exit 1
}

# Install remaining dependencies
Write-Host "`n[5/6] Installing remaining dependencies..." -ForegroundColor Yellow
Write-Host "  ℹ This may take 3-5 minutes..." -ForegroundColor Blue
pip install -r requirements.txt --quiet
if ($?) {
    Write-Host "  ✓ All dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Warning: Some dependencies may have failed" -ForegroundColor Yellow
}

# Setup environment file
Write-Host "`n[6/6] Setting up environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ℹ .env file already exists - skipping" -ForegroundColor Blue
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Created .env file from template" -ForegroundColor Green
    Write-Host "  ⚠ IMPORTANT: Edit .env and add your API keys!" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "`nCreating directories..." -ForegroundColor Yellow
$dirs = @("logs", "data", "data/chromadb", "frontend/templates", "frontend/static")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created $dir" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Setup Complete!                                               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env file and add your API keys:" -ForegroundColor White
Write-Host "     - GITHUB_TOKEN (https://github.com/settings/tokens)" -ForegroundColor Gray
Write-Host "     - GOOGLE_MAPS_API_KEY (Google Cloud Console)" -ForegroundColor Gray
Write-Host "     - CENSUS_API_KEY (https://api.census.gov/data/key_signup.html)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Run the application:" -ForegroundColor White
Write-Host "     python run.py" -ForegroundColor Green
Write-Host ""
Write-Host "  3. Access the API:" -ForegroundColor White
Write-Host "     http://localhost:8000/api/docs" -ForegroundColor Green
Write-Host ""
Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Blue
Write-Host ""

# Check if API keys are configured
Write-Host "Checking configuration..." -ForegroundColor Yellow
$envContent = Get-Content ".env" -Raw
$keysNeeded = @()

if ($envContent -notmatch 'GITHUB_TOKEN="?ghp_\w+') {
    $keysNeeded += "GITHUB_TOKEN"
}
if ($envContent -notmatch 'GOOGLE_MAPS_API_KEY="?\w+') {
    $keysNeeded += "GOOGLE_MAPS_API_KEY"
}
if ($envContent -notmatch 'CENSUS_API_KEY="?\w+') {
    $keysNeeded += "CENSUS_API_KEY"
}

if ($keysNeeded.Count -gt 0) {
    Write-Host "`n⚠ WARNING: Missing required API keys in .env:" -ForegroundColor Red
    foreach ($key in $keysNeeded) {
        Write-Host "  - $key" -ForegroundColor Red
    }
    Write-Host "`nThe application will not work without these keys." -ForegroundColor Yellow
    Write-Host "Please edit .env and add them before running." -ForegroundColor Yellow
} else {
    Write-Host "`n✓ All required API keys appear to be configured!" -ForegroundColor Green
    Write-Host "Ready to run: python run.py" -ForegroundColor Green
}

Write-Host ""
