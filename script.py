import os
import re
from difflib import SequenceMatcher
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

# Constants
LONG_METHOD_THRESHOLD = 10  # Lines
DUPLICATE_SIMILARITY_THRESHOLD = 0.9  # Similarity for duplicates

def extract_methods_and_comments(file_content, file_name):
    """Extract methods and comments from C++ code."""
    methods = []
    comments = []
    current_method = []
    method_start_line = None
    inside_method = False

    lines = file_content.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect comments
        if stripped.startswith("//") or stripped.startswith("/*"):
            comments.append((file_name, i + 1, stripped))  # Track file and line number
            continue

        # Detect method start (simplistic)
        if re.match(r".*\s+\w+\(.*\)\s*{", stripped):  # Matches returnType funcName(args) {
            if inside_method:
                methods.append((file_name, method_start_line, "\n".join(current_method)))
                current_method = []
            inside_method = True
            method_start_line = i + 1

        if inside_method:
            current_method.append(line)

        if stripped.endswith("}") and inside_method:
            methods.append((file_name, method_start_line, "\n".join(current_method)))
            current_method = []
            inside_method = False

    return methods, comments

def detect_long_methods(methods):
    """Detect long methods"""
    long_methods = []
    for file_name, start_line, method in methods:
        # Exclude main() from analysis
        if re.match(r".*\bmain\s*\(.*\)", method):
            continue
        if method.count("\n") > LONG_METHOD_THRESHOLD:
            long_methods.append((file_name, start_line, method))
    return long_methods

def detect_duplicate_code(methods):
    """Detect duplicate code blocks."""
    duplicates = []
    for i, (file1, line1, method1) in enumerate(methods):
        for j, (file2, line2, method2) in enumerate(methods):
            if i != j and SequenceMatcher(None, method1, method2).ratio() > DUPLICATE_SIMILARITY_THRESHOLD:
                duplicates.append((file1, line1, file2, line2))
    return duplicates

def analyze_cpp_project(root_dir):
    """Analyze a C++ project for code smells."""
    results = {
        "long_methods": [],
        "duplicate_code": [],
    }
    all_methods = []
    all_comments = []

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".cpp") or file.endswith(".h"):
                file_path = os.path.join(subdir, file)
                with open(file_path, "r") as f:
                    content = f.read()
                    methods, comments = extract_methods_and_comments(content, file)
                    all_methods.extend(methods)
                    all_comments.extend(comments)

    # Detect smells
    results["long_methods"] = detect_long_methods(all_methods)
    results["duplicate_code"] = detect_duplicate_code(all_methods)

    return results

def generate_report(results, output_file="code_smells_report.md"):
    """Generate a Markdown report for the code smells."""
    with open(output_file, "w") as f:
        f.write("# Code Smells Report\n\n")

        # Long Methods
        long_methods_count = len(results["long_methods"])
        f.write(f"## Long Methods ({long_methods_count})\n")
        if long_methods_count:
            for file, line, method in results["long_methods"]:
                f.write(f"Detected in `{file}` at Line {line}:\n```\n{method}\n```\n")
        else:
            f.write("No long methods detected.\n")

        # Duplicate Code
        duplicate_code_count = len(results["duplicate_code"])
        f.write(f"\n## Duplicate Code ({duplicate_code_count})\n")
        if duplicate_code_count:
            for file1, line1, file2, line2 in results["duplicate_code"]:
                f.write(f"Duplicate between `{file1}` (Line {line1}) and `{file2}` (Line {line2})\n")
        else:
            f.write("No duplicate code detected.\n")

def display_report_cli(results):
    """Display the code smells report in the CLI."""
    console = Console()

    # Title
    console.print("# Code Smells Report\n", style="bold green")

    # Long Methods
    long_methods_count = len(results["long_methods"])
    console.print(f"## Long Methods ({long_methods_count})", style="bold cyan")
    if long_methods_count:
        for file, line, method in results["long_methods"]:
            console.print(f"[bold yellow]File:[/bold yellow] {file} [bold yellow]Line:[/bold yellow] {line}")
            console.print(f"[italic]{method}[/italic]\n", style="dim")
    else:
        console.print("No long methods detected.\n", style="dim")

    # Duplicate Code
    duplicate_code_count = len(results["duplicate_code"])
    console.print(f"\n## Duplicate Code ({duplicate_code_count})", style="bold cyan")
    if duplicate_code_count:
        table = Table(title="Duplicate Code", show_header=True, header_style="bold magenta")
        table.add_column("File 1", justify="left")
        table.add_column("Line 1", justify="center")
        table.add_column("File 2", justify="left")
        table.add_column("Line 2", justify="center")

        for file1, line1, file2, line2 in results["duplicate_code"]:
            table.add_row(file1, str(line1), file2, str(line2))
        console.print(table)
    else:
        console.print("No duplicate code detected.\n", style="dim")

if __name__ == "__main__":
    project_dir = input("Enter the path to the project directory: ").strip()
    output_file = "code_smells_report.md"

    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} is not a valid directory.")
    else:
        results = analyze_cpp_project(project_dir)
        generate_report(results, output_file)
        print(f"Analysis complete! Report saved to {output_file}")
