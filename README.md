# adsbdb
poll dump1090 interface for aircraft.json and log results into mysql

I created this as a very quick and dirty way to record some data from a piaware
adsb reciever.  As a result many things could definitely be done better, and
some customization may be required for it to suite one's purposes.

A quick list of things that one may care to change:
 - root password on mysql in docker
 - where the mysql volume on the host is located
 - network path to piaware
 - sampling frequency (currently sampling once a second, probably too fast)

