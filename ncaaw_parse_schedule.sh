#!/bin/bash

#this script takes saved HTML files (from ncaaw_teamresults.sh and parses them into csvs)

files="data/team_schedules/*.html"
#files="data/team_schedules/5.html" #single team for testing purposes


for f in $files;
do

query=$(python ncaaw_parse_schedule.py $f)

echo "Parsing team schedule & stats for $f"
echo $query

done
