# Python Virtual Environment Setup Guide

This guide explains how to create, activate, and use a Python virtual environment (venv) and install project requirements.

## What is a Virtual Environment?

A virtual environment is an isolated Python environment that allows you to install packages specific to a project without affecting your system-wide Python installation.

## Prerequisites

- Python 3.3 or higher (venv comes built-in)
- pip (usually comes with Python)

## Creating a Virtual Environment

### On Windows
```bash
# Navigate to your project directory
cd path/to/your/project

# Create a virtual environment named 'venv'
python -m venv venv
```

### On macOS/Linux
```bash
# Navigate to your project directory
cd path/to/your/project

# Create a virtual environment named 'venv'
python3 -m venv venv
```

## Activating the Virtual Environment

### On Windows
```bash
# Command Prompt
venv\Scripts\activate.bat

# PowerShell
venv\Scripts\Activate.ps1

# Git Bash
source venv/Scripts/activate
```

### On macOS/Linux
```bash
source venv/bin/activate
```

## Verifying Activation

When activated, you should see `(venv)` at the beginning of your command prompt:
```
(venv) user@computer:~/project$
```

You can also verify by checking the Python location:
```bash
which python  # macOS/Linux
where python  # Windows
```

## Installing Requirements

### If you have a requirements.txt file
```bash
pip install -r requirements.txt
```

### Installing individual packages
```bash
pip install package_name
```

### Installing multiple packages
```bash
pip install package1 package2 package3
```

## Creating a requirements.txt File

To save your current environment's packages:
```bash
pip freeze > requirements.txt
```

## Deactivating the Virtual Environment

When you're done working:
```bash
deactivate
```

## Common Issues and Solutions

### PowerShell Execution Policy Error (Windows)

If you get an error about execution policies, run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Permission Denied (macOS/Linux)

If you encounter permission issues, ensure the activate script is executable:
```bash
chmod +x venv/bin/activate
```

## Best Practices

- Always activate your virtual environment before working on your project
- Keep your `requirements.txt` file updated
- Add `venv/` to your `.gitignore` file (don't commit virtual environments)
- Use descriptive names for virtual environments if managing multiple projects
- Recreate virtual environments periodically to keep dependencies clean

## Example Workflow
```bash
# 1. Create project directory
mkdir my_project
cd my_project

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 4. Install requirements
pip install -r requirements.txt

# 5. Work on your project
python main.py

# 6. Deactivate when done
deactivate
```

## Additional Tips

- To upgrade pip inside the virtual environment:
```bash
  pip install --upgrade pip
```

- To list installed packages:
```bash
  pip list
```

- To uninstall a package:
```bash
  pip uninstall package_name
```