from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import difflib
from io import StringIO

console = Console()

def generate_diff(old_content, new_content, file_path):
    if old_content is None:
        old_content = ""

    diff_lines = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm=""
    )
    diff_text = "\n".join(diff_lines)
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
    
    with StringIO() as buf:
        temp_console = Console(file=buf, force_terminal=True, color_system="truecolor", width=console.width)
        temp_console.print(Panel(syntax, title=f"Diff for {file_path}"))
        return buf.getvalue()
