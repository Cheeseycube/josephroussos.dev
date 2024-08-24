# Errors and other Messages

## [Scraper](../Scraper-reference/)

When running the `Scraper`--such as in a daily `dbUpdater` run--all errors will be piped to `logs/error.log`.<br>
Most error messages will indicate the function they occurred in, as well as which statistic was affected.<br>
From there you can debug, but first it is recommended to rerun the code to see if the issue resolves.<br>
Web scraping is dependent on the website being scraped responding correctly, so every now and then a request will fall through the cracks.<br>
In the event that an error is persistent, the Scraper is designed to pull as much information as possible regardless.


## [dbUpdater](../dbUpdater-reference/)

`dbUpdater` logs messages to `logs/update.log`. Each time the main function in `dbUpdater` is called,
The time is recorded along with how many riders and races were scraped. In addition, the logged messages
indicate the "integrity" of the scraped data that was just pushed to the database. 
For more details see [dbUpdater.check_integrity()](../dbUpdater-reference/#dbUpdater.check_integrity).<br>

### example update log entry

```
2024-08-14 16:46:58.627886
Scraped 53078 races
Scraped 973 riders

race_results integrity:
stage_url: 100.00%, result: 90.67%, pcs_points: 100.00%, uci_points: 100.00%, rider_url: 100.00%, 

race_info integrity:
race_url: 100.00%, is_total_results_page: 100.00%, class: 100.00%, parcour_type: 100.00%, Date: 100.00%, Distance: 100.00%, ProfileScore: 68.17%, Vertical meters: 68.17%, Race ranking: 75.29%, Startlist quality score: 87.83%, 

rider_info integrity:
rider_url: 100.00%, name: 100.00%, nationality: 100.00%, current_team: 100.00%, birthdate: 100.00%, age: 100.00%, 

team history/info integrity:
team_url: 100.00%, season: 100.00%, team_name: 100.00%, class: 100.00%,
```



## [Front-End](../app-reference/)

All [Flask App](../app-reference/) run-time errors are outputted in the web-app itself with a full stack-trace,
along with the list of filters that was attempted to be queried.<br>
Errors typically occur from a faulty filter, so it is recommended to copy-paste the filters
from the error message and debug further separately.

## Common Errors

### error scraping races from: https://www.procyclingstats.com/rider/mieke-docx/2022 in getRiderRaceResults_async(): 'NoneType' object has no attribute 'text'

Errors such as this indicate the given url is empty or does not exist. In this specific example, 
further investigation revealed that the given url was temporarily down on the website, so it appeared empty. 
After some time, the url worked as normally again.<br> 
In other cases, the url may simply be invalid and will never work. The process of dealing with these
errors could certainly be improved, but for now they are infrequent enough that they do not pose a major
issue.

### Error Code 500

If you see this error on the webpage, an uncaught error within the app is the cause.
To pin down the exact problem, you will need to look at the generated stacktrace which should be
visible on the webpage itself.



