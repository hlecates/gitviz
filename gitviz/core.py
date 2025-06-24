"""
Core graph construction and rendering backends for Gitviz.
"""

import subprocess
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class GitCommit:
    """Represents a Git commit with metadata."""
    sha: str
    short_sha: str
    message: str
    parents: List[str]
    author: str
    date: str


class RenderEngine(ABC):
    """Abstract base class for rendering engines."""
    
    @abstractmethod
    def render(self, commits: List[GitCommit], output_path: str, **kwargs) -> None:
        """Render the commit graph to the specified output path."""
        pass
    
    @abstractmethod
    def supports_format(self, format_type: str) -> bool:
        """Check if the engine supports the given output format."""
        pass


class GraphvizEngine(RenderEngine):
    """Graphviz rendering engine for static outputs."""
    
    def __init__(self):
        self.available = self._check_graphviz_available()
    
    def _check_graphviz_available(self) -> bool:
        """Check if Graphviz is available."""
        try:
            import graphviz
            return True
        except ImportError:
            return False
    
    def supports_format(self, format_type: str) -> bool:
        """Check if format is supported by Graphviz."""
        return format_type.lower() in ['svg', 'png', 'pdf', 'dot']
    
    def render(self, commits: List[GitCommit], output_path: str, format_type: str = 'svg') -> None:
        """Render using Graphviz."""
        if not self.available:
            raise RuntimeError("Graphviz is not available. Install with: pip install graphviz")
        
        import graphviz
        
        # Create directed graph
        dot = graphviz.Digraph(comment='Git Repository Structure')
        dot.attr(rankdir='TB', size='12,8', dpi='300')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        dot.attr('edge', color='gray', arrowhead='vee')
        
        # Add nodes for each commit
        for commit in commits:
            label = f"{commit.short_sha}\\n{self._truncate_message(commit.message)}"
            dot.node(commit.sha, label)
        
        # Add edges for parent-child relationships
        for commit in commits:
            for parent_sha in commit.parents:
                # Only add edge if parent exists in our commit list
                if any(c.sha == parent_sha for c in commits):
                    dot.edge(parent_sha, commit.sha)
        
        # Render to file
        base_name = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
        dot.render(base_name, format=format_type, cleanup=True)
        print(f"Graph rendered to {base_name}.{format_type}")
    
    def _truncate_message(self, message: str, max_length: int = 30) -> str:
        """Truncate commit message for display."""
        if len(message) <= max_length:
            return message
        return message[:max_length-3] + "..."


class PyVisEngine(RenderEngine):
    """PyVis rendering engine for interactive HTML output."""
    
    def __init__(self):
        self.available = self._check_pyvis_available()
    
    def _check_pyvis_available(self) -> bool:
        """Check if PyVis is available."""
        try:
            import pyvis
            return True
        except ImportError:
            return False
    
    def supports_format(self, format_type: str) -> bool:
        """PyVis only supports HTML format."""
        return format_type.lower() == 'html'
    
    def render(self, commits: List[GitCommit], output_path: str, **kwargs) -> None:
        """Render using PyVis."""
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
            title = f"SHA: {commit.sha}\\nAuthor: {commit.author}\\nDate: {commit.date}\\nMessage: {commit.message}"
            net.add_node(
                commit.sha,
                label=f"{commit.short_sha}\\n{self._truncate_message(commit.message)}",
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
        """Truncate commit message for display."""
        if len(message) <= max_length:
            return message
        return message[:max_length-3] + "..."


class GitRepository:
    """Handles Git repository operations."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self._validate_git_repo()
    
    def _validate_git_repo(self) -> None:
        """Validate that the path contains a Git repository."""
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
        """Retrieve commit history from the repository."""
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
    """Main GitViz class that orchestrates graph generation."""
    
    def __init__(self):
        self.engines = {
            'graphviz': GraphvizEngine(),
            'pyvis': PyVisEngine()
        }
    
    def get_available_engines(self) -> List[str]:
        """Get list of available rendering engines."""
        return [name for name, engine in self.engines.items() if engine.available]
    
    def visualize(self, 
                  repo_path: str = ".",
                  engine: str = "auto",
                  output_path: str = "git_graph",
                  format_type: str = "svg",
                  max_commits: int = 100) -> None:
        """Generate visualization of Git repository."""
        
        # Auto-select engine if needed
        if engine == "auto":
            available = self.get_available_engines()
            if not available:
                raise RuntimeError("No rendering engines available. Install graphviz or pyvis.")
            
            # Prefer graphviz for static formats, pyvis for html
            if format_type.lower() == "html" and "pyvis" in available:
                engine = "pyvis"
            elif format_type.lower() in ["svg", "png", "pdf", "dot"] and "graphviz" in available:
                engine = "graphviz"
            else:
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
        if engine == "pyvis":
            selected_engine.render(commits, output_path)
        else:
            selected_engine.render(commits, output_path, format_type)