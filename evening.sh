cd /home/rishika/Multilex-workflows
echo sharika1709$ | sudo -S python3 -m luigi --module evening Part1EveningPipeline --local-scheduler
echo sharika1709$ | sudo -S python3 -m luigi --module evening Part2EveningPipeline_new --local-scheduler
echo sharika1709$ | sudo -S python3 -m luigi --module evening Final_Report_Mailing_workflow --local-scheduler
