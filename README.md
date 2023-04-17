# CNIT372-Group-Project
Contains SQL files for the solution of the group project questions

This repository is seperated into 4 files to aid with the construction on the Youtube Database
- init.sql
- convert.py
- import.sql
- questions.sql

## init.sql
init.sql is the first sql file that should be run, this file initializes all the tables used by the following files.

## convert.py
Because the exported YouTube data is in the formats JSON and HTML which aren't easily imported into a SQL based environment, there is a Python file that will parse the given data and generate files that can now be read into the database

## import.sql
This file takes the outputted files from the python script and inserts them into the database tables to allow for queries to be run on them

## questions.sql
This file contains all the queries that answers the questions we had about the YouTube data in order to solve our driving question on how individual users patterns were affected by the 2020 COVID Pandemic