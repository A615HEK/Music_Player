# Motivation
This is a passion project of mine. Not done to showcase my brilliance. There's loads of much better music players out there. This project was undertaken to help me learn the basics of building a structured app. I have wanted to build a music player for myself. This is the reason for such an endeavour.

# The Journey
Discussing the thought process, Design decisions and tradeoffs. Changes Done and to be done (context and actions for current and past TODO portions barring a few minor deets):
<ol>
<li> Migrated from FastAPI to a simple Py module/file
<br> Context: Cold start problem (~20 seconds from displaying 1st screen to UI update), overkill for the app in its current state and usecase
<br> Result: Load time without threading dropped to ~4s (5x improvement in loading time); <i> Additional testing TBD </i>
</li>
<li> Background thread for async UI update
</li>
</ol>