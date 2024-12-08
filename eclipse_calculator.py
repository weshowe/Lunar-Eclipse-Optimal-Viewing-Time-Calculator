import math
import ephem
from datetime import datetime, timedelta
import random
import argparse

# UTC offset to timezone mapping.
utc_offsets_to_timezones = {
    -12: "UTC-12:00 Baker/Howland Island",
    -11: "UTC-11:00 Samoa Time Zone",
    -10: "UTC-10:00 Hawaii-Aleutian Standard Time",
    -9: "UTC-09:00 Alaska Standard Time",
    -8: "UTC-08:00 Pacific Standard Time / Alaska Daylight Time",
    -7: "UTC-07:00 Mountain Standard Time / Pacific Daylight Time",
    -6: "UTC-06:00 Central Standard Time / Mountain Daylight Time",
    -5: "UTC-05:00 Eastern Standard Time / Central Daylight Time",
    -4: "UTC-04:00 Atlantic Standard Time / Eastern Daylight Time",
    -3: "UTC-03:00 Argentina Time / Atlantic Daylight Time",
    -2: "UTC-02:00 South Georgia and the South Sandwich Islands",
    -1: "UTC-01:00 Azores Time",
    0: "UTC or GMT",
    1: "UTC+01:00 Central European Time / Western European Summer Time",
    2: "UTC+02:00 Eastern European Time / Central European Summer Time",
    3: "UTC+03:00 Moscow Time /  Eastern European Summer Time",
    4: "UTC+04:00 Gulf Standard Time / Moscow Daylight Time",
    5: "UTC+05:00 Pakistan Standard Time",
    6: "UTC+06:00 Bangladesh Standard Time",
    7: "UTC+07:00 Indochina Time",
    8: "UTC+08:00 China Standard Time",
    9: "UTC+09:00 Japan Standard Time",
    10: "UTC+10:00 Australian Eastern Standard Time",
    11: "UTC+11:00 Solomon Islands Time",
    12: "UTC+12:00 Fiji Time"
}

# Monte Carlo sampling functions for estimating percentage of Sun obscured by Moon.

# Given body origin, given point, and body radius, determine if the point falls within the body
def iswithin(inPoint, targetPoint, radius):
    vecDist = math.sqrt((targetPoint[1] - inPoint[1])**2 + (targetPoint[0] - inPoint[0])**2)

    if vecDist <= radius:
        return True
    
    else:
        return False

# Take a random point from within the grid
def samplePoint(gridSize):
    cur_x = random.randint(-gridSize, gridSize)
    cur_y = random.randint(-gridSize, gridSize)
    return [cur_x, cur_y]

# Monte Carlo sampling to determine percentage of sun is obscured by moon
# Sample n times, resultant is  1 - number of points in sun and not in moon / number of points in sun      
def montecarlo(gridSize, sep, moon_radius, sun_radius, n):

    moon_origin = [0,0]
    sun_origin = [0, sep]

    inBoth = 0
    inSunOnly = 0

    for i in range(0, n):
        newPoint = samplePoint(gridSize)

        inMoon = iswithin(newPoint, moon_origin, moon_radius)
        inSun = iswithin(newPoint, sun_origin, sun_radius)

        # If our random sample fell outside both bodies, ignore.
        if (inMoon == False) and (inSun == False):
            continue

        elif (inMoon == True) and (inSun == True):
                inBoth += 1

        elif (inMoon == False) and (inSun == True):
                inSunOnly += 1
    
    return 1 - (inSunOnly / (inBoth + inSunOnly))

