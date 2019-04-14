# course-2019-spr-proj
Team Members: Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara

Directory: ldisalvo_skeesara_vidyaap

## Project 1 - Justification
The below datasets can be combined to score the ideologies of voting districts within Massachusetts. The election data will help to identify which political party residents in that district typically vote for. The demographic census data can be used to determine predictors of voting patterns within each county and town. We plan to use the county shapes data to build our visualization of voting districts. We also plan to characterize each ballot question ideologically by comparing districts that voted in favor of the ballot question with those that voted for certain party candidates in the same year.  

## Datasets
### ballotQuestions
contains: data about each Massachusetts Ballot Question from 2000 to 2018

source: http://electionstats.state.ma.us/ballot_questions/search/year_from:2000/year_to:2018
```
{
    "_id" : "7322",
    "year" : 2018,
    "number" : "4",
    "description" : "SUMMARY Sections 3 to 7 of Chapter 44B of the General Laws
        of Massachusetts, also known as the Community Preservation Act (the 'Act'),
        establishes a dedicated funding source for the: acquisition, creation and
        preservation of open space; acquisition, preservation, rehabilitation and
        restoration of hi...",
    "type" : "Local Question",
    "location" : "Various cities/towns"
}
```

### ballotQuestionsResults
contains: data about voting results for each Massachusetts Ballot Question from 2000 to 2018

source: http://electionstats.state.ma.us/ballot_questions/download/7303/precincts_include:1/
```
{
    "Locality" : "Bourne",
    "Ward" : "-",
    "Pct" : "7",
    "Yes" : 375,
    "No" : 914,
    "Blanks" : 26,
    "Total Votes Cast" : 1315,
    "Question ID" : "7303"
}
```
### stateHouseElections
contains: data about each Massachusetts General State House Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/search/year_from:2000/year_to:2018/office_id:8/stage:General
```
{
    "_id" : "131672",
    "year" : 2018,
    "district" : "3rd Bristol",
    "candidates" :
    [ {
        "name" : "Shaunna L. O'Connell",
        "party" : "Republican",
        "isWinner" : true
    },
    {
        "name" : "Emily Jm Farrer",
        "party" : "Democratic",
        "isWinner" : false
    } ]
}
```
### stateHouseElectionsResults
contains: data about voting results for each Massachusetts General State House Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/download/131581/precincts_include:1/
```
{
    "City/Town" : "Barnstable",
    "Ward" : "-",
    "Pct" : "7",
    "Election ID" : "131582",
    "William L Crocker, Jr" : 1079,
    "Paul J Cusack" : 1059,
    "All Others" : 5,
    "Blanks" : 42,
    "Total Votes Cast" : 2185
}
```
### stateSenateElections
contains: data about each Massachusetts General State Senate Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/search/year_from:2000/year_to:2018/office_id:9/stage:General
```
{
    "_id" : "131666",
    "year" : 2018,
    "district" : "1st Middlesex",
    "candidates" :
    [ {
        "name" : "Edward J. Kennedy",
        "party" : "Democratic",
        "isWinner" : true
    }, {
        "name" : "John A. Macdonald",
        "party" : "Republican",
        "isWinner" : false
    } ] 
}
```
### stateSenateElectionsResults
contains: data about voting results for each Massachusetts General State Senate Election from 2000 to 2018

source: http://electionstats.state.ma.us/elections/download/131526/precincts_include:1/

```
{
    "City/Town" : "Egremont",
    "Ward" : "-",
    "Pct" : "1",
    "Election ID" : "131526",
    "Adam G Hinds" : 682,
    "All Others" : 0,
    "Blanks" : 111,
    "Total Votes Cast" : 793
}
```
### countyShapes
contains: geoJSON data about each Massachusetts county (taken from Google Fusion Table and uploaded to datamechanics.io)

source: http://datamechanics.io/data/massachusetts_counties.csv
```
{
    "_id" : "7322",
    "Name" : Barnstable,
    "Shape" : "<Polygon> ... ",
    "Geo_ID" : "25001",
}
```
### demographicDataCounty
contains: demographic data for Massachusetts by county from census.gov, to see full list of fields, go to:
 
