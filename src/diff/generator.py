import difflib
from rich.syntax import Syntax
from rich.panel import Panel

class DiffGenerator:
    @staticmethod
    def generate(old, new, path):
        old_lines = (old or '').splitlines()
        new_lines = (new or '').splitlines()
        diff = difflib.unified_diff(old_lines, new_lines, fromfile=f'a/{path}', tofile=f'b/{path}', lineterm='')
        text = '\n'.join(diff)
        return Panel(Syntax(text, 'diff', line_numbers=True), title=f"Diff for {path}")
