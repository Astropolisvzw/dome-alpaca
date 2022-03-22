# dome-alpaca
Ascom Alpaca driver for custom dome hardware

## Install systemd

copy dome.service to /etc/systemd/system/dome.service




## Code structure

- APAshDomeServer.py => web server, responding to the alpaca REST requests
- dome.py => 1-to-1 python implementation of the alpaca REST interface, using helper classes to perform necessary tasks
- dome_calc.py => helper class to calculate dome positions, slew direction, ...


## Dome limits

There is a limited amount of cabling providing electricity to the top shutter.
Let's say this allows the dome to rotate 180 deg clockwise and 180 deg counterclockwise from *a certain starting point*.

This starting point will be our 'home' point, and will be in the South direction of the dome. (for now a marker will suffice, some switch would be better)
So the fixed limits are valid whenever starting from the home position.
We also have a limitcounter which keeps track of how much cable is still left in each direction.

## TODO

- while slewing, if a new request comes in *seamlessly* target the new azimuth
- clean up the limit handling
- unit test limit handling and dome rotation (separate them?)


