import subprocess
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class GitCommit:
    sha: str
    short_sha: str
    message: str
    parents: List[str]
    author: str
    date: str


class RenderEngine(ABC):
    @abstractmethod
    def render(self, commits: List[GitCommit], output_path: str, **kwargs) -> None:
        pass
    
    @abstractmethod
    def supports_format(self, format_type: str) -> bool:
        pass


class PyVisEngine(RenderEngine):
    def __init__(self):
        self.available = self._check_pyvis_available()
    
    def _check_pyvis_available(self) -> bool:
        try:
            import pyvis
            return True
        except ImportError:
            return False
    
    def supports_format(self, format_type: str) -> bool:
        return format_type.lower() == 'html'
    
    def render(self, commits: List[GitCommit], output_path: str, **kwargs) -> None:
        if not self.available:
            raise RuntimeError("PyVis is not available. Install with: pip install pyvis")
        
        from pyvis.network import Network
        
        # Create network
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
        net.set_options("""
        var options = {
            "physics": {
                "enabled": true,
                "stabilization": {"iterations": 100}
            }
        }
        """)
        
        # Add nodes
        for commit in commits:
            title = f"SHA: {commit.sha}\nAuthor: {commit.author}\nDate: {commit.date}\nMessage: {commit.message}"
            net.add_node(
                commit.sha,
                label=f"{self._truncate_message(commit.message)}",
                title=title,
                color="#97C2FC"
            )
        
        # Add edges
        for commit in commits:
            for parent_sha in commit.parents:
                if any(c.sha == parent_sha for c in commits):
                    net.add_edge(parent_sha, commit.sha, color="gray")
        
        # Ensure output has .html extension
        if not output_path.endswith('.html'):
            output_path += '.html'
        
        # Save the network
        net.save_graph(output_path)
        print(f"Interactive graph rendered to {output_path}")
    
    def _truncate_message(self, message: str, max_length: int = 25) -> str:
        if len(message) <= max_length:
            return message
        return message[:max_length-3] + "..."


class MatplotlibEngine(RenderEngine):
    def __init__(self):
        self.available = self._check_matplotlib_available()
    
    def _check_matplotlib_available(self) -> bool:
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            import networkx as nx
            return True
        except ImportError:
            return False
    
    def supports_format(self, format_type: str) -> bool:
        return format_type.lower() in ['png', 'svg', 'pdf', 'jpg', 'jpeg']
    
    def render(self, commits: List[GitCommit], output_path: str, **kwargs) -> None:
        if not self.available:
            raise RuntimeError("Matplotlib is not available. Install with: pip install matplotlib networkx")
        
        import matplotlib.pyplot as plt
        import networkx as nx
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes
        for commit in commits:
            G.add_node(commit.sha, 
                      label=self._truncate_message(commit.message),
                      author=commit.author,
                      date=commit.date)
        
        # Add edges
        for commit in commits:
            for parent_sha in commit.parents:
                if any(c.sha == parent_sha for c in commits):
                    G.add_edge(parent_sha, commit.sha)
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Use hierarchical layout for better visualization
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_color='lightblue',
                              node_size=1000,
                              alpha=0.7)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, 
                              edge_color='gray',
                              arrows=True,
                              arrowsize=20,
                              alpha=0.6)
        
        # Add labels
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title("Git Repository Visualization", fontsize=16, pad=20)
        plt.axis('off')
        
        # Determine file extension
        if not any(output_path.endswith(ext) for ext in ['.png', '.svg', '.pdf', '.jpg', '.jpeg']):
            output_path += '.png'
        
        # Save the plot
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Static graph rendered to {output_path}")
    
    def _truncate_message(self, message: str, max_length: int = 20) -> str:
        if len(message) <= max_length:
            return message
        return message[:max_length-3] + "..."


