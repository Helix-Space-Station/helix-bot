#!/usr/bin/env python3
"""
Static code analysis checks
"""

import ast
import os
import sys

def check_syntax(filepath):
    """Check Python file syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, "✓ Valid syntax"
    except SyntaxError as e:
        return False, f"✗ Syntax error: {e}"

def check_imports(filepath):
    """Check for problematic imports"""
    problematic_imports = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith('.'):
                    problematic_imports.append(f"Relative import: {alias.name}")
        
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith('.'):
                problematic_imports.append(f"Relative import from: {node.module}")
    
    return problematic_imports

def run_static_analysis():
    """Run all static analysis checks"""
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and hidden directories
        if any(skip in root for skip in ['venv', '.git', '__pycache__', '.pytest_cache']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    all_passed = True
    
    print("Running static analysis...")
    for filepath in python_files:
        print(f"\nChecking {filepath}:")
        
        # Check syntax
        success, message = check_syntax(filepath)
        print(f"  Syntax: {message}")
        if not success:
            all_passed = False
        
        # Check imports
        issues = check_imports(filepath)
        if issues:
            print(f"  Imports: ✗ Found {len(issues)} issues")
            for issue in issues:
                print(f"    - {issue}")
            all_passed = False
        else:
            print("  Imports: ✓ No issues found")
    
    return all_passed

if __name__ == "__main__":
    success = run_static_analysis()
    sys.exit(0 if success else 1)
