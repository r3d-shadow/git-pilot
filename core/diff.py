from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import difflib
import sys
import termios
import tty

console = Console()

def generate_diff(old_content, new_content, file_path):
    # Ensure contents are strings to avoid attribute errors
    if not isinstance(old_content, str):
        old_content = ""
    if not isinstance(new_content, str):
        new_content = ""

    diff_lines = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm=""
    )
    diff_text = "\n".join(diff_lines)
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
    return Panel(syntax, title=f"Diff for {file_path}")

def read_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch += sys.stdin.read(2)  # Read full escape sequence
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def interactive_diff_view(file_diffs):
    """
    file_diffs: List of tuples in format:
        (repo_name, operation, file_path, old_content, new_content)
    """
    selected = 0
    show_diff = [False] * len(file_diffs)

    while True:
        console.clear()
        console.print("[bold]Interactive Dry Run Diff Viewer[/bold]")
        console.print("Press [green]Enter[/green] to toggle diff, [↑↓] to navigate, [red]q[/red] to quit.\n")

        for i, (repo_name, operation, file_path, old_content, new_content) in enumerate(file_diffs):
            prefix = "👉" if i == selected else "  "

            # Check if we have valid string content to display diff
            can_show_diff = (isinstance(old_content, str) and old_content.strip() != "") or \
                            (isinstance(new_content, str) and new_content.strip() != "")

            if can_show_diff:
                status = "[green](shown)[/green]" if show_diff[i] else "[red](hidden)[/red]"
            else:
                # No valid content to show diff
                status = "[grey62](no content)[/grey62]"
                # Always hide diffs if no content (force hide_diff to False)
                show_diff[i] = False

            label = f"{prefix} {repo_name}/{file_path} [{operation.upper()}] {status}"
            console.print(label)

            # Show diff panel only if toggled and content exists
            if show_diff[i] and can_show_diff:
                panel = generate_diff(old_content, new_content, file_path)
                console.print(panel)

        key = read_key()
        if key == "q":
            break
        elif key in ("\x1b[A", "\x1b[B"):
            selected = (selected - 1) % len(file_diffs) if key == "\x1b[A" else (selected + 1) % len(file_diffs)
        elif key == "\r":
            # Only toggle if content is valid
            _, operation, _, old_content, new_content = file_diffs[selected]
            can_show_diff = (isinstance(old_content, str) and old_content.strip() != "") or \
                            (isinstance(new_content, str) and new_content.strip() != "")
            if can_show_diff:
                show_diff[selected] = not show_diff[selected]
