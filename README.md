# Predoc Course as ICS

This script fetches the webpage from [https://www.embl.de/predoccourse/2018/schedule/index.html]
and provides the content as a ICS file.

This is useful for anyone wanting the HTML table calendar to be easily accessible 
from their phone or other devices.

## Usage

Have python3 and icalendar  installed (pip3 install icalendar) and run:

```
python3 main.py output.ics
```
This requires a working network connection as it will fetch the HTML content from the page mentioned.



## Issues

As this is a parser for a webpage written by humans, errors might occur as not everything 
is super machine readable.

E.g. some dates are "Friday afternoon" which is hard to interpret for a script.

ATM everything works (as far as I checked) but if issues arrise please notify me or
fix them yourself.


