@echo off
python -m luigi --module evening Part1EveningPipeline --local-scheduler
python -m luigi --module evening Part2EveningPipeline_new --local-scheduler