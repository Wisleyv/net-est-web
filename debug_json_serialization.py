#!/usr/bin/env python3
"""
Diagnostic script to identify JSON serialization issues in KiloCode requests.
This script helps identify malformed Unicode escape sequences and other JSON parsing problems.
"""

import json
import re
import sys
from pathlib import Path

def find_malformed_unicode_escapes(text):
    """Find potential malformed Unicode escape sequences in text."""
    # Look for \u sequences that aren't followed by exactly 4 hex digits
    malformed_escapes = []

    # Find all \u sequences
    u_sequences = re.finditer(r'\\u', text)

    for match in u_sequences:
        start_pos = match.start()
        # Check if there are exactly 4 hex digits after \u
        after_u = text[start_pos:start_pos + 6]  # \u + 4 hex digits

        if len(after_u) < 6:
            malformed_escapes.append({
                'position': start_pos,
                'sequence': after_u,
                'issue': 'incomplete_sequence'
            })
        elif not re.match(r'\\u[0-9a-fA-F]{4}', after_u):
            malformed_escapes.append({
                'position': start_pos,
                'sequence': after_u,
                'issue': 'invalid_hex_digits'
            })

    return malformed_escapes

def analyze_file_for_json_issues(filepath):
    """Analyze a file for potential JSON serialization issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        issues = []

        # Check for backslashes that might cause JSON escaping issues
        backslash_count = content.count('\\')
        if backslash_count > 0:
            issues.append(f"Contains {backslash_count} backslash characters")

        # Check for malformed Unicode escapes
        malformed_escapes = find_malformed_unicode_escapes(content)
        if malformed_escapes:
            issues.append(f"Found {len(malformed_escapes)} malformed Unicode escape sequences")
            for escape in malformed_escapes[:5]:  # Show first 5
                issues.append(f"  Position {escape['position']}: {escape['sequence']} ({escape['issue']})")

        # Try to JSON encode the content to see if it causes issues
        try:
            json.dumps(content)
        except Exception as e:
            issues.append(f"JSON encoding failed: {str(e)}")

        return issues

    except Exception as e:
        return [f"Error analyzing file: {str(e)}"]

def main():
    """Main diagnostic function."""
    print("KiloCode JSON Serialization Diagnostic")
    print("=" * 50)

    # Analyze common file types that might be sent in requests
    file_patterns = [
        "**/*.py",
        "**/*.js",
        "**/*.json",
        "**/*.md",
        "**/*.txt",
        "**/*.ps1"
    ]

    total_issues = 0

    for pattern in file_patterns:
        print(f"\nAnalyzing {pattern} files...")
        try:
            files = list(Path(".").glob(pattern))
            files = [f for f in files if f.is_file() and f.stat().st_size > 0]

            for filepath in files[:10]:  # Limit to first 10 files per pattern
                issues = analyze_file_for_json_issues(filepath)
                if issues:
                    print(f"\n  WARNING: {filepath}:")
                    for issue in issues:
                        print(f"    - {issue}")
                    total_issues += len(issues)

        except Exception as e:
            print(f"Error processing pattern {pattern}: {e}")

    print("\nSUMMARY:")
    print(f"Total potential issues found: {total_issues}")

    if total_issues == 0:
        print("No obvious JSON serialization issues found in analyzed files.")
        print("\nThe error might be caused by:")
        print("   - Large request payload truncation")
        print("   - VS Code extension not properly escaping content")
        print("   - Buffer limits cutting off escape sequences")
    else:
        print("Potential sources of JSON parsing issues identified above.")

if __name__ == "__main__":
    main()