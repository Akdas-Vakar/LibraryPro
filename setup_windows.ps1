# ============================================================
#  LibraryPro — Windows Setup Script (PowerShell)
#  Run this from the LibraryPro\ root folder:
#    .\setup_windows.ps1
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LibraryPro — Windows Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── STEP 1: Check Python ─────────────────────────────────
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if ($python) {
    $ver = & python --version 2>&1
    Write-Host "      ✅ Found: $ver" -ForegroundColor Green
} else {
    Write-Host "      ❌ Python not found. Download: https://python.org" -ForegroundColor Red
    exit 1
}

# ── STEP 2: Create virtual environment ───────────────────
Write-Host ""
Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Yellow

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "      ✅ venv created" -ForegroundColor Green
} else {
    Write-Host "      ℹ️  venv already exists, skipping" -ForegroundColor Gray
}

# Activate venv
& ".\venv\Scripts\Activate.ps1"
Write-Host "      ✅ venv activated" -ForegroundColor Green

# ── STEP 3: Install packages ──────────────────────────────
Write-Host ""
Write-Host "[3/4] Installing Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "      ✅ Packages installed" -ForegroundColor Green
} else {
    Write-Host "      ❌ pip install failed" -ForegroundColor Red
    exit 1
}

# ── STEP 4: .env file ─────────────────────────────────────
Write-Host ""
Write-Host "[4/4] Checking .env file..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "      ✅ .env created from .env.example" -ForegroundColor Green
    Write-Host "      ⚠️  EDIT .env and add your MySQL password / Gemini Key!" -ForegroundColor Yellow
} else {
    Write-Host "      ✅ .env already exists" -ForegroundColor Green
}

# ── DONE ──────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "    1. Edit .env  →  set your MySQL password and GEMINI_API_KEY" -ForegroundColor Gray
Write-Host "    2. Run MySQL schema:" -ForegroundColor Gray
Write-Host "       mysql -u root -p < database\schema.sql" -ForegroundColor Cyan
Write-Host "    3. Seed the 100 catalog books (generates embeddings!):" -ForegroundColor Gray
Write-Host "       python seed_books.py" -ForegroundColor Cyan
Write-Host "    4. Start the app:" -ForegroundColor Gray
Write-Host "       python backend\app.py" -ForegroundColor Cyan
Write-Host "    5. Open browser: http://localhost:5000" -ForegroundColor Cyan
Write-Host "       Login: admin / admin@123" -ForegroundColor Cyan
Write-Host ""
