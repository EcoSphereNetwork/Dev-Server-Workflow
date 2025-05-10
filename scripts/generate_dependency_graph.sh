#!/bin/bash

# Script to generate a dependency graph for the repository
# Created as part of the Dev-Server-Workflow repository cleanup project

# Function to display section header
section() {
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

# Display welcome message
section "Dependency Graph Generator"
echo "This script will generate a dependency graph for the Dev-Server-Workflow repository."
echo ""

# Check if graphviz is installed
if ! command -v dot &> /dev/null; then
    echo "Graphviz is not installed. Installing..."
    apt-get update && apt-get install -y graphviz
    echo "Graphviz installed."
    echo ""
fi

# Generate dependency graph for Python files
section "Generating Python Dependency Graph"
echo "Generating dependency graph for Python files..."

# Create a temporary file to store the graph
graph_file=$(mktemp)

# Start the graph
echo "digraph G {" > $graph_file
echo "  rankdir=LR;" >> $graph_file
echo "  node [shape=box, style=filled, fillcolor=lightblue];" >> $graph_file

# Find all Python files
python_files=$(find . -name "*.py" -not -path "*/\.*" -not -path "*/legacy/*" -not -path "*/node_modules/*")

# Process each Python file
for file in $python_files; do
    # Get the module name
    module=$(echo $file | sed 's/\.\///g' | sed 's/\.py$//g' | sed 's/\//./g')
    
    # Add the module to the graph
    echo "  \"$module\" [label=\"$module\"];" >> $graph_file
    
    # Find all imports in the file
    imports=$(grep -E "^(import|from) " $file | grep -v "import *$" | sed 's/^from \([^ ]*\) import.*/\1/g' | sed 's/^import \([^,]*\).*/\1/g' | sort | uniq)
    
    # Add edges for each import
    for import in $imports; do
        # Skip standard library imports
        if [[ ! $import =~ ^(os|sys|re|json|time|datetime|logging|argparse|pathlib|shutil|subprocess|tempfile|threading|uuid|math|random|collections|itertools|functools|operator|typing|enum|abc|io|socket|http|urllib|ssl|email|xml|html|csv|sqlite3|pickle|shelve|configparser|hashlib|base64|hmac|secrets|zlib|gzip|tarfile|zipfile|struct|array|heapq|bisect|weakref|copy|pprint|textwrap|locale|gettext|unicodedata|stringprep|readline|rlcompleter|code|codeop|dis|inspect|site|stat|fileinput|filecmp|linecache|tokenize|token|keyword|parser|ast|symtable|symbol|traceback|__future__|gc|atexit|builtins|warnings|contextlib|dataclasses|_thread|_dummy_thread|dummy_threading|distutils|importlib|pkgutil|modulefinder|runpy|glob|fnmatch|posixpath|ntpath|genericpath|macpath|posix|nt|os.path|sysconfig|platform|pydoc|doctest|unittest|test|bdb|pdb|profile|cProfile|timeit|trace|tracemalloc|py_compile|compileall|zipapp|faulthandler|tty|pty|fcntl|pipes|resource|nis|syslog|aifc|asynchat|asyncore|audioop|cgi|cgitb|chunk|colorsys|crypt|imaplib|mailbox|mailcap|mimetypes|nntplib|optparse|ossaudiodev|pipes|poplib|pty|pwd|pyclbr|queue|select|selectors|smtpd|smtplib|sndhdr|spwd|sunau|telnetlib|termios|test|uu|wave|webbrowser|xdrlib|zipimport|antigravity|this|lib2to3|2to3|idle|turtledemo|turtle|cmd|shlex|netrc|pstats|tkinter|curses|venv|ensurepip|tomllib|wsgiref|multiprocessing|concurrent|asyncio|mmap|msvcrt|winreg|winsound|cmath|decimal|fractions|numbers|statistics|ctypes|msilib|wincertstore|lzma|bz2|binascii|quopri|uu|formatter|imp|sre|sre_compile|sre_constants|sre_parse|copyreg|sets|__phello__|_bootlocale|_collections_abc|_compat_pickle|_compression|_dummy_thread|_markupbase|_osx_support|_py_abc|_pydecimal|_pyio|_sitebuiltins|_strptime|_sysconfigdata|_sysconfigdata_m|_threading_local|_weakrefset|genericpath|ntpath|posixpath|sre_constants|sre_parse|sre_compile|stat|reprlib|heapq|_heapq|types|weakref|_weakref|_collections|_functools|_locale|_io|_stat|_warnings|_stat|_thread|_signal|_tracemalloc|_symtable|_ast|_imp|_frozen_importlib|_frozen_importlib_external|_sre|_codecs|_codecs_cn|_codecs_hk|_codecs_iso2022|_codecs_jp|_codecs_kr|_codecs_tw|_multibytecodec|_string|_opcode|_json|_sha1|_sha256|_sha512|_md5|_blake2|_sha3|_random|_bisect|_datetime|_zoneinfo|_bz2|_lzma|_socket|_ssl|_hashlib|_uuid|_posixsubprocess|_scproxy|_winapi|_msi|_overlapped|_asyncio|_queue|_contextvars|_decimal|_peg_parser|_typing|_abc|_csv|_pickle|_elementtree|_struct|_xxsubinterpreters|_xxinterpchannels|_xxsubinterpreters|_posixshmem|_multiprocessing|_ctypes|_ctypes_test|_testbuffer|_testinternalcapi|_testimportmultiple|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype|_crypt|_curses|_curses_panel|_dbm|_gdbm|_tkinter|_sqlite3|_statistics|_testcapi|_testclinic|_testfunc|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype|_decimal|_peg_parser|_typing|_abc|_csv|_pickle|_elementtree|_struct|_xxsubinterpreters|_xxinterpchannels|_xxsubinterpreters|_posixshmem|_multiprocessing|_ctypes|_ctypes_test|_testbuffer|_testinternalcapi|_testimportmultiple|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype|_crypt|_curses|_curses_panel|_dbm|_gdbm|_tkinter|_sqlite3|_statistics|_testcapi|_testclinic|_testfunc|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype)(\.|$) ]]; then
            # Check if the import is a module in the repository
            if grep -q "^$import$" <(echo "$python_files" | sed 's/\.\///g' | sed 's/\.py$//g' | sed 's/\//./g'); then
                echo "  \"$module\" -> \"$import\";" >> $graph_file
            fi
        fi
    done
done

# End the graph
echo "}" >> $graph_file

# Generate the graph image
dot -Tpng $graph_file -o dependency_graph.png

# Generate the graph in Markdown format
section "Generating Markdown Dependency Documentation"
echo "Generating dependency documentation in Markdown format..."

# Create the Markdown file
echo "# Dependency Graph" > dependency_graph.md
echo "" >> dependency_graph.md
echo "This document provides a comprehensive overview of the dependencies between components in the Dev-Server-Workflow repository." >> dependency_graph.md
echo "" >> dependency_graph.md

# Add the graph image
echo "## Visual Dependency Graph" >> dependency_graph.md
echo "" >> dependency_graph.md
echo "![Dependency Graph](dependency_graph.png)" >> dependency_graph.md
echo "" >> dependency_graph.md

# Add the dependency list
echo "## Component Dependencies" >> dependency_graph.md
echo "" >> dependency_graph.md

# Process each Python file
for file in $python_files; do
    # Get the module name
    module=$(echo $file | sed 's/\.\///g' | sed 's/\.py$//g' | sed 's/\//./g')
    
    # Add the module to the documentation
    echo "### $module" >> dependency_graph.md
    echo "" >> dependency_graph.md
    
    # Find all imports in the file
    imports=$(grep -E "^(import|from) " $file | grep -v "import *$" | sed 's/^from \([^ ]*\) import.*/\1/g' | sed 's/^import \([^,]*\).*/\1/g' | sort | uniq)
    
    # Add dependencies
    echo "Dependencies:" >> dependency_graph.md
    echo "" >> dependency_graph.md
    
    if [ -z "$imports" ]; then
        echo "- None" >> dependency_graph.md
    else
        for import in $imports; do
            # Skip standard library imports
            if [[ ! $import =~ ^(os|sys|re|json|time|datetime|logging|argparse|pathlib|shutil|subprocess|tempfile|threading|uuid|math|random|collections|itertools|functools|operator|typing|enum|abc|io|socket|http|urllib|ssl|email|xml|html|csv|sqlite3|pickle|shelve|configparser|hashlib|base64|hmac|secrets|zlib|gzip|tarfile|zipfile|struct|array|heapq|bisect|weakref|copy|pprint|textwrap|locale|gettext|unicodedata|stringprep|readline|rlcompleter|code|codeop|dis|inspect|site|stat|fileinput|filecmp|linecache|tokenize|token|keyword|parser|ast|symtable|symbol|traceback|__future__|gc|atexit|builtins|warnings|contextlib|dataclasses|_thread|_dummy_thread|dummy_threading|distutils|importlib|pkgutil|modulefinder|runpy|glob|fnmatch|posixpath|ntpath|genericpath|macpath|posix|nt|os.path|sysconfig|platform|pydoc|doctest|unittest|test|bdb|pdb|profile|cProfile|timeit|trace|tracemalloc|py_compile|compileall|zipapp|faulthandler|tty|pty|fcntl|pipes|resource|nis|syslog|aifc|asynchat|asyncore|audioop|cgi|cgitb|chunk|colorsys|crypt|imaplib|mailbox|mailcap|mimetypes|nntplib|optparse|ossaudiodev|pipes|poplib|pty|pwd|pyclbr|queue|select|selectors|smtpd|smtplib|sndhdr|spwd|sunau|telnetlib|termios|test|uu|wave|webbrowser|xdrlib|zipimport|antigravity|this|lib2to3|2to3|idle|turtledemo|turtle|cmd|shlex|netrc|pstats|tkinter|curses|venv|ensurepip|tomllib|wsgiref|multiprocessing|concurrent|asyncio|mmap|msvcrt|winreg|winsound|cmath|decimal|fractions|numbers|statistics|ctypes|msilib|wincertstore|lzma|bz2|binascii|quopri|uu|formatter|imp|sre|sre_compile|sre_constants|sre_parse|copyreg|sets|__phello__|_bootlocale|_collections_abc|_compat_pickle|_compression|_dummy_thread|_markupbase|_osx_support|_py_abc|_pydecimal|_pyio|_sitebuiltins|_strptime|_sysconfigdata|_sysconfigdata_m|_threading_local|_weakrefset|genericpath|ntpath|posixpath|sre_constants|sre_parse|sre_compile|stat|reprlib|heapq|_heapq|types|weakref|_weakref|_collections|_functools|_locale|_io|_stat|_warnings|_stat|_thread|_signal|_tracemalloc|_symtable|_ast|_imp|_frozen_importlib|_frozen_importlib_external|_sre|_codecs|_codecs_cn|_codecs_hk|_codecs_iso2022|_codecs_jp|_codecs_kr|_codecs_tw|_multibytecodec|_string|_opcode|_json|_sha1|_sha256|_sha512|_md5|_blake2|_sha3|_random|_bisect|_datetime|_zoneinfo|_bz2|_lzma|_socket|_ssl|_hashlib|_uuid|_posixsubprocess|_scproxy|_winapi|_msi|_overlapped|_asyncio|_queue|_contextvars|_decimal|_peg_parser|_typing|_abc|_csv|_pickle|_elementtree|_struct|_xxsubinterpreters|_xxinterpchannels|_xxsubinterpreters|_posixshmem|_multiprocessing|_ctypes|_ctypes_test|_testbuffer|_testinternalcapi|_testimportmultiple|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype|_crypt|_curses|_curses_panel|_dbm|_gdbm|_tkinter|_sqlite3|_statistics|_testcapi|_testclinic|_testfunc|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype|_decimal|_peg_parser|_typing|_abc|_csv|_pickle|_elementtree|_struct|_xxsubinterpreters|_xxinterpchannels|_xxsubinterpreters|_posixshmem|_multiprocessing|_ctypes|_ctypes_test|_testbuffer|_testinternalcapi|_testimportmultiple|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype|_crypt|_curses|_curses_panel|_dbm|_gdbm|_tkinter|_sqlite3|_statistics|_testcapi|_testclinic|_testfunc|_testmultiphase|_testsinglephase|_xxtestfuzz|xxlimited|xxlimited_35|xxsubtype)(\.|$) ]]; then
                # Check if the import is a module in the repository
                if grep -q "^$import$" <(echo "$python_files" | sed 's/\.\///g' | sed 's/\.py$//g' | sed 's/\//./g'); then
                    echo "- [$import](#$import)" >> dependency_graph.md
                else
                    echo "- $import (external)" >> dependency_graph.md
                fi
            fi
        done
    fi
    
    echo "" >> dependency_graph.md
done

# Remove the temporary file
rm $graph_file

echo "Dependency graph generated as dependency_graph.png"
echo "Dependency documentation generated as dependency_graph.md"
echo ""

section "Dependency Graph Generation Complete"
echo "The dependency graph generation is now complete."
echo "Please review the generated files to understand the dependencies between components."
echo ""
echo "Thank you for using the Dependency Graph Generator script."