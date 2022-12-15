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
from typing import Optional, Union, Tuple
import subprocess


# operating system
class OS:
    """Operating System Constants
    """
    WINDOWS = "win32"
    LINUX = "linux"
    MACOS = "macosx"


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
def getOSResolution() -> Tuple[OS, int, int]:
    """Detect OS and screen resolution.

    Returns:
        Tuple[OS, int, int]: (os_type, screen_width, screen_height) 
            where screen_width and screen_height are int types according to measurement.
            In case all fails, it returns default value: ('linux', 1920, 1080)
    """

    try:  # Platforms supported by GTK3, Fx Linux/BSD
        from gi.repository import Gdk
        screen = Gdk.Screen.get_default()
        width = screen.get_width()
        height = screen.get_height()
        return (OS.LINUX, width, height)
    except:
        try:  # Windows only
            from win32api import GetSystemMetrics
            width_px = GetSystemMetrics(0)
            height_px = GetSystemMetrics(1)
            return (OS.WINDOWS, width_px, height_px)
        except:
            try:  # Windows only
                import ctypes
                user32 = ctypes.windll.user32
                width_px = user32.GetSystemMetrics(0)
                height_px = user32.GetSystemMetrics(1)
                return (OS.WINDOWS, width_px, height_px)
            except:
                try:  # Mac OS X only
                    import AppKit
                    for screen in AppKit.NSScreen.screens():
                        width_px = screen.frame().size.width
                        height_px = screen.frame().size.height
                        return (OS.MACOS, width_px, height_px)
                except:
                    try:  # Linux/Unix
                        import Xlib.display
                        resolution = Xlib.display.Display().screen().root.get_geometry()
                        width_px = resolution.width
                        height_px = resolution.height
                        return (OS.LINUX, width_px, height_px)
                    except:
                        try:  # Linux/Unix
                            args = ["xrandr", "-q", "-d", ":0"]
                            proc = subprocess.Popen(
                                args, stdout=subprocess.PIPE)
                            for line in iter(proc.stdout.readline, ''):
                                if isinstance(line, bytes):
                                    line = line.decode("utf-8")
                                if "Screen" in line:
                                    width_px = int(line.split()[7])
                                    height_px = int(line.split()[9][:-1])
                                    return (OS.LINUX, width_px, height_px)
                        except:
                            # Failover
                            screensize = (OS.LINUX, 1920, 1080)
                            logging.warning(
                                "Failed to detect OS and Screen resolution. Falling back to %s:%sx%s" % screensize)
                            return screensize


def downloadWallpaper(nDaysAgo: Optional[int] = 0, overwrite: Optional[bool] = False) -> Union[OS, Path]:
    """Download wallpaper

    Args:
        nDaysAgo (Optional[int], optional): Get `nDaysAgo` wallpaper. Defaults to 0(today). Defaults to 0.
        overwrite (Optional[bool], optional): Downloads any if set to True. Defaults to False.

    Returns:
        Union[OS, Path]: OS constant and Path object from Pathlib.
    """
    platform, width, height = getOSResolution()
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

    return platform, imagePath


def setWallpaper(platform: OS, imagePath: Path) -> bool:
    """Sets Wallpaper

    Args:
        platform (OS):  Different action to set wallpaper is taken according to platform
        imagePath (Path): Path to wallpaper

    Returns:
        bool: True if successful, otherwise False
    """
    if not imagePath.is_file():
        logging.error(f"{imagePath} is not found")
        return False

    if platform == OS.WINDOWS:
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

    elif platform == OS.LINUX:
        command = ["gsettings", "set", "org.gnome.desktop.background",
                   "picture-uri", f"file://{str(imagePath)}"]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode == 0:
            return True
        else:
            return False

    elif platform == OS.MACOS:
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
    platform, imagePath = downloadWallpaper()
    setWallpaper(platform, imagePath)
