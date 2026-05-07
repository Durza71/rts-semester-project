#!/usr/bin/env fish

clear 

rm -r *.csv
rm -r *.png

python3 main.py 
python3 analysis.py --compare edf_overruns.csv llf_overruns.csv rm_overruns.csv 
chafa comparison_average_slack.png