#!/bin/bash
cd /home/kavia/workspace/code-generation/music-video-preview-player-22936-22945/music_player_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

