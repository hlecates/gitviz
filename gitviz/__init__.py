from .core import GitViz, GitRepository, GitCommit
from .cli import main

__version__ = "1.0.0"
__author__ = "Henry LeCates"
__description__ = "Visualize Git repository structure as a directed acyclic graph"

__all__ = ["GitViz", "GitRepository", "GitCommit", "main"]