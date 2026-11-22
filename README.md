# news-image-20261121 entry

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Elies87/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Elies87/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

An entry for the make.fun bounty [news-image-20261121](https://make.fun/bounty/news-image-20261121).

A self-contained Python program (standard library only) that draws one
1024x1024 PNG summing up the world news of Saturday 21 November 2026, and
writes it to /output/entry.png.

The front page is rendered entirely by code: a hand-built 5x7 bitmap
font, a small raster canvas, and panel illustrations drawn from
primitives (a missile rising over a naval-base skyline, a city under
attack, a globe, a shield, a falling market chart, three summit flags),
plus a news ticker. The day's stories: Iran's strikes on US bases in
Bahrain, the Russian missile hit on Kryvyi Rih, the COP31 deadlock in
Antalya, Mexico's capture of cartel boss "Chapo Isidro", the AI stock
sell-off, and the fallout of the Shenzhen summit. All news content lives
in one STORIES structure at the top of main.py, taken from real
reporting of the day; the program needs no network and runs
deterministically — two runs produce byte-identical output.

License: MIT (see LICENSE).
