#! /usr/bin/python3
# Author: 1kko <me@1kko.com>
# https://github.com/1kko/bing-wallpaper
# Version: 1.0
# License: MIT
# Description: Downloads the Bing Wallpaper and sets it as wallpaper (Linux / Windows / Mac).

# import requests
from urllib.request import urlopen, urlretrieve
from pathlib import Path, PurePath
import logging
import json
from typing import Optional, Tuple, Union
import subprocess
import platform
import argparse


def getPlatform() -> str:
    """Get current platform and returns platform in string

    Returns:
        str: platform string (eg. 'Windows', 'Linux', 'macOS', etc)
    """
    return platform.system()


def getBingMetadata(width: int, height: int) -> json:
    url = f"https://go.microsoft.com/fwlink/?linkid=2151983&screenWidth={str(width)}&screenHeight={str(height)}&env=live"
    try:
        with urlopen(url) as res:
            response = json.loads(res.read().decode())
        return response
    except Exception as e:
        logging.exception(e)
        raise e


# I grabbed and modified a bit from code here: https://stackoverflow.com/a/21213145
def getResolution() -> Tuple[int, int]:
    """Detect OS and screen resolution.

    Returns:
        Tuple[int, int]: (screen_width, screen_height) 
            where screen_width and screen_height are int types according to measurement.
            In case all fails, it returns default value: (1920, 1080)
    """

    currentPlatform = getPlatform()
    fallBackSize = (1920, 1080)

    def _fallback():
        # Failover
        logging.warning(
            f"Failed to detect OS and Screen resolution. Falling back to {fallBackSize}")
        return fallBackSize

    if currentPlatform == "Linux":
        try:  # Platforms supported by GTK3, Fx Linux/BSD
            from gi.repository import Gdk
            screen = Gdk.Screen.get_default()
            width = screen.get_width()
            height = screen.get_height()
            return (width, height)
        except:
            try:
                import Xlib.display
                screen = Xlib.display.Display().screen().root.get_geometry()
                width = screen.width
                height = screen.height
                return (width, height)
            except:
                try:  # Linux/Unix
                    args = ["xrandr", "-q", "-d", ":0"]
                    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
                    for line in iter(proc.stdout.readline, ''):
                        if isinstance(line, bytes):
                            line = line.decode("utf-8")
                        if "Screen" in line:
                            width = int(line.split()[7])
                            height = int(line.split()[9][:-1])
                            return (width, height)
                except:
                    _fallback()

    elif currentPlatform == "Windows":
        try:  # Windows only
            from win32api import GetSystemMetrics
            width = GetSystemMetrics(0)
            height = GetSystemMetrics(1)
            return (width, height)

        except:
            try:  # Windows only
                import ctypes
                user32 = ctypes.windll.user32
                width = user32.GetSystemMetrics(0)
                height = user32.GetSystemMetrics(1)
                return (width, height)
            except:
                _fallback()

    elif currentPlatform == "macOS":
        try:  # Mac OS X only
            import AppKit
            for screen in AppKit.NSScreen.screens():
                width = screen.frame().size.width
                height = screen.frame().size.height
                return (width, height)
        except:
            _fallback()

    else:
        _fallback()


def downloadWallpaper(nDaysAgo: Optional[int] = 0, overwrite: Optional[bool] = False) -> Union[Path, dict]:
    """Download wallpaper

    Args:
        nDaysAgo (Optional[int], optional): Get `nDaysAgo` wallpaper. Defaults to 0(today). Defaults to 0.
        overwrite (Optional[bool], optional): Downloads any if set to True. Defaults to False.

    Returns:
        Path: Pathlib object specifies path of image file.
        dict: Metadata related to image file.
    """
    width, height = getResolution()
    metadata = getBingMetadata(width, height)

    # metadata is ordered recent date first.

    if nDaysAgo > len(metadata['images']):
        nDaysAgo = len(metadata['images'])
    idx = nDaysAgo

    target = metadata['images'][idx]
    filename = PurePath(target['url']).name
    logging.info(f"{filename}: {target}")

    # create images directory
    Path('images').mkdir(parents=True, exist_ok=True)

    # check if file exists
    imagePath = Path('./images').resolve(strict=True) / Path(filename)
    jsonPath = imagePath.with_suffix(".json")
    if not imagePath.is_file() or overwrite is True:
        # write image file
        try:
            logging.debug(
                f"Retrieving {target['url']} and save to {imagePath}")
            urlretrieve(target['url'], imagePath)
        except Exception as e:
            logging.exception(f"Unable to fetch {target['url']}")
            raise

        # write json file
        with open(jsonPath, "w") as jfp:
            json.dump(target, jfp)

    return imagePath, target


def setWallpaper(imagePath: Path) -> bool:
    """Sets Wallpaper

    Args:
        imagePath (Path): Path to wallpaper

    Returns:
        bool: True if successful, otherwise False
    """

    currentPlatform = getPlatform()
    if not imagePath.is_file():
        logging.error(f"{imagePath} is not found")
        return False

    if currentPlatform == "Windows":
        import ctypes
        logging.info(f"Setting {imagePath} as a wallpaper")
        uiAction = 20  # SPI_SETDESKWALLPAPER = 0x0014 or 20 in decimal
        uiParam = 0
        pvParam = str(imagePath)
        fWinIni = 0
        success = ctypes.windll.user32.SystemParametersInfoW(
            uiAction, uiParam, pvParam, fWinIni)
        if success:
            logging.info("Wallpaper is set.")
            return True
        else:
            logging.error("Setting wallpaper has failed.")
            return False

    elif currentPlatform == "Linux":
        command = ["gsettings", "set", "org.gnome.desktop.background",
                   "picture-uri", f"file://{str(imagePath)}"]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode == 0:
            return True
        else:
            return False

    elif currentPlatform == "macOS":
        # might need to try if current method doesn't work
        # https://apple.stackexchange.com/a/145174
        # sqlite3 ~/Library/Application\ Support/Dock/desktoppicture.db "update data set value = '/path/to/any/picture.png'" && killall Dock

        command = ["osascript", "-e",
                   "'tell application \"Finder\" to set desktop picture to POSIX file \"{imagePath}\"'"]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode == 0:
            return True
        return False
    else:
        logging.error("OS Type unknown")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--ndays', help="Number of previous days to retrieve.",
                        dest="nDaysAgo", default=0, type=int)
    parser.add_argument('-m', '--metadata',
                        help="output metadata to stdout.", dest="showJson", action=argparse.BooleanOptionalAction)

    showJson = parser.parse_args().showJson
    nDaysAgo = parser.parse_args().nDaysAgo
    nDaysAgo = 7 if nDaysAgo >= 7 else nDaysAgo
    nDaysAgo = 0 if nDaysAgo <= 0 else nDaysAgo
    imagePath, metadata = downloadWallpaper(nDaysAgo=nDaysAgo)
    if showJson and metadata is not None:
        print(json.dumps(metadata, indent=4, sort_keys=True))
    setWallpaper(imagePath)
