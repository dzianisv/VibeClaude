#!/usr/bin/env python3
"""
test_audio.py
=============

Test audio functionality for VibeClaude - includes actual sound playback.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vibeclaude.main import play_jingle

def test_actual_sound():
    """Test that actually plays sound - run manually to hear it."""
    print("Playing test sound...")
    play_jingle()
    print("Sound should have played!")

if __name__ == '__main__':
    test_actual_sound()