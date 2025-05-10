#!/bin/bash

# Script to update the progress log
# Created as part of the Dev-Server-Workflow production readiness project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Progress Update"
echo "This script will update the progress log for the Dev-Server-Workflow production readiness project."
echo ""

# Get task information
echo "Please enter the task completed:"
read TASK

if [ -z "$TASK" ]; then
    echo "❌ Task cannot be empty"
    exit 1
fi

echo "Please enter any issues encountered (press Enter if none):"
read ISSUES

echo "Please enter the next steps:"
read NEXT_STEPS

if [ -z "$NEXT_STEPS" ]; then
    echo "❌ Next steps cannot be empty"
    exit 1
fi

# Create progress log file if it doesn't exist
if [ ! -f "progress_log.md" ]; then
    cat > progress_log.md << EOF
# Dev-Server-Workflow Production Readiness Project Progress Log

This log tracks the progress of the Dev-Server-Workflow production readiness project.

## Progress Log

EOF
fi

# Update progress log
echo "Updating progress log..."

cat >> progress_log.md << EOF
### $(date +"%Y-%m-%d %H:%M:%S")

**Task Completed:** $TASK

EOF

if [ -n "$ISSUES" ]; then
    cat >> progress_log.md << EOF
**Issues Encountered:** $ISSUES

EOF
fi

cat >> progress_log.md << EOF
**Next Steps:** $NEXT_STEPS

---

EOF

echo "Progress log updated."
echo ""

# Final message
section "Progress Update Complete"
echo "The progress update is now complete."
echo "The progress log has been updated at progress_log.md."
echo ""
echo "Thank you for using the Progress Update script."