# shiftSrt
Shift subtitles in SRT format.
# Requirements
Requires python3.
# Usage
Basic usage is to just shift the subtitles by a constant amount (the -s/--simple), e.g.
```batch
python3 srt.py -i input.srt -s 5.5 -o output.srt
```
shifts the time of each subtitle 5.5 seconds forward. This of course can be negative.

For a more complex case when a constant shift is not enough (e.g. the subtitles need both shifting by a constant amout and speeding up/slowing down), one can use the -c/--complex parameter. Let's say that at first the difference was small (~2s) and then grew larger as time went on up until more than 5 minutes at the end of the video. We can take two points in time (the further apart the better) and note down when they happened and when they should happen. This gives us 4 different points in time which we can feed into the script:
```batch
python3 srt.py -i input.srt -c 00:01:00.000 00:01:02.000 02:03:01.000 02:08:13.000 -o output.srt
```
In this case, a transformation will be applied to ensure that these 2 points are corrected exactly as specified, and the offsets of rest of them are interpolated using the linear relation.

# Limitations
This is quite a simple script based on regexes, so it doesn't have a complicated parsing mechanism. Because of that, it doesn't fix the srt if it has structure issues, nor it can detect them. It will happily run through every file without throwing an error. This may also be an advantage as it changes the bare minimum, and leaves the rest as is.

The script will also not work correctly with timestamps bigger than 24h (unlikely for most movies) as it uses date formatting under the hood (bigger timestamps will overflow and start a new day).