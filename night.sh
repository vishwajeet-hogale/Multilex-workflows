@echo off
python3 -m luigi --module night NightPipeline --local-scheduler
