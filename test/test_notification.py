#!/usr/bin/env python3
"""
test_notification.py
====================

Test notification functionality for VibeClaude.
"""

import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vibeclaude.main import notify, run_hook, last_assistant_line


class TestNotification(unittest.TestCase):
    """Test notification functionality."""

    def test_notify_macos(self):
        """Test macOS notification using osascript."""
        with patch('platform.system', return_value='Darwin'):
            with patch('subprocess.run') as mock_run:
                notify("Test message")
                
                mock_run.assert_called_once_with([
                    "osascript", "-e", 
                    'display notification "Test message" with title "Claude ✔ Finished"'
                ], check=False)

    def test_notify_empty_message(self):
        """Test notification with empty message."""
        with patch('platform.system', return_value='Darwin'):
            with patch('subprocess.run') as mock_run:
                notify("")
                
                mock_run.assert_called_once_with([
                    "osascript", "-e", 
                    'display notification "Task complete." with title "Claude ✔ Finished"'
                ], check=False)

    def test_notify_none_message(self):
        """Test notification with None message."""
        with patch('platform.system', return_value='Darwin'):
            with patch('subprocess.run') as mock_run:
                notify(None)
                
                mock_run.assert_called_once_with([
                    "osascript", "-e", 
                    'display notification "Task complete." with title "Claude ✔ Finished"'
                ], check=False)

    def test_last_assistant_line(self):
        """Test extracting last assistant message from transcript."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            # Write some test transcript data
            f.write('{"role": "user", "text": "Hello"}\n')
            f.write('{"role": "assistant", "text": "Hi there!"}\n')
            f.write('{"role": "user", "text": "How are you?"}\n')
            f.write('{"role": "assistant", "text": "I am doing well, thank you!"}\n')
            f.flush()
            
            try:
                result = last_assistant_line(pathlib.Path(f.name))
                self.assertEqual(result, "I am doing well, thank you!")
            finally:
                os.unlink(f.name)

    def test_last_assistant_line_empty_file(self):
        """Test with empty transcript file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.flush()
            
            try:
                result = last_assistant_line(pathlib.Path(f.name))
                self.assertEqual(result, "")
            finally:
                os.unlink(f.name)

    def test_run_hook_with_transcript(self):
        """Test complete hook execution with transcript."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"role": "assistant", "text": "Task completed successfully!"}\n')
            f.flush()
            
            try:
                with patch('platform.system', return_value='Darwin'):
                    with patch('subprocess.run') as mock_run:
                        with patch('vibeclaude.main.play_jingle') as mock_jingle:
                            payload = {"transcript_path": f.name}
                            
                            # Capture stdout
                            from io import StringIO
                            captured_output = StringIO()
                            with patch('sys.stdout', captured_output):
                                run_hook(payload)
                            
                            # Check notification was called
                            mock_run.assert_called_once_with([
                                "osascript", "-e", 
                                'display notification "Task completed successfully!" with title "Claude ✔ Finished"'
                            ], check=False)
                            
                            # Check jingle was called
                            mock_jingle.assert_called_once()
                            
                            # Check output was printed
                            output = captured_output.getvalue().strip()
                            self.assertEqual(output, "Task completed successfully!")
            finally:
                os.unlink(f.name)

    def test_run_hook_no_transcript(self):
        """Test hook execution without transcript."""
        with patch('platform.system', return_value='Darwin'):
            with patch('subprocess.run') as mock_run:
                with patch('vibeclaude.main.play_jingle') as mock_jingle:
                    payload = {}
                    
                    run_hook(payload)
                    
                    # Check notification was called with default message
                    mock_run.assert_called_once_with([
                        "osascript", "-e", 
                        'display notification "Task complete." with title "Claude ✔ Finished"'
                    ], check=False)
                    
                    # Check jingle was called
                    mock_jingle.assert_called_once()

    def test_integration_end_to_end(self):
        """Test full integration from CLI input to notification."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"role": "assistant", "text": "Integration test message"}\n')
            f.flush()
            
            try:
                # Test payload like what Claude-Code would send
                test_payload = {
                    "transcript_path": f.name,
                    "event": "Stop"
                }
                
                with patch('platform.system', return_value='Darwin'):
                    with patch('subprocess.run') as mock_run:
                        with patch('vibeclaude.main.play_jingle'):
                            from vibeclaude.main import run_hook
                            run_hook(test_payload)
                            
                            # Verify the notification was triggered with correct message
                            mock_run.assert_called_once_with([
                                "osascript", "-e", 
                                'display notification "Integration test message" with title "Claude ✔ Finished"'
                            ], check=False)
            finally:
                os.unlink(f.name)


if __name__ == '__main__':
    unittest.main()