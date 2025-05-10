#!/bin/bash

# Script to fix import errors in Python files
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Python Import Error Fixer"
echo "This script will fix import errors in Python files."
echo ""

# Find files with import errors
section "Finding Files with Import Errors"
echo "Finding Python files with import errors..."

files_with_errors=$(grep -r "ImportError\|ModuleNotFoundError" --include="*.py" . | cut -d: -f1 | sort | uniq)
error_count=$(echo "$files_with_errors" | wc -l)

echo "Found $error_count files with import errors."
echo ""

# Process each file with import errors
section "Processing Files with Import Errors"
echo "Processing files with import errors..."

for file in $files_with_errors; do
    echo "Processing $file..."
    
    # Skip files in legacy directory
    if [[ $file == ./legacy/* ]]; then
        echo "  Skipping legacy file"
        continue
    fi
    
    # Check for common import error patterns and fix them
    
    # Pattern 1: Try-except ImportError for OpenHands
    if grep -q "except ImportError:" "$file" && grep -q "openhands" "$file"; then
        echo "  Fixing OpenHands import error in $file"
        sed -i 's/from openhands/from src.openhands/g' "$file"
    fi
    
    # Pattern 2: Try-except ImportError for monitoring
    if grep -q "except ImportError:" "$file" && grep -q "monitoring" "$file"; then
        echo "  Fixing monitoring import error in $file"
        sed -i 's/from monitoring/from src.monitoring/g' "$file"
    fi
    
    # Pattern 3: Try-except ImportError for MCP components
    if grep -q "except ImportError:" "$file" && grep -q "mcp" "$file"; then
        echo "  Fixing MCP import error in $file"
        sed -i 's/from mcp\./from src.mcp./g' "$file"
        sed -i 's/from mcp_servers\./from src.mcp_servers./g' "$file"
        sed -i 's/from mcp_hub\./from src.mcp_hub./g' "$file"
    fi
    
    # Pattern 4: Try-except ImportError for LLM components
    if grep -q "except ImportError:" "$file" && grep -q "llm" "$file"; then
        echo "  Fixing LLM import error in $file"
        sed -i 's/from llm_/from src.llm_/g' "$file"
    fi
    
    # Pattern 5: General relative imports
    if grep -q "ImportError:" "$file" || grep -q "ModuleNotFoundError:" "$file"; then
        echo "  Fixing relative imports in $file"
        sed -i 's/from \.\./from src./g' "$file"
        sed -i 's/from \./from src./g' "$file"
    fi
done

echo ""
section "Import Error Fixing Complete"
echo "The import error fixing process is now complete."
echo "Please review the changes and test the code to ensure everything works correctly."
echo ""
echo "Thank you for using the Python Import Error Fixer script."