#!/bin/bash

#this script is a wrapper for ncaaw_scores_fetch.py, which takes the line-by-line station ID codes from an input file and uses the python script to download html files and loop over a set of dates
#usage - ./ncaaw_scores_fetch.sh

#read line-over-line from input file

teamlist=$( cat teamlist.txt)
teamnum=$(echo "${teamlist}" | grep -oP "(?<=team\/).*?(?=\.0\/)")

echo "$teamnum"
echo "$teamnum" > teamlist_clean.txt
