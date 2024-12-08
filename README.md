# Lunar-Eclipse-Optimal-Viewing-Time-Calculator
A script to calculate the optimal viewing time for a lunar eclipse (down to the second) based on your location. Will also print some fun stats including an estimate of how much of the Sun will be covered.

## Installation
Clone the repo to a folder of your choice and install the ephem library (does the astronomy calculations) by typing "pip install ephem" in the command line.

## Usage
This script functions by going through every second of the day you choose and showing the exact time when the Sun and Moon are closest to each other. If there is an eclipse that day, they will be very close indeed. 

It will also print some stats about that point in time, including the angle of separation between them (in degrees), their sizes in the sky (in arcseconds), and an estimate of what percentage of the Sun is covered by the Moon.

The script requires the latitude and longitude of your observation point (you can get this from Google Maps), the time zone at the observation point (specified as a UTC offset), and the date the eclipse is supposed to happen (in the observation point's local time).

For example, let's say I'm sitting by the Eiffel Tower at 48.857921, 2.295497. I'm in Central European Time (UTC + 1) and I want to see an eclipse that will be occuring on December 25th, 2024. I would type:

    python eclipse_calculator.py --lat 48.857921 --long 2.295497 --utcoffset 1 --year 2024 --month 12 --day 25

If no UTC offset is specified, the script will use UTC time.

Lastly, the program uses Monte Carlo sampling to estimate what percentage of the Sun is covered by the Moon. This requires a large number of sampling points for an accurate estimate. By default it creates 10 million sampling points, but if you want to fine tune it, you can use the --nsamples argument with your chosen number of sampling points. To not perform the estimate, use --nsamples 0

## "But Wes, why would I use your lame script when there are so many cool web apps made by people much smarter than you?"
I wasn't able to find one that calculated the ideal observation time down to the second, which I wanted to know for the April 2024 eclipse because I am a huge nerd. This was also fun to make.
