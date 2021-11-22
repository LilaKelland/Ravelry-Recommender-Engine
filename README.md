# Ravelry-Recommender-Engine

### Goal:
Create a knitting pattern recommender engine for Ravelry

### Probelm:
Ravelry (https://www.ravelry.com/) has cornered the market in terms online knitting and fibre art content. Nearly any pattern can be found in it's database. The website is well laid out with a fabulous search menu - if you know what you're looking for, but if you don't you can get lost for hours trying to dig through the hundreds of thousands of obtions.  In the words of Steve Jobs "A lot of times, people don’t know what they want until you show it to them".

Knitting is a hobby known for destressing or relaxing.  There is a heavy time commitment, and monetary investment for the materials required for each project, and because of the shear number patterns, picking out the next project to start can be quite stressful.  

The problem this project aims to solve is making this selection process easier, by providing pattern recommendations to the user, when given a particular pattern the user enjoyed or likes. 

I'll be focussing on knitting for this project as it's a hobby I've been practicing for over three decades and more confortable assesing recomendation level of success in that area rather than the other fibre arts. 

### About Ravelry
Ravelry is a free indie-website started in 2007 which supports documenting fiber art projects. 

"The community [needed] an independent, not for-profit, decentralized, community owned database of patterns, yarns, and their connections to projects". - Cassidy :Ravelry co-founder  

Members share projects, ideas, collections of yarn and tools.  Because it's so community driven, nearly any knitting or crochet pattern can be found and reviewed. 
ref: https://en.wikipedia.org/wiki/Ravelry

#### Note this project is not asscoiated with Ravelry - all content is provided by Ravelry through public api

## Timeline:
* 18 - start!
* 19 - Data gathering cleaning
* 20 - Simple Model (popularity and rating)
* 21 - EDA, more feature engineering - stretch goal - first content based (but I'll be happy with ALL the data)

Monday
* 22 
* 22.5- more feature engineering - 2nd content based 
* 23
* 24 - collaborative filtering (Item Based) - start investigating RBM??
* 25
* 26 - hybrid content based and colaborative filtering 
* Sat
* 27 - final model complete ( would LOVE to be able to add in yarn filters for recommendation)
* 28 - repo clean up and buffer time (model tuning if have time)

Monday 
* 29 - work on presentation and deployment - or streamlet
* 30 
* 1 - dry run presentation
* 2 - presentation

## Progress Report:
Nov 22
- this morning looked at data and realized, it doesn't match the query (and has duplicates accross queries).  debugged and instead of "most recent", use sort by "best match" - seems to be okay now 
- updated api query to get actaully relevent data has been running for hours
- GOAL - would like to work on pipelining processing! And have ALL patterns data in db or csv 
- (stretch - have narrowed down to which patterns to pull projects, and then start calling for users for to populate similarity matrix
- learning about deep NN and RBM's for collabroative model (but worried about data at the moment)

Nov 21
- queried data (very slow process) - managed to get 120 mb (rating 5 clothing and rating 4 all) - turns out that's 
not actually the data I got (see Nov 22)
- wrote functions to clean and further parse out data, new features created - still need to figure out how
to pipeline these as some deal with more than one column at a time. 


Nov 20
- recieved email response from ravelry - very helpful! 
- still going on the data - MUCH more work than anticipated, and I haven't even gotten to the users yet! (Oh my, over 10million users...)
- learning about implicit collaborative recommenders - less than 1/5 of users rate patterns, and majority of people who do rate are only very positive (4-5), so going to take projects completed (like netflix veiws) instead. (as - if they've completed project, most times a win, if they hated it, would be "frogged")
- woot - have a MVP simple recommender (just weighted ratings score - most popular)... for 99 patterns 
- still need MANY more records (and users) - and WOW its needs a LOT of processing. cleaning - so many missing values/ mix-matches

Nov19
- MAJOR snag - turns out you need id's for patterns, going to be resource and time consuming to gather data
- sent email to team, hoping for response, but starting brainstorm alternative ideas, and moving forward
with this one - with fingers crossed
- working on accessing, cleaning data 

- 
Nov 18 
- picked a topic! And started documentation
- facing hurdle of actually starting, and worried about data size, what features to keep
- another hurdle is I'm not confident in recommender systems...yet! 
- api accessing and getting the data 

Next steps:
- yarn recommender 
- if you have yarn (say from stash, or reclaimed or thrifted), recommend patterns you may like to try to use that yarn up*** that would be my stretch goal! (yardage, weight) - excited about this part
- step further would be to take yarn in your stash (on ravelry) and use that as a recommender (woah - this could be interesting, take colourways that people use commonly together on projects - ML what works best, with what you have, and your preferences, and patterns and separate yardage requirements)


### Data 

gauge_per_inch - a measure of how loosely quickly a project can be knit up.  - can be related to yarn thickness or airyness of fabric

stages of life - why not user-user recommendations
eliminate high producers (often pumping out products for craft shows and sales)