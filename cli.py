import argparse


def get_username():
    """Parse and return the Chess.com username from command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Chess stats analyzer"
    )
    parser.add_argument("username", help="Chess.com username")
    args = parser.parse_args()
    return args.username
