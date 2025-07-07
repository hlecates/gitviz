#!/usr/bin/env python3
"""
Tests for the rendering engines in GitViz
"""

import pytest
import os
import tempfile
import shutil
from gitviz.core import GitViz


class TestRenderingEngines:
    """Test class for rendering engines"""
    
    def setup_method(self):
        """Set up test environment"""
        self.gitviz = GitViz()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_available_engines(self):
        """Test that engines are properly detected"""
        available = self.gitviz.get_available_engines()
        assert isinstance(available, list)
        assert len(available) > 0, "At least one engine should be available"
        
        # ASCII engine should always be available (no dependencies)
        assert 'ascii' in available, "ASCII engine should always be available"
    
    def test_ascii_engine(self):
        """Test ASCII engine functionality"""
        if 'ascii' not in self.gitviz.get_available_engines():
            pytest.skip("ASCII engine not available")
        
        output_path = os.path.join(self.temp_dir, "test_ascii")
        
        # Test ASCII engine
        self.gitviz.visualize(
            repo_path=".",
            engine='ascii',
            output_path=output_path,
            format_type='txt',
            max_commits=5
        )
        
        # Check that output file was created
        expected_file = output_path + '.txt'
        assert os.path.exists(expected_file), f"Expected file {expected_file} was not created"
        
        # Check file content
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Git Repository Visualization (ASCII)" in content
            assert "Total commits:" in content
    
    def test_matplotlib_engine(self):
        """Test Matplotlib engine functionality"""
        if 'matplotlib' not in self.gitviz.get_available_engines():
            pytest.skip("Matplotlib engine not available")
        
        output_path = os.path.join(self.temp_dir, "test_matplotlib")
        
        # Test matplotlib engine
        self.gitviz.visualize(
            repo_path=".",
            engine='matplotlib',
            output_path=output_path,
            format_type='png',
            max_commits=5
        )
        
        # Check that output file was created
        expected_file = output_path + '.png'
        assert os.path.exists(expected_file), f"Expected file {expected_file} was not created"
        
        # Check file size (should be > 0)
        assert os.path.getsize(expected_file) > 0, "Generated PNG file is empty"
    
    def test_pyvis_engine(self):
        """Test PyVis engine functionality"""
        if 'pyvis' not in self.gitviz.get_available_engines():
            pytest.skip("PyVis engine not available")
        
        output_path = os.path.join(self.temp_dir, "test_pyvis")
        
        # Test pyvis engine
        self.gitviz.visualize(
            repo_path=".",
            engine='pyvis',
            output_path=output_path,
            format_type='html',
            max_commits=5
        )
        
        # Check that output file was created
        expected_file = output_path + '.html'
        assert os.path.exists(expected_file), f"Expected file {expected_file} was not created"
        
        # Check file content
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "<html>" in content.lower()
            assert "vis-network" in content.lower()
    
    def test_auto_engine_selection(self):
        """Test automatic engine selection based on format"""
        available = self.gitviz.get_available_engines()
        
        # Test auto-selection for different formats
        test_cases = [
            ('html', 'pyvis'),
            ('png', 'matplotlib'),
            ('txt', 'ascii'),
        ]
        
        for format_type, expected_engine in test_cases:
            if expected_engine in available:
                output_path = os.path.join(self.temp_dir, f"test_auto_{format_type}")
                
                # Test auto engine selection
                self.gitviz.visualize(
                    repo_path=".",
                    engine='auto',
                    output_path=output_path,
                    format_type=format_type,
                    max_commits=3
                )
                
                # Check that some output was generated
                output_files = [f for f in os.listdir(self.temp_dir) if f.startswith(f"test_auto_{format_type}")]
                assert len(output_files) > 0, f"No output files generated for {format_type}"
    
    def test_engine_validation(self):
        """Test that invalid engine/format combinations are rejected"""
        with pytest.raises(ValueError):
            self.gitviz.visualize(
                repo_path=".",
                engine='nonexistent_engine',
                output_path="test",
                format_type='html',
                max_commits=5
            )
    
    def test_format_validation(self):
        """Test that unsupported formats are rejected"""
        # Test with ASCII engine and unsupported format
        if 'ascii' in self.gitviz.get_available_engines():
            with pytest.raises(ValueError):
                self.gitviz.visualize(
                    repo_path=".",
                    engine='ascii',
                    output_path="test",
                    format_type='html',  # ASCII doesn't support HTML
                    max_commits=5
                )


def test_engine_listing():
    """Test that engine listing works correctly"""
    gitviz = GitViz()
    available = gitviz.get_available_engines()
    
    # Should have at least ASCII engine
    assert 'ascii' in available
    
    # Check that all available engines are properly initialized
    for engine_name in available:
        engine = gitviz.engines[engine_name]
        assert engine.available, f"Engine {engine_name} should be available"
        assert hasattr(engine, 'supports_format'), f"Engine {engine_name} should have supports_format method"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"]) 