source:https://www.census.gov/quickfacts/fact/table/ma/PST045217
```
{ "Barnstable County, Massachusetts":
   "Population estimates, July 1, 2017,  (V2017)": "213,444",
   "Population estimates base, April 1, 2010,  (V2017)": "215,868",
   "Population, percent change - April 1, 2010 (estimates base) to July 1, 2017,  (V2017)": "-1.1%",
   "Population, Census, April 1, 2010": "215,888",
   "Persons under 5 years, percent": "3.6%",
   "Persons under 18 years, percent": "15.1%",
   ..........................
}
```

### demographicDataTown
contains: demographic data for Massachusetts by city and town from census.gov and includes the data retreived from demographicDataCity, to see full list of fields, go to:

source: https://www.census.gov/quickfacts/fact/table/ma/PST045217)
```
{ "Winchester town, Middlesex County, Massachusetts":
  "Population estimates, July 1, 2017,  (V2017)": "23,339",
  "Population estimates base, April 1, 2010,  (V2017)": "23,797",
  "Population, percent change - April 1, 2010 (estimates base) to July 1, 2017,  (V2017)": "-1.9%",
  "Population, Census, April 1, 2010": "23,793",
  ..........................
}
```



## Transformations
### House District Ideology
Calculates a basic ideology score for each state house electoral district (160) by counting number of Democratic and Republican wins from 2000 to 2018

```
{
    "district" : "1st Barnstable",
    "percentDem" : 25,
    "percentRepub" : 75,
    "numDemWins" : 1,
    "numRepubWins" : 3,
    "numElections" : 4
}
```

### Senate District Ideology
Calculates a basic ideology score for each state senate electoral district (51) by counting number of Democratic and Republican wins from 2000 to 2018

```
{
    "district" : "1st Hampden and Hampshire",
    "percentDem" : 70, 
    "percentRepub" : 30, 
    "numDemWins" : 7,
    "numRepubWins" : 3, 
    "numElections" : 10 
}

```


### Weighted Senate Ideology
Calculates a weighted ideology score for each state senate electoral district by creating a ratio of type of vote to total vote in each year and finding the average

```
{
    "district" : "1st Hampden and Hampshire",
    "Democratic ratio" : .6,
    "Republican ratio" : .2,
    "Others ratio" : .1,
    "Blanks ratios" : .1,
    "Totals" : 1
}

```

### Weighted House Ideology
Calculates a weighted ideology score for each state house electoral district by creating a ratio of type of vote to total vote in each year and finding the average

```
{
    "district" : "1st Hampden and Hampshire",
    "Democratic ratio" : .6,
    "Republican ratio" : .2,
    "Others ratio" : .1,
    "Blanks ratios" : .1,
    "Totals" : 1
}

```

### Demographic Summary Metrics
Retrieves summary demographic data for all facts by county and town. Displays maximum and minimum values and corresponding towns for each fact.
```
{
    'Fact': 'Population estimates, July 1, 2017,  (V2017)',
    'Town_Min': 'Middleton town, Essex County, Massachusetts',
    'Town_Min_Val': '9,861',
    'Town_Max': 'Littleton town, Middlesex County, Massachusetts',
    'Town_Max_Value': '10,115',
    'County_Min': 'Worcester County, Massachusetts',
    'County_Min_Val': '826,116',
    'County_Max': 'Middlesex County, Massachusetts',
    'County_Max_Value': '1,602,947'}
}

```

### Voting District Towns
Maps voting district for state senate and house races to the list of towns in each district.
```
{
    "Type" : "Senate",
    "District" : "2nd Middlesex and Norfolk",
    "Towns" : [ "Ashland", "Framingham", "Franklin", "Holliston", "Hopkinton", "Medway", "Natick" ]
}

```

### demographicDataDistrictHouse
Retrieves average demographic data by house district for Massachusetts.
```
     {  "House District" : "10th Bristol" ,
        "Population estimates, July 1, 2017,  (V2017)" : 64728,
        "Population estimates base, April 1, 2010,  (V2017)" : 64552,
        "Population, Census, April 1, 2010" : 64552,
        ..........................
     }
```

