Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) { exit }

Write-Host "Building yt-dlp-Simplified.exe ..."
python -m nuitka ui.py --standalone --windows-console-mode=attach --enable-plugin=tk-inter --include-package-data=ttkthemes --windows-icon-from-ico=icon.ico --include-data-files=icon.ico=icon.ico --include-data-files=bins/*=bins/ --output-filename="yt-dlp-Simplified.exe"
if ($LASTEXITCODE -ne 0) { exit }

Write-Host "Building updater.exe ..."
python -m nuitka --standalone --onefile --windows-console-mode=attach --enable-plugin=tk-inter --output-filename="updater.exe" self_updater.py
if ($LASTEXITCODE -ne 0) { exit }

Write-Host "Copying updater.exe to ui.dist ..."
Copy-Item updater.exe .\ui.dist\

Write-Host "Build completed successfully."