class ASCIIEngine(RenderEngine):
    def __init__(self):
        self.available = True  # No external dependencies
    
    def supports_format(self, format_type: str) -> bool:
        return format_type.lower() in ['txt', 'ascii']
    
    def render(self, commits: List[GitCommit], output_path: str, **kwargs) -> None:
        # Create ASCII representation
        ascii_graph = self._generate_ascii_graph(commits)
        
        # Determine file extension
        if not output_path.endswith('.txt'):
            output_path += '.txt'
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ascii_graph)
        
        print(f"ASCII graph rendered to {output_path}")
        print("\n" + "="*50)
        print("ASCII Preview:")
        print("="*50)
        print(ascii_graph)
    
    def _generate_ascii_graph(self, commits: List[GitCommit]) -> str:
        if not commits:
            return "No commits found."
        
        # Create a simple tree representation
        lines = []
        lines.append("Git Repository Visualization (ASCII)")
        lines.append("=" * 50)
        lines.append("")
        
        # Group commits by their depth in the tree
        commit_map = {commit.sha: commit for commit in commits}
        depth_map = {}
        
        # Calculate depths (simplified approach)
        for commit in commits:
            if not commit.parents or not any(p in commit_map for p in commit.parents):
                depth_map[commit.sha] = 0
            else:
                max_parent_depth = max(depth_map.get(p, 0) for p in commit.parents if p in commit_map)
                depth_map[commit.sha] = max_parent_depth + 1
        
        # Sort commits by depth and date
        sorted_commits = sorted(commits, key=lambda c: (depth_map.get(c.sha, 0), c.date))
        
        # Generate ASCII tree
        for i, commit in enumerate(sorted_commits):
            depth = depth_map.get(commit.sha, 0)
            indent = "  " * depth
            
            # Tree connector
            if i == len(sorted_commits) - 1:
                connector = "└── "
            else:
                connector = "├── "
            
            # Commit line
            short_msg = self._truncate_message(commit.message, 40)
            commit_line = f"{indent}{connector}{commit.short_sha} {short_msg}"
            lines.append(commit_line)
            
            # Author and date info
            info_line = f"{indent}    Author: {commit.author}"
            lines.append(info_line)
            date_line = f"{indent}    Date: {commit.date}"
            lines.append(date_line)
            lines.append("")
        
        # Add summary
        lines.append("=" * 50)
        lines.append(f"Total commits: {len(commits)}")
        lines.append(f"Date range: {sorted_commits[-1].date} to {sorted_commits[0].date}")
        
        return "\n".join(lines)
    
    def _truncate_message(self, message: str, max_length: int = 40) -> str:
        if len(message) <= max_length:
            return message
        return message[:max_length-3] + "..."


class GitRepository:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self._validate_git_repo()
    
    def _validate_git_repo(self) -> None:
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(f"Not a git repository: {self.repo_path}")
    
    def get_commits(self, max_commits: int = 100) -> List[GitCommit]:
        # Git log format: SHA|SHORT_SHA|MESSAGE|PARENTS|AUTHOR|DATE
        format_str = "%H|%h|%s|%P|%an|%ai"
        
        try:
            result = subprocess.run([
                "git", "log",
                f"--max-count={max_commits}",
                f"--pretty=format:{format_str}",
                "--all"
            ], cwd=self.repo_path, capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 6:
                    sha, short_sha, message, parents_str, author, date = parts[:6]
                    parents = parents_str.split() if parents_str else []
                    
                    commits.append(GitCommit(
                        sha=sha,
                        short_sha=short_sha,
                        message=message,
                        parents=parents,
                        author=author,
                        date=date
                    ))
            
            return commits
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to retrieve git log: {e}")


class GitViz:
    def __init__(self):
        self.engines = {
            'pyvis': PyVisEngine(),
            'matplotlib': MatplotlibEngine(),
            'ascii': ASCIIEngine()
        }
    
    def get_available_engines(self) -> List[str]:
        return [name for name, engine in self.engines.items() if engine.available]
    
    def visualize(self, 
                  repo_path: str = ".",
                  engine: str = "auto",
                  output_path: str = "git_graph",
                  format_type: str = "html",
                  max_commits: int = 100) -> None:
        
        # Auto-select engine if needed
        if engine == "auto":
            available = self.get_available_engines()
            if not available:
                raise RuntimeError("No rendering engines available. Install pyvis, matplotlib, or use ascii engine.")
            
            # Auto-select based on format
            if format_type.lower() == "html" and "pyvis" in available:
                engine = "pyvis"
            elif format_type.lower() in ["png", "svg", "pdf", "jpg", "jpeg"] and "matplotlib" in available:
                engine = "matplotlib"
            elif format_type.lower() in ["txt", "ascii"]:
                engine = "ascii"
            else:
                # Fallback to first available engine
                engine = available[0]
        
        # Validate engine
        if engine not in self.engines:
            raise ValueError(f"Unknown engine: {engine}")
        
        selected_engine = self.engines[engine]
        if not selected_engine.available:
            raise RuntimeError(f"Engine '{engine}' is not available")
        
        # Validate format
        if not selected_engine.supports_format(format_type):
            raise ValueError(f"Engine '{engine}' does not support format '{format_type}'")
        
        # Get repository data
        repo = GitRepository(repo_path)
        commits = repo.get_commits(max_commits)
        
        if not commits:
            raise RuntimeError("No commits found in repository")
        
        print(f"Found {len(commits)} commits")
        print(f"Using {engine} engine to generate {format_type} output")
        
        # Render graph
        selected_engine.render(commits, output_path, format_type=format_type)