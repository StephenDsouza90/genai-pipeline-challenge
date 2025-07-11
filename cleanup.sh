# Remove all .pyc files
find . -name "*.pyc" -delete

# Remove all __pycache__ directories
find . -name "__pycache__" -type d -exec rm -rf {} +

# Remove all .ruff_cache directories
find . -name ".ruff_cache" -type d -exec rm -rf {} +

# Remove all .DS_Store files
find . -name ".DS_Store" -delete

# Remove all .pytest_cache directories
find . -name ".pytest_cache" -type d -exec rm -rf {} +

# Remove venv directory
rm -rf venv