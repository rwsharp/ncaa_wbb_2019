#!/bin/bash

#this script is a wrapper for ncaaw_scores_fetch.py, which takes the line-by-line station ID codes from an input file and uses the python script to download html files and loop over a set of dates
#usage - ./ncaaw_scores_fetch.sh

#read line-over-line from input file
#start=2018-10-27
start=2019-03-15
start=$(date -d $start +%Y-%m-%d);

today=$(date +%Y-%m-%d);

while [[ "$start" != "$today" ]];
do
# echo $start
 start=$(date -d "$start + 1 day" +%Y-%m-%d)
 start_format=$(date -d $start +%m-%d-%Y) #invert the format to match NCAA's MM/DD/YYYY for the URL
 date=$(echo $start_format  | sed -e 's/\-/%2F/g' ) #convert - to %2F for URL encoding
 query=$(python ncaaw_scores_fetch.py $date $start_format) #set the query command
 echo $query #query the python
  echo ">>>> Fetching $date <<<<" #report to stdout
# echo "$start"
done
