# C++ Code Smell Analyzer

## Overview

The **C++ Code Smell Analyzer** is a Python tool that scans C++ projects for common code smells, including:
- Long methods.
- Duplicate code.

It provides insights to improve code readability and maintainability. The results are saved in a Markdown report or displayed interactively in the CLI.

## Features

- Detects **long methods** exceeding a customizable line threshold.
- Identifies **duplicate code** using similarity matching.
- Works with `.cpp` and `.h` files.
- Generates a user-friendly Markdown report.
- CLI output with styled visualization.

## Installation

1. Ensure Python 3.x is installed on your system.
2. Install dependencies:
   ```bash
   pip install rich
