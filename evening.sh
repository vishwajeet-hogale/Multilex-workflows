cd /home/rishika/Multilex-workflows
python3 -m luigi --module evening Part1EveningPipeline --local-scheduler
python3 -m luigi --module evening Part2EveningPipeline_new --local-scheduler
python3 -m luigi --module evening Final_Report_Mailing_workflow --local-scheduler
