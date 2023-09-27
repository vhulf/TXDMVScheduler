The Texas DMV sucks... If only there was a script to constantly monitor appointment openings and cancellations to hit that 5 a day pool that opens at 8am or to snag the oddball cancellation... :hmmm:

## Usage
```
python3 dmvScheduler.py -h
```
NOTE:: --current is unimplemented atm! For now a current best _must_ be created by hand and it's date added to the 'current_best' file, an example is in this repo for reference! ALSO , a very OLD time could be used to force update without needing to make an appointment by hand!

NOTE #2:: This was created with a specific type of appointment in mind , new or renew license plate (code 71 for their API) is _hard coded_ in this script, there is a comment on the related line if you need a different type of appointment!

## Output Key
```
# N           = Month of earliest availability
# !           = Found a better appointment!
# X! & X!!    = Request errors...
# XX! & XX!!  = JSON Decode Errors...
```
