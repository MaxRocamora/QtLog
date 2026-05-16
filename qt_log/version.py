# ----------------------------------------------------------------------------------------
# 1.0.0 05/2022 - Initial Release
# 1.0.1 07/2022 - Fixed Import paths
# 1.1.1 01/2025 - Added PySide6 imports, Ruff Format, Poetry
# 1.1.2 02/2025 - Fixed font monospace property on PySide6
# 1.1.3 08/2025 - Fixed poetry python requirements
# 1.2.0 05/2026 - replaced poetry with uv, type hints
# ----------------------------------------------------------------------------------------

VERSION_MAJOR: int = 1
VERSION_MINOR: int = 2
VERSION_PATCH: int = 0

version: str = f'{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}'

app_name: str = 'QtLog'
