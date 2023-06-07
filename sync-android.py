#!/usr/bin/env python3
"""
Script to sync directory trees from/to android device

Suggested usage:
    $ sync-android.py /Users/chris/Dropbox/Chris/media/mp3 /Music/mp3 [--run] [--skip-wav]

Prerequisites:
1. install adb (see https://developer.android.com/studio/command-line/adb#Enabling)
2. on android: enable "Use developer options" in settings
    - On the device, go to Settings > About <device>.
    - Tap the Build number seven times to make Settings > Developer options available.
3. on android: enable "usb debugging" in "Developer options"
"""
import argparse
import collections
import os
import pprint
import sys
import subprocess


ADB = os.path.expanduser("~/coding/android/platform-tools/adb")
CMD = "push"
# constants
KB = 1024
MB = KB * 1024


FileInfo = collections.namedtuple("FileInfo", ["path", "size"])


def main():
    src_dir, dst_dir = args.src, args.dest
    dst_dir = dst_dir.lstrip("/")
    dst_dir = os.path.join("/sdcard", dst_dir)
    walked = []
    total = 0
    for basepath, _, filenames in os.walk(src_dir):
        for filename in filenames:
            rel_dir = basepath[len(src_dir) :]
            rel_dir = rel_dir.lstrip("/")
            rel_path = os.path.join(rel_dir, filename)
            size = os.path.getsize(os.path.join(src_dir, rel_path))
            walked.append(FileInfo(rel_path, size))
            total += size
    so_far = 0
    for rel_path, size in walked:
        if args.skip_wav and rel_path.lower().endswith(".wav"):
            continue
        dest_path = os.path.join(dst_dir, rel_path)
        # usage example of adb push:
        #  adb push --sync "Winter.mp3" "/sdcard/Music/mp3/Winter.mp3"
        command = [ADB, "push", "--sync", os.path.join(src_dir, rel_path), dest_path]
        if args.verbose:
            pprint.pprint(command)
        if args.run:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.returncode:
                print(result.stdout.decode().strip())
                print(result.stderr.decode().strip())
                return 1
            if args.verbose:
                print(result.stdout.decode().strip())
                print(result.stderr.decode().strip())
        else:
            if args.verbose:
                print("--- not run without run=True")
        print_bar(so_far, total)
        so_far += size
    return 0


def print_bar(so_far: int, total: int):
    complete = 40
    progress = int(so_far / total * complete)
    bar = (progress * "#").ljust(complete, "-")
    percent = so_far / total * 100
    percent = f"{percent:.1f}"
    so_far_mb = f"{so_far / MB:.1f}"
    total_mb = f"{total / MB:.1f}"
    if args.verbose:
        end = "\n"
    else:
        end = "\r"
    print(f"[{bar}] {percent}% ({so_far_mb} MB / {total_mb} MB)", end=end)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sync files onto android",
    )
    parser.add_argument("src", help="source directory")
    parser.add_argument("dest", help="destination directory (will prepend /sdcard)")
    parser.add_argument(
        "--run", action="store_true", help="run the commands", default=False
    )
    parser.add_argument(
        "--skip-wav", action="store_true", help="skip wav files", default=False
    )
    parser.add_argument(
        "--verbose", action="store_true", help="run in verbose mode", default=False
    )
    return parser.parse_args()


if __name__ == "__main__":
    src = "/Users/chris/Dropbox/Chris/media/mp3"
    dest = "/Music/mp3"  # will prepend /sdcard
    args = parse_args()
    sys.exit(main())
