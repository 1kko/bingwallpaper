# bingwallpaper
Fetches Bing Wallpaper and changes wallpaper by python script. 

# How to use:

Just run ```python3 wallpaper.py```

# Supported OS

- Linux: Unity and Gnome3
- Windows: 7, 10, 11 (tested)
- MacOS: (not tested). fix for PR is welcome! 

# Why python?

You can download exact same functioning application from [Microsoft Bing Wallpaper](https://www.microsoft.com/en-us/bing/bing-wallpaper)

But it sits on your tray icon and eats your RAM (about 7-9MB), not available for other OS.

Well, I use Windows and I love it but I just wanted to remove the tray icon.

For better portability I also tried to have minimal dependencies from other library, using only included imports.


# How to automatically change my wallpaper everyday?

It depends on which operating system you would use, as all operating system includes own scheduler processes:

- Windows: [Task Scheduler](https://www.google.com/search?q=windows+task+scheduler&oq=windows+task+scheduler&aqs=edge..69i57j0i512l7.7612j0j1&sourceid=chrome&ie=UTF-8)
- Linux: [Cron](https://www.google.com/search?q=how+add+cron+job+on+linux&newwindow=1&sxsrf=ALiCzsaYUEqszEGk-S47EctGx9GrxyP51w%3A1671105959133&ei=pw2bY6zjB9iJoASztoiwAw&ved=0ahUKEwjs0s3oyvv7AhXYBIgKHTMbAjYQ4dUDCA8&uact=5&oq=how+add+cron+job+on+linux&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIFCAAQogQyBQgAEKIEOgoIABBHENYEELADOgQIABAeOgYIABAIEB46BQghEKABOgcIIRCgARAKOgQIIRAVSgQIQRgASgQIRhgAUMIDWJwOYN8PaAFwAXgAgAGYAYgBvAiSAQMwLjmYAQCgAQHIAQrAAQE&sclient=gws-wiz-serp)
- Mac: [Cron](https://www.google.com/search?q=how+add+cron+job+on+mac&newwindow=1&sxsrf=ALiCzsaNfD0ylTsK_-CMQ2tXZkEil8kfAg%3A1671105971185&ei=sw2bY7H8Cpbm-Aat8peoAg&ved=0ahUKEwjxoa3uyvv7AhUWM94KHS35BSUQ4dUDCA8&uact=5&oq=how+add+cron+job+on+mac&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIFCCEQoAE6CggAEEcQ1gQQsANKBAhBGABKBAhGGABQ9gRYmAZgqQloAnABeACAAYkBiAHqApIBAzAuM5gBAKABAcgBCsABAQ&sclient=gws-wiz-serp)


# Inspiration

I was inspired (actually stolen some code) by some of the followings.

- [Maximilian Muth's bing-wallpaper](https://github.com/mammuth/bing-wallpaper)

- [Screen resolution in multiple OSes](https://stackoverflow.com/a/21213145)

- [some answers in StackExchange](https://apple.stackexchange.com/questions/40644/how-do-i-change-desktop-background-with-a-terminal-command)
