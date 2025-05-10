#!/bin/bash

# Script to run a security scan on the repository
# Created as part of the Dev-Server-Workflow repository cleanup project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Security Scanner"
echo "This script will run a security scan on the Dev-Server-Workflow repository."
echo ""

# Check if required tools are installed
section "Checking Required Tools"

# Check for bandit (Python security scanner)
if ! command -v bandit &> /dev/null; then
    echo "Bandit is not installed. Installing..."
    pip install bandit
    echo "Bandit installed."
else
    echo "Bandit is already installed."
fi

# Check for npm-audit (JavaScript security scanner)
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Installing..."
    apt-get update && apt-get install -y npm
    echo "npm installed."
else
    echo "npm is already installed."
fi

# Check for safety (Python dependency scanner)
if ! command -v safety &> /dev/null; then
    echo "Safety is not installed. Installing..."
    pip install safety
    echo "Safety installed."
else
    echo "Safety is already installed."
fi

echo ""

# Run security scan on Python code
section "Scanning Python Code with Bandit"
echo "Running Bandit on Python code..."
bandit -r ./src -f json -o bandit_results.json
bandit -r ./src -f txt -o bandit_results.txt
echo "Bandit scan complete. Results saved to bandit_results.json and bandit_results.txt"
echo ""

# Run security scan on Python dependencies
section "Scanning Python Dependencies with Safety"
echo "Running Safety on Python dependencies..."
safety check -r requirements.txt --json > safety_results.json
safety check -r requirements.txt > safety_results.txt
echo "Safety scan complete. Results saved to safety_results.json and safety_results.txt"
echo ""

# Run security scan on JavaScript code
section "Scanning JavaScript Dependencies with npm audit"
echo "Running npm audit on JavaScript dependencies..."
cd frontend && npm audit --json > ../npm_audit_results.json
cd frontend && npm audit > ../npm_audit_results.txt
echo "npm audit complete. Results saved to npm_audit_results.json and npm_audit_results.txt"
echo ""

# Generate security report
section "Generating Security Report"
echo "Generating security report..."

# Create the report file
echo "# Security Scan Report" > security_report.md
echo "" >> security_report.md
echo "This report provides a summary of security issues found in the Dev-Server-Workflow repository." >> security_report.md
echo "" >> security_report.md
echo "Scan date: $(date)" >> security_report.md
echo "" >> security_report.md

# Add Bandit results
echo "## Python Code Security Issues" >> security_report.md
echo "" >> security_report.md
echo "The following security issues were found in the Python code:" >> security_report.md
echo "" >> security_report.md
echo '```' >> security_report.md
cat bandit_results.txt >> security_report.md
echo '```' >> security_report.md
echo "" >> security_report.md

# Add Safety results
echo "## Python Dependency Security Issues" >> security_report.md
echo "" >> security_report.md
echo "The following security issues were found in the Python dependencies:" >> security_report.md
echo "" >> security_report.md
echo '```' >> security_report.md
cat safety_results.txt >> security_report.md
echo '```' >> security_report.md
echo "" >> security_report.md

# Add npm audit results
echo "## JavaScript Dependency Security Issues" >> security_report.md
echo "" >> security_report.md
echo "The following security issues were found in the JavaScript dependencies:" >> security_report.md
echo "" >> security_report.md
echo '```' >> security_report.md
cat npm_audit_results.txt >> security_report.md
echo '```' >> security_report.md
echo "" >> security_report.md

# Add recommendations
echo "## Recommendations" >> security_report.md
echo "" >> security_report.md
echo "Based on the security scan results, the following recommendations are made:" >> security_report.md
echo "" >> security_report.md
echo "1. Address all high and critical severity issues immediately" >> security_report.md
echo "2. Review and address medium severity issues in the next release" >> security_report.md
echo "3. Document low severity issues for future consideration" >> security_report.md
echo "4. Implement regular security scanning as part of the CI/CD pipeline" >> security_report.md
echo "5. Update dependencies regularly to address security vulnerabilities" >> security_report.md
echo "" >> security_report.md

echo "Security report generated as security_report.md"
echo ""

section "Security Scan Complete"
echo "The security scan is now complete."
echo "Please review the generated report to address security issues."
echo ""
echo "Thank you for using the Security Scanner script."