#!/usr/bin/python3

import sys
import argparse
import re
from datetime import timedelta, datetime

timeRegex = r"(\d\d):(\d\d):(\d\d),(\d+)"
fullRegex = rf"(\d)+\s*\n(?P<time1>{timeRegex})\s*-->\s*(?P<time2>{timeRegex})"


def seconds_from_string(s):
    hours, minutes, seconds, milliseconds = [int(x) for x in re.findall("\d+", s)]
    return timedelta(
        hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds
    ).total_seconds()


def transform_point(t, transformation):
    if not type(transformation) is list:
        # Simple shift
        return t + transformation

    x1, y1, x2, y2 = transformation
    # Interpolating via line connecting two points (x1,y1) and (x2,y2) -- assuming linearity
    return (y2 - y1) / (x2 - x1) * (t - x2) + y2


def transform_time(timestring, transformation):
    time = seconds_from_string(timestring)
    transformedTime = transform_point(time, transformation)
    transformedDate = datetime.utcfromtimestamp(transformedTime)
    # Won't work for timestamps of over 24 hours as we are using date to format them
    return transformedDate.strftime("%H:%M:%S,%f")[:-3]


def multiple_replace(input_string, translate_dict):
    return re.sub(timeRegex, lambda m: translate_dict[m.group()], input_string)


def replace_func(matchobj, transformation):
    time1 = matchobj.group("time1")
    time2 = matchobj.group("time2")
    transformedTime1 = transform_time(time1, transformation)
    transformedTime2 = transform_time(time2, transformation)
    repl = {time1: transformedTime1, time2: transformedTime2}
    return multiple_replace(matchobj.group(0), repl)


def main(input_file, transformation, output_file):
    # Read from stdin if "-" is specified
    if input_file == "-":
        data = sys.stdin.read()
    else:
        with open(input_file, "r") as file:
            data = file.read()

    transformed_data = re.sub(
        fullRegex, lambda s: replace_func(s, transformation), data
    )

    # Write to stdout if "-" is specified
    if output_file == "-":
        print(transformed_data)
    else:
        with open(output_file, "w") as file:
            file.write(transformed_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shift subtitles in SRT format.")
    parser.add_argument(
        "-i", "--input", type=str, default="-", help='Input SRT file or "-" for stdin'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-s",
        "--simple",
        type=float,
        help="Shift by a constant amount given in seconds",
    )
    group.add_argument(
        "-c",
        "--complex",
        nargs=4,
        help="""Transform using a linear mapping. Useful if the subtitles and video differ in fps. 
        Pick two points in the movie where the subtitles don\'t match (the further apart, the better)
        and note when they appear and when they should appear. 
        Give the list of times for syncing in the format "HH:MM:SS.mmm"
        in order wrong1 correct1 wrong2 correct2""",
    )
    parser.add_argument(
        "-o", "--output", type=str, default="-", help='Output file or "-" for stdout'
    )
    args = parser.parse_args()

    if args.complex:
        transformation = [seconds_from_string(t) for t in args.complex]
    else:
        transformation = args.simple

    main(args.input, transformation, args.output)
