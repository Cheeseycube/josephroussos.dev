# Overview

The PCS Filter Tool is a software package that performs three primary tasks:

1. Web-scraping statistics about professional women cyclers from [www.procyclingstats.com](https://www.procyclingstats.com)
2. Building and maintaining a SQL database containing cleaned web-scraped data.
3. Providing a front-end for users to query the database with a number of filters

## The Scraper

Web-scraping is handled by several classes located in [Scraper.py](../Scraper-reference).<br>
Within [Scraper.py](../Scraper-reference) there are two general techniques for scraping.<br>

### In-House Scraping

Methods such as [RaceScraper.getRaceInfo()](../Scraper-reference/#Scraper.RaceScraper.getRaceInfo) utilize our own scraping algorithm
that relies on a python package called [selectolax](https://pypi.org/project/selectolax/) to handle html parsing.<br>
Any errors that occur during scraping will be outputted to `logs/error.log`.

### Scraping via [Procyclingstats](https://pypi.org/project/procyclingstats/)

Methods such as [RiderScraper.getRiderInfo()](../Scraper-reference/#Scraper.RiderScraper.getRiderInfo) utilize a python package
called [procyclingstats](https://pypi.org/project/procyclingstats/) to handle web scraping.
This package is open-source and made to scrape this specific website.
Internally, [selectolax](https://pypi.org/project/selectolax/) is still used, so a familiarity with this package
will prove helpful for debugging.<br>
<br>
**NOTE**: A static copy of the [procyclingstats](https://pypi.org/project/procyclingstats/) package is used as opposed to
the latest version from pypi. The CBA team made this concession because unfortunately the latest version of this package
tends to have bugs and missing features that aren't addressed in a timely manner. To that end, we have customized 
the package with a few new features and bug fixes.<br><br>
**A full list of changes to the original package are listed below**<br>
* `procyclingstats/rider_scraper.birthdate()`: CBA team added a special case for those with only year<br>
* `procyclingstats/rider_scraper.age()`: CBA team added this new method<br>
* `procyclingstats/table_parser._filter_a_elements()`: CBA team added a conditional for national races<br>

## The Database

### [dbBuilder](../dbBuilder-reference)

This is the heart of the database where there exist methods to build and update
each table. Duplicates are automatically ignored, and if a table doesn't exist yet it will be
created.

### [dbUpdater](../dbUpdater-reference/)

This is a simple script that can be scheduled to run as often as you want--we recommend at least
once a day--and will keep the [database](../database-schema/) up-to-date.
By default, `dbUpdater` sends log data to `logs/update.log`, but that could easily be piped somewhere else.

### [dataCleaner](../dataCleaner-reference/)

Finally, it is important to note that scraped data is first sent through various cleaning methods located in `dataCleaner.py`
before being sent to `dbBuilder`.

## The Front-End

### [Flask App](../app-reference/)

The front-end is powered by a simple python Flask app located in `app.py`. The app renders a home page that allows a user
to select various filters and submit them through a form.

### [queryBuilder](../queryBuilder-reference/)

`queryBuilder.py` takes in a list of filters provided by the user, and constructs/executes a corresponding sql query.
The returned filtered list of riders is then displayed to the user by the Flask App.
