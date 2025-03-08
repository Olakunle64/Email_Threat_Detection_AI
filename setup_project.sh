#!/bin/bash

# Create project directories
mkdir -p data notebooks src app results

# Create Python scripts in src directory
touch src/preprocessing.py
touch src/model.py
touch src/inference.py
touch src/utils.py

# Create essential project files
touch requirements.txt
touch README.md


# Add a .gitignore file (optional)
cat <<EOL > .gitignore
__pycache__/
*.pyc
*.pyo
.DS_Store
data/
results/
EOL

echo "Project structure created successfully! 🎯"
