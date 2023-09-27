import sys, select
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse
from datetime import datetime

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# N           = Month
# !           = Found a better appointment!
# X! & X!!    = Request error
# XX! & XX!!  = JSON Decode Errors


# create argument parser
parser = argparse.ArgumentParser(description='Heres what it does')

parser.add_argument('-f', '--first-name', type=str, help='Your first name. (used in booking request)', required=True)
parser.add_argument('-l', '--last-name', type=str, help='Your last name. (used in booking request)', required=True)
parser.add_argument('-z', '--zip', type=str,help="Five digit zip in TX you prefer the appointment be close to. (used in lookup request)", required=True)
parser.add_argument("-s", "--ssn", type=str, help="Last four digits of your SSN. (used in booking request)", required=True)
parser.add_argument("-e", "--email", type=str, help="You email address. (used in booking request)", required=True)
parser.add_argument("-b", "--dob", type=str, help="Date of birth in 'DD/MM/YYYY format.'", required=True)
parser.add_argument("-q", default=False, action="store_true", help="Quiet mode #1, silences boop on handled errors...")
parser.add_argument("-qq", default=False, action="store_true", help="Quiet mode #2, silences ALL boops including new appointment boop!")

# TODO actually implement current best booked input! (validate expected input and place in file...)
parser.add_argument("-c", "--current", type=str, help="Current best booked timeslot in YYYY-MM-DDTHH:MM:SS format where HH is in military time. EXAMPLE: 2023-06-20T15:30:00 is June 20th at 3:30pm. (optional, if none exist I'm yoinking first best! , also only needed if no current_best exists tracking the best date already!)", required=False)


# parse arguments
args = parser.parse_args()

print("---------------------------------------------------------------------")
print("            You are now waiting in the digital DMV line.             ")
print("               ( Press enter to step out of line... )                ")
print("---------------------------------------------------------------------")

curBestFile = open("./current_best", "r")
curBest = curBestFile.read()
curBestFile.close()

firstName = args.first_name
lastName = args.last_name
zip = args.zip
ssn = args.ssn
email = args.email
dob = args.dob
current = args.current

while True:
    # check if user is trying to exit condition
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = input()
        break

    headers = {"Host": "publicapi.txdpsscheduler.com", "Origin": "https://www.tx.com", "Cache-Control": "no-cache, no-store"}
    
    # TODO add arg to set typeId for other types of appointments!
    # # TODO TODO THIS 71  \/  IS WHAT YOU MUST REPLACE TO SCHEDULE OTHER APPOINTMENT TYPES MUST PROXY WHILE SUBMITTING APPOINTMENT FORM TO FIND (form itself not easily decipherable)
    searchData = {"TypeId":71,"ZipCode":args.zip,"CityName":"","PreferredDay":0}
    
    okay = True
    try:
        searchRequest = requests.post("https://publicapi.txdpsscheduler.com/api/AvailableLocation",
            headers=headers,
            json=searchData,
            timeout=30)
    except:
        okay = False

    if searchRequest.ok and searchRequest.json() is not None and okay:
        curBestTime = datetime.strptime(curBest, "%Y-%m-%dT%H:%M:%S")
        print(str(curBestTime.month), end=" ", flush="True")
        try:
            newBest = searchRequest.json()[0]["Availability"]["LocationAvailabilityDates"][0]["AvailableTimeSlots"][0]["StartDateTime"]
            durationOfBest = searchRequest.json()[0]["Availability"]["LocationAvailabilityDates"][0]["AvailableTimeSlots"][0]["Duration"]
            # Still need to get the site id from here!!

            newBestTime = datetime.strptime(newBest, "%Y-%m-%dT%H:%M:%S")
            newSiteId = searchRequest.json()[0]["Id"]
        except:
            print("XX!", end=" ", flush="True")
            if not args.q and not args.qq: print('\a', end="", flush="True")
            time.sleep(5)
            continue

        # if the current best is greater.... in time. as in later!
        if curBestTime > newBestTime and durationOfBest >= 30:
            print("!", end=" ", flush="True")
            if not args.qq: print('\a', end="", flush="True")
            # attempt to book appointment
            # TODO appointmentTypeId for different types of appointments??
            bookData = {"CardNumber":"","FirstName":firstName,"LastName":lastName,"DateOfBirth":dob,"Last4Ssn":ssn,"Email":email,"CellPhone":"","HomePhone":"","ServiceTypeId":71,"BookingDateTime":newBest,"BookingDuration":30,"SpanishLanguage":"N","SiteId":newSiteId,"SendSms":False,"AdaRequired":False}
            
            # redundancy because paranoid c:
            okay = True
            try:
                bookRequest = requests.post("https://publicapi.txdpsscheduler.com/api/NewBooking",
                    headers=headers,
                    json=bookData,
                    timeout=30)
            except:
                okay = False

            if bookRequest.ok and bookRequest.json() is not None and okay:
                try:
                    if bookRequest.json()["ErrorMessage"] is None:
                        # if successful, update best day
                        curBestFile = open("./current_best", "w")
                        curBestFile.write(newBest)
                        curBestFile.close()
                        print()
                        print("A new appointment has been booked, on " + newBest + "! :D")
                        print()
                    else:
                        print()
                        print(bookRequest.json()["ErrorMessage"])
                        print("Timeslot attempted to book:   " + newBest)
                        print("Current Timeslot:             " + curBest)
                        print()
                except:
                    print("XX!!", end=" ", flush="True")
                    if not args.q and not args.qq: print('\a', end="", flush="True")
                    time.sleep(5)
                    continue
            else:
                print("X!!", end=" ", flush="True")
                if not args.q and not args.qq: print('\a', end="", flush="True")
                time.sleep(5)
    else:
        print("X!", end=" ", flush="True")
        if not args.q and not args.qq: print('\a', end="", flush="True")
        time.sleep(5)
        