# Calculates optimal viewing time, using minimum angle of separation between sun and moon
# params:
#    lat (float): latitude
#    long (float): longitude
#    utc_offset (int): your local time, as a UTC offset. ie, for Pacific Standard Time (UTC - 8), it is -8
#    year (int): the year
#    month (int): month as integer
#    day (int): day of the month as integer
#    monteCarloSamples (int): Number of sampling points for estimating percentage of Sun obscured. Should be relatively high (default is 10,000,000, lower it if your computer is slow).
def calculate_optimal_view(lat, long, utc_offset, year, month, day, monteCarloSamples = 10000000):
    moon = ephem.Moon()
    sun = ephem.Sun()
    here = ephem.Observer()
    here.lat = str(lat)
    here.lon = str(long)

    tim_start = datetime(year=year, month = month, day = day, hour = 0, minute = 0, second = 0)
    tim_end = datetime(year=year, month = month, day = day, hour = 23, minute = 59, second = 59)

    def computeBodyDist(inTime):
        
        # Since ephem uses UTC time, we add the offset here.
        if utc_offset >= 0:
            here.date = str(inTime - timedelta(hours=abs(utc_offset)))
        else:
            here.date = str(inTime + timedelta(hours=abs(utc_offset)))

        moon.compute(here)
        sun.compute(here)
        dist = ephem.separation(sun, moon)
        return dist
    
    bestDist = 1000000000000000000
    bestTime = ""

    while(str(tim_start) != str(tim_end)):
        curDist = computeBodyDist(tim_start)

        if curDist < bestDist:
           bestDist = curDist
           bestTime = tim_start

        tim_start += timedelta(seconds=1)

    timezonePretty = utc_offsets_to_timezones[utc_offset]
    print(f"Best time to see eclipse: {bestTime} ({timezonePretty})")

    # 
    distDegrees = math.degrees(bestDist)
    distString = '%.12f' % float(distDegrees)
    print(f"Minimum angle of separation between sun and moon centroids (degrees): {distString}")

    # recompute sun and moon position at best observation time for more stats
    there = ephem.Observer()
    there.lat = str(lat)
    there.lon = str(long)

    # Since ephem uses UTC time, we add the offset here.
    if utc_offset >= 0:
        there.date = str(bestTime - timedelta(hours=abs(utc_offset)))
    else:
        there.date = str(bestTime + timedelta(hours=abs(utc_offset)))

    moon.compute(there)
    sun.compute(there)
    print(f"Apparent size of Sun (arcseconds): {sun.size}")
    print(f"Apparent size of Moon (arcseconds): {moon.size}")

    if monteCarloSamples > 0:
        print("\nPerforming Monte Carlo sampling to determine the percentage of the Sun that will be covered by the Moon at the best viewing time...\n")

        # standardize angle to match unit of sun and moon size.
        distArcseconds = distDegrees * 3600

        # need radii for distance calculations
        sun_radius = sun.size/2
        moon_radius = moon.size/2 

        # Conservative grid - diagonal between sun edge and moon edge, add both radii
        gridSize = int((sun_radius + distArcseconds + moon_radius) + sun_radius + moon_radius)

        percentage = montecarlo(gridSize, distArcseconds, moon_radius, sun_radius, monteCarloSamples)

        print(f"Estimated percentage of Sun obscured by Moon: {percentage * 100}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lat", type = float, help="latitude of your observation location", action="store", required = True)
    parser.add_argument("-k", "--long", help="longitude of your observation location", action="store", required = True)
    parser.add_argument("-t", "--utcoffset", type=int, help="The UTC offset of your timezone. ie: for Pacific Standard Time (UTC - 8 hours), this is -4. If not specified, will use UTC Time", action = "store")
    parser.add_argument("-d", "--day", type=int, help="the day of the month that the eclipse will happen.", action = "store" , required=True)
    parser.add_argument("-m", "--month", type=int, help="the month that the eclipse will happen (1-12).", action = "store" , required=True)
    parser.add_argument("-y", "--year", type=int, help="the year that the eclipse will happen.", action = "store" , required=True)
    parser.add_argument("-n", "--nsamples", type=int, help="The number of Monte Carlo sampling points to use when calculating how much of the Sun is obscured by the Moon. Default is 10 million.", action = "store")
    args = parser.parse_args()

    # use UTC time if no offset specified.
    if args.utcoffset is None:
        args.utcoffset = 0
    
    if args.nsamples is None:
        calculate_optimal_view(args.lat, args.long, args.utcoffset, args.year, args.month, args.day)

    else:
        calculate_optimal_view(args.lat, args.long, args.utcoffset, args.year, args.month, args.day, args.nsamples)

    print("\nProgram completed.\n")

if __name__ == "__main__":
    main()


