from src.cli.parsers import ParserBuilder
from rich.console import Console
from rich.text import Text

def main():
    console = Console()

    header = Text("Git-Pilot", style="bold dark_orange underline")
    subheader = Text(" — Sync workflows, configs, and more across 10+ repos in seconds!", style="light_salmon1")

    console.print("\n" * 1) 
    console.print(header.append(subheader))
    console.print("\n" * 1) 

    parser = ParserBuilder().with_init_command().with_sync_command().build()
    args = parser.parse_args()
    args.command.execute(args)
