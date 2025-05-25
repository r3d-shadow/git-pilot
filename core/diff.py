from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import difflib
import sys
import termios
import tty

console = Console()

def generate_diff(old_content, new_content, file_path):
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
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def interactive_diff_view(file_diffs):
    """
    Interactive viewer with always-visible confirmation prompt.
    Returns True if 'y', False if 'n'
    """
    selected = 0
    show_diff = [False] * len(file_diffs)

    while True:
        console.clear()
        console.print("[bold cyan]Interactive Dry Run Diff Viewer[/bold cyan]")
        console.print("Use [green]↑ ↓[/green] to navigate, [yellow]Enter[/yellow] to toggle diff, type [bold]y[/bold] or [bold]n[/bold] to confirm.\n")

        for i, (repo_name, operation, file_path, old_content, new_content) in enumerate(file_diffs):
            prefix = "👉" if i == selected else "  "
            can_show_diff = (isinstance(old_content, str) and old_content.strip()) or \
                            (isinstance(new_content, str) and new_content.strip())

            if can_show_diff:
                status = "[green](shown)[/green]" if show_diff[i] else "[red](hidden)[/red]"
            else:
                status = "[grey62](no content)[/grey62]"
                show_diff[i] = False

            label = f"{prefix} {repo_name}/{file_path} [{operation.upper()}] {status}"
            console.print(label)

            if show_diff[i] and can_show_diff:
                console.print(generate_diff(old_content, new_content, file_path))

        # Always show confirmation prompt
        console.print("\n[bold yellow]Do you want to apply these changes? (Y/N)[/bold yellow]: ", end="")
        console.file.flush()

        key = read_key()
        if key.lower() == 'y':
            return True
        elif key.lower() == 'n':
            return False
        elif key == "\x1b[A":  # up arrow
            selected = (selected - 1) % len(file_diffs)
        elif key == "\x1b[B":  # down arrow
            selected = (selected + 1) % len(file_diffs)
        elif key == "\r":  # enter
            can_show = (isinstance(file_diffs[selected][3], str) and file_diffs[selected][3].strip()) or \
                       (isinstance(file_diffs[selected][4], str) and file_diffs[selected][4].strip())
            if can_show:
                show_diff[selected] = not show_diff[selected]