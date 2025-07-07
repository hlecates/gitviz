import argparse
import sys
import os
from typing import Optional

from .core import GitViz


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Visualize Git repository structure as a DAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--path",
        default=".",
        help="Path to Git repository (default: current directory)"
    )
    
    parser.add_argument(
        "--engine",
        choices=["pyvis", "matplotlib", "ascii", "auto"],
        default="auto",
        help="Rendering engine to use (default: auto)"
    )
    
    parser.add_argument(
        "--format",
        choices=["html", "png", "svg", "pdf", "jpg", "jpeg", "txt", "ascii"],
        default="html",
        help="Output format (default: html)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="git_graph",
        help="Output file name without extension (default: git_graph)"
    )
    
    parser.add_argument(
        "--max-commits",
        type=int,
        default=100,
        help="Maximum number of commits to include (default: 100)"
    )
    
    parser.add_argument(
        "--list-engines",
        action="store_true",
        help="List available rendering engines and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def validate_args(args: argparse.Namespace) -> None:
    # Check if repository path exists
    if not os.path.exists(args.path):
        print(f"Error: Repository path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # Validate max commits
    if args.max_commits <= 0:
        print("Error: --max-commits must be a positive integer", file=sys.stderr)
        sys.exit(1)
    
    # Auto-select engine based on format if needed
    if args.engine == "auto":
        if args.format in ["html"]:
            args.engine = "pyvis"
        elif args.format in ["png", "svg", "pdf", "jpg", "jpeg"]:
            args.engine = "matplotlib"
        elif args.format in ["txt", "ascii"]:
            args.engine = "ascii"
        else:
            args.engine = "pyvis"  # fallback
    
    # Format-specific validations
    if args.format == "html" and args.engine != "pyvis":
        print("Warning: HTML format requires PyVis engine, switching to 'pyvis'")
        args.engine = "pyvis"
    
    if args.format in ["png", "svg", "pdf", "jpg", "jpeg"] and args.engine not in ["matplotlib"]:
        print(f"Warning: {args.format} format requires matplotlib engine, switching to 'matplotlib'")
        args.engine = "matplotlib"
    
    if args.format in ["txt", "ascii"] and args.engine not in ["ascii"]:
        print(f"Warning: {args.format} format requires ascii engine, switching to 'ascii'")
        args.engine = "ascii"


def list_engines() -> None:
    gitviz = GitViz()
    available = gitviz.get_available_engines()
    
    print("Available rendering engines:")
    print()
    
    engines_info = {
        'pyvis': {
            'description': 'Interactive HTML visualizations',
            'formats': ['html'],
            'install': 'pip install pyvis'
        },
        'matplotlib': {
            'description': 'Static high-quality plots for publications',
            'formats': ['png', 'svg', 'pdf', 'jpg', 'jpeg'],
            'install': 'pip install matplotlib networkx'
        },
        'ascii': {
            'description': 'Terminal-based text visualizations',
            'formats': ['txt', 'ascii'],
            'install': 'No dependencies required'
        }
    }
    
    for engine_name, info in engines_info.items():
        status = "Available" if engine_name in available else "Not installed"
        print(f"  {engine_name:<12} {status}")
        print(f"             {info['description']}")
        print(f"             Formats: {', '.join(info['formats'])}")
        if engine_name not in available:
            print(f"             Install: {info['install']}")
        print()


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_engines:
        list_engines()
        return
    
    # Validate arguments
    validate_args(args)
    
    try:
        # Create GitViz instance and generate visualization
        gitviz = GitViz()
        
        # Check if any engines are available
        available_engines = gitviz.get_available_engines()
        if not available_engines:
            print("Error: No rendering engines available!", file=sys.stderr)
            print("Install the following:", file=sys.stderr)
            print("  pip install pyvis", file=sys.stderr)
            sys.exit(1)
        
        gitviz.visualize(
            repo_path=args.path,
            engine=args.engine,
            output_path=args.output,
            format_type=args.format,
            max_commits=args.max_commits
        )
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()