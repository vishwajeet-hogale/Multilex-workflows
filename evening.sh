cd /home/ubuntu/Multilex-workflows
/home/ubuntu/anaconda3/bin/python3 -m luigi --module evening Part1EveningPipeline --local-scheduler
/home/ubuntu/anaconda3/bin/python3 -m luigi --module evening Part2EveningPipeline_new --local-scheduler
/home/ubuntu/anaconda3/bin/python3 -m luigi --module evening Final_Report_Mailing_workflow --local-scheduler
