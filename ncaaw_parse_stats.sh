#!/bin/bash

#this script takes saved HTML files (from ncaaw_teamresults.sh and parses them into csvs)

files="data/team_stats/*.html"
#files="data/team_stats/51.html" #single team for testing purposes


for f in $files;
do

query=$(python ncaaw_parse_stats.py $f)

echo "Parsing player stats for $f"
echo $query

done
