import sys
import termios
import tty
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from src.core.interfaces import DiffViewerInterface
from .generator import DiffGenerator

class RichDiffViewer(DiffViewerInterface):
    def __init__(self):
        self.console = Console()

    def _read_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

    def _render(self, file_diffs, selected, show_flags):
        table = Table.grid(expand=True)
        table.add_column()
        table.add_column()
        table.add_column()

        header = "[bold cyan]Diff Viewer[/bold cyan]\n" \
                 "Use [green]↑ ↓[/green] to navigate, [yellow]Enter[/yellow] to toggle diff, [bold]y[/bold]/[bold]n[/bold] to confirm.\n"
        table.add_row("", header, "")

        for idx, (repo, branch, op, path, old, new) in enumerate(file_diffs):
            prefix = "👉" if idx == selected else "  "
            can_show = bool((old and old.strip()) or (new and new.strip()))
            status = (
                "[green](shown)[/green]" if show_flags[idx] and can_show else
                "[red](hidden)[/red]" if can_show else
                "[grey62](no content)[/grey62]"
            )
            table.add_row(prefix, f"{repo} ({branch})/{path} [{op.upper()}]", status)

            if show_flags[idx] and can_show:
                diff_panel = DiffGenerator.generate(old, new, path)
                # Put diff_panel spanning columns to keep layout neat
                table.add_row("", diff_panel, "")

        footer = "[bold yellow]Apply these changes? (y/n)[/bold yellow]: "
        table.add_row("", footer, "")

        return Panel(table, border_style="bright_blue")

    def show(self, file_diffs):
        selected = 0
        show_flags = [False] * len(file_diffs)

        with Live(console=self.console, screen=False, auto_refresh=False) as live:
            while True:
                live.update(self._render(file_diffs, selected, show_flags), refresh=True)

                key = self._read_key()
                if key.lower() == 'y':
                    return True
                if key.lower() == 'n':
                    return False
                if key == "\x1b[A":  # up arrow
                    selected = (selected - 1) % len(file_diffs)
                elif key == "\x1b[B":  # down arrow
                    selected = (selected + 1) % len(file_diffs)
                elif key == "\r":  # enter
                    if bool((file_diffs[selected][4] or "").strip()) or bool((file_diffs[selected][5] or "").strip()):
                        show_flags[selected] = not show_flags[selected]