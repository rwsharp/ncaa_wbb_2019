#!/bin/bash

#this script is a wrapper for ncaaw_scores_fetch.py, which takes the line-by-line station ID codes from an input file and uses the python script to download html files and loop over a set of dates
#usage - ./ncaaw_scores_fetch.sh

#read line-over-line from input file
#start=2018-10-27
while read line;
do
# echo $start
 url="https://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=14320&org_id=$line&stats_player_seq=-100"
 query=$(curl -sL $url > data/team_schedules/$line.html) #set the query command
 echo $query #query the python
  echo ">>>> Fetching $line schedule <<<<" #report to stdout
# echo "$start"
done <teamlist_clean.txt
