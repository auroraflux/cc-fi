"""Main CLI entry point for cc-fi."""

import argparse
import logging
import sys

from cc_fi.core.cache import get_sessions_with_cache, invalidate_cache
from cc_fi.core.formatter import format_list_header, format_list_row, format_fzf_preview
from cc_fi.core.search import filter_sessions, get_session_by_id


def setup_logging(verbose: bool) -> None:
    """
    Configure logging based on verbosity flag.

    @param verbose Enable debug logging if True
    @complexity O(1)
    @pure false - modifies global logging state
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=level,
    )


def print_sessions_list(sessions: list, show_header: bool = True) -> None:
    """
    Print sessions in columnar format.

    @param sessions List of SessionData to print
    @param show_header Print header row if True
    @complexity O(n) where n is number of sessions
    @pure false - writes to stdout
    """
    from cc_fi.core.formatter import format_header_separator

    if show_header:
        print(format_list_header())
        print(format_header_separator())

    for session in sessions:
        print(format_list_row(session))


def handle_preview_mode(session_id: str) -> None:
    """
    Handle --preview mode for fzf integration.

    @param session_id Session ID to preview
    @complexity O(n) where n is cached sessions
    @pure false - reads cache, writes to stdout
    """
    import logging

    logging.disable(logging.CRITICAL)

    sessions = get_sessions_with_cache()
    session = get_session_by_id(sessions, session_id)

    if session:
        print(format_fzf_preview(session))
    else:
        print(f"Session not found: {session_id}")


def handle_interactive_mode() -> None:
    """
    Handle interactive mode with fzf.

    @complexity O(n) where n is number of sessions
    @pure false - launches fzf subprocess
    """
    import logging
    from cc_fi.core.fzf import run_fzf_selection

    logging.disable(logging.CRITICAL)

    sessions = get_sessions_with_cache()

    if not sessions:
        print("No sessions found.")
        return

    selected = run_fzf_selection(sessions)

    if selected:
        resume_cmd = f'cd "{selected.cwd}" && claude -r {selected.session_id}'
        print("\nTo resume this session, run:")
        print(f"\n  {resume_cmd}\n")


def handle_list_mode(search_term: str, force_rebuild: bool) -> None:
    """
    Handle list/search mode.

    @param search_term Search term to filter (empty for all)
    @param force_rebuild Force cache rebuild if True
    @complexity O(n) where n is number of sessions
    @pure false - reads cache/filesystem
    """
    sessions = get_sessions_with_cache(force_rebuild=force_rebuild)

    if search_term:
        sessions = filter_sessions(sessions, search_term)

    if not sessions:
        print("No sessions found.")
        return

    print_sessions_list(sessions)


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.

    @returns Configured ArgumentParser
    @complexity O(1)
    @pure true
    """
    parser = argparse.ArgumentParser(
        prog="cc-fi",
        description="Find and resume Claude Code sessions",
        epilog="Examples:\n"
        "  cc-fi                    Interactive mode (default)\n"
        "  cc-fi -l                 List all sessions\n"
        "  cc-fi -l search-term     List filtered sessions\n"
        "  cc-fi -r                 Force rebuild cache\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "search",
        nargs="?",
        default="",
        help="Search term to filter sessions (use with -l)",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List sessions instead of interactive mode",
    )

    parser.add_argument(
        "-r",
        "--rebuild",
        action="store_true",
        help="Force rebuild cache",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--preview",
        metavar="SESSION_ID",
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear cache and exit",
    )

    return parser


def main() -> int:
    """
    Main entry point for cc-fi CLI.

    @returns Exit code (0 for success, 1 for error)
    @complexity Varies by mode
    @pure false - handles all I/O and state
    """
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        if args.clear_cache:
            invalidate_cache()
            print("Cache cleared.")
            return 0

        if args.preview:
            handle_preview_mode(args.preview)
            return 0

        if args.list:
            handle_list_mode(args.search, args.rebuild)
            return 0

        # Default: interactive mode
        handle_interactive_mode()
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