### demographicDataDistrictSenate
Retrieves average demographic data by senate district for Massachusetts.
```
     {  "Senate District" : "2nd Middlesex and Norfolk" 
        "Population estimates, July 1, 2017,  (V2017)" : 29299.571428571428, 
        "Population estimates base, April 1, 2010,  (V2017)" : 27253, 
        "Population, Census, April 1, 2010" : 27253.714285714286, 
        "Persons under 5 years, percent" : 5.985714285714286,  }
        ..........................
     }
```

## Project 2 - Narrative
Problem: How do we use demographic factors to create a profile of local voting districts in Massachusetts that allows campaigns or political groups to determine which neighborhoods to canvass in?

To do this, we created demographic profiles of each voting district. We did this through several preliminary datasets. We created Voting District Towns which contains a mapping of all the towns within each voting district. The districts are also classified by state senate or house. We also created Demographic Data District House and Demographic Data District Senate datasets. These two scripts used the Voting District Towns dataset and the Demographic Data Town dataset to determine which towns made up a district and to average the numbers for a certain demographic statistic across all the towns to determine the statistic for the entire district. Once we did the above, we were able to proceed with our statistical analysis and constraint satisfaction problems. 

Constraint Satisfaction: We chose to solve the canvassing problem on a voting district level. Each voting district consists of neighborhoods for which we have demographic data. Given a budgeting constraint of X number of people that can be canvassed, we want to solve the problem of which neighborhoods within the district can be visited without going over the total district budget. We decided to use the z3-Solver library to solve this constraint problem for each district. Each neighborhood within a district is a z3 variable that can either be assigned a 0 (do not canvass) or a 1 (do canvass). The constraints use the population of each neighborhood to weight which ones to visit.

Statistical Analysis: In order to determine any strong predictors of voting ideology by district, we used the 2017 demographic data by district and the weighted ideology tables to create a table of correlation coefficients comparing demographic information and voting ideology.  The coefficients compare each piece of demographic data with "how Democratic" and  "how Republican" each district is.  The higher the coefficient, the more correlated that demographic information is with the likelihood of that district voting a certain way.

Note: When trial mode is enabled, running time is cut from 2 minutes and 30 seconds to 28 seconds. 

## Datasets
### Canvassing Budget Constraint
Determines which towns within a voting district can be canvassed within a specified canvassing budget (in number of people).
```
{
    "District" : "2nd Middlesex and Norfolk",
    "Type" : "Senate",
    "Budget (# of people)" : 100000,
    "Check" : "sat",
    "Excluded Towns" : [ ],
    "Model" : [
                [ "Ashland", 1 ],
                [ "Framingham", 1 ],
                [ "Franklin", 0 ],
                [ "Holliston", 0 ],
                [ "Hopkinton", 0 ],
                [ "Medway", 0 ],
                [ "Natick", 0 ],
                [ "popNatick", 36246 ],
                [ "popMedway", 13329 ],
                [ "popHopkinton", 18035 ],
                [ "popHolliston", 14753 ],
                [ "popFranklin", 32996 ],
                [ "popFramingham", 72032 ],
                [ "popAshland", 17706 ]
            ]
}
```

### Voting District Election Outcome Factors
```
     {"_id" : ObjectId("5ca6479e3f7b1b6f24598da3"),
      "Party" : "Democratic", 
      "Population estimates, July 1, 2017,  (V2017)" : NaN, 
      "Population estimates base, April 1, 2010,  (V2017)" : NaN, 
      "Population, Census, April 1, 2010" : 0.35763757741202973, 
      "Persons under 5 years, percent" : 0.16158614409129984, 
      "Persons under 18 years, percent" : -0.24276258580942858, 
      "Persons 65 years and over, percent" : -0.15693780305590088,
      ...
      }
```


## Additional Python Libraries
You may need to import the following libraries to access our datasets: bs4, pandas, requests, csv, io

They can be installed by running the requirements.txt file

```
pip3 install requirements.txt
```

If you get a 'SSL: CERTIFICATE_VERIFY_FAILED' error, you need to install certificates for your version of Python. In MacOS, navigate to Finder->Applications->Python3.7 and double click on 'InstallCertificates.command' and then on 'UpdateShellProfile.command'.