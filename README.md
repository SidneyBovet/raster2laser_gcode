# IMPORTANT! - Tweaked to work with Inkscape 1.x

- Original work by 305engineering

## Starting to change original logic
- No more option to pick background color (always white, which translates to a simple move - laser off)
- New file names
- New svg -> png conversion
- Remove Preview Only
- Feed rate in mm/min (was mm/s)
- Add feed rate to travel moves
- Add power constant laser power (Sx) #TODO: variable power for grayscale *not working
- Consolidate Feed (=speed Fx) and Speed(=power Sx) to gcode header
- Moved LASER ON / LASER OFF to begin/end file only
- Added option to set laser max power GCode (usually 255)
- Make selectable to turn the LASER ON/OFF only at the beginning and end of the file, or turn it in the middle of the raster.
- Add option to enter file extension


----------- ORIGINAL TEXT -----------------


# Raster 2 Laser GCode generator

## Descriptions
- Raster 2 Laser GCode generator is an extension to generate Gcode for a laser cutter/engraver (or pen plotter), it can generate various type of outputs from a simple B&W (on/off) to a more detailed Grayscale (pwm)


## Installing:

Simply copy all the files in the folder "Extensions" of Inkscape

>Windows ) "C:\<...>\Inkscape\share\extensions"

>Linux ) "/usr/share/inkscape/extensions"

>Mac ) "/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions"


for unix (& mac maybe) change the permission on the file:

>>chmod 755 for all the *.py files

>>chmod 644 for all the *.inx files



## Usage of "Raster 2 Laser GCode generator":

[Required file: png.py / raster2laser_gcode.inx / raster2laser_gcode.py]

- Step 1) Resize the inkscape document to match the dimension of your working area on the laser cutter/engraver (Shift+Ctrl+D)

- Step 2) Draw or import the image

- Step 3) To run the extension go to: Extension > 305 Engineering > Raster 2 Laser GCode generator

- Step 4) Play!




## Note
I have created all the file except for png.py , see that file for details on the license
