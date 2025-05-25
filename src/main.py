from src.cli.parsers import build_parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.command.execute(args)

if __name__ == "__main__":
    main()
