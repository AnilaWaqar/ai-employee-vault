#!/usr/bin/env python3
"""Initialize a new Agent Skill directory structure."""

import argparse
import sys
from pathlib import Path


def create_skill(skill_name: str, skills_path: str):
    """Create skill directory with required files."""
    base_path = Path(skills_path) / skill_name

    # Create directories
    (base_path / 'scripts').mkdir(parents=True, exist_ok=True)
    (base_path / 'references').mkdir(parents=True, exist_ok=True)
    (base_path / 'assets').mkdir(parents=True, exist_ok=True)
    print("[OK] Created skill directory")

    # Create SKILL.md
    skill_md = base_path / 'SKILL.md'
    skill_md.write_text(f"""---
name: {skill_name}
description: |
  [Describe what this skill does and when to use it]
---

# {skill_name}

## Overview
[Brief description of this skill]

## Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Rules
- [Rule 1]
- [Rule 2]
""")
    print("[OK] Created SKILL.md")

    # Create scripts/example.py
    example_py = base_path / 'scripts' / 'example.py'
    example_py.write_text(f"""# Example script for {skill_name}
# Replace this with actual implementation

def main():
    print("Running {skill_name}")

if __name__ == "__main__":
    main()
""")
    print("[OK] Created scripts/example.py")

    # Create references/api_reference.md
    api_ref = base_path / 'references' / 'api_reference.md'
    api_ref.write_text(f"""# API Reference for {skill_name}

## Functions

### main()
Main entry point for the skill.
""")
    print("[OK] Created references/api_reference.md")

    # Create assets/example_asset.txt
    asset = base_path / 'assets' / 'example_asset.txt'
    asset.write_text(f"Example asset for {skill_name}\n")
    print("[OK] Created assets/example_asset.txt")


def main():
    parser = argparse.ArgumentParser(description='Initialize a new Agent Skill')
    parser.add_argument('skill_name', help='Name of the skill to create')
    parser.add_argument('--path', default='Skills', help='Path where skills directory is located')

    args = parser.parse_args()

    print(f"\nCreating skill: {args.skill_name}")
    print(f"Location: {args.path}/{args.skill_name}")
    print("-" * 40)

    create_skill(args.skill_name, args.path)

    print("-" * 40)
    print(f"\n[DONE] Skill '{args.skill_name}' created successfully!")
    print(f"[NEXT] Now edit: {args.path}/{args.skill_name}/SKILL.md")


if __name__ == "__main__":
    main()
