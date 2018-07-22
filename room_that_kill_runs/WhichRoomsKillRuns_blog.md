###Legend of Zelda speedrunning-  Which rooms kill runs?
This is the part 2 of my series on analyzing speedrunning of Legend of Zelda  (check out part 1: Legend of Zelda speedrunning - top 5 time wasting rooms)

Back to the Legend of Zelda.  If you're like me you spent many hours as a kid playing this game.  The thing I remember about it at the time is that it was the first game I played with an open world.  I could choose how I wanted to go around the world and play the game.  This game wasn't like Super Mario Bros. Where you had to play the game in the order the game wanted you to (for the most part). In Legend of Zelda, you were free to choose, and I liked that.

## The Project

A few months ago I got pretty into watch Arcus87 on Twitch, and at the time he was speedrunning the Legend of Zelda (speedrunning is where players try to complete the game in the fastest time possible).  Arcus has this casual animated quality that really makes him a ton of fun to watch.  I was on board with his mission of beating Legend of Zelda in under 30 minutes. 

At the time I was also deciding that I wanted to leave the academic world and try to get into data science.  To accomplish that goal, I decided that I needed to learn Python since it's a major language used in data science.  I had already mastered Matlab with years of building models and data analysis during my PhD/postdoc, but I knew that wouldn't cut it in the data science field.  So I decided I needed a project to force myself to learn Python.  I picked scraping Arcus' stream and doing this data analysis you see here today.  So enjoy!

## Speedrunning Legend of Zelda

A few things you should know about speedrunning before we get started.  The Legend of Zelda has different rooms (also called screens), that the player has to travel through to eventually win the game.  The Legend of Zelda is open in that the player is free to choose different paths to accomplish this goal.  In speedrunning however, predefined routes are used to beat the game is the shortest time possible.  

I scraped data for 4581 of Arcus's runs.  Let's take a look at the rooms where those runs ended.

INSERT FIGURE OF TIMES ENTERED VS ROOM

On the figure we have dots representing rooms ordered in the position on the route on the horizontal (x-axis) and the number of times Arcus entered that room on the vertical (y-axis). You can look at the number of times entered on the left or the fraction of times entered on right.  We can that the overwhelming majority of runs ended before Arcus completed his first dungeon (which in this route is Dungeon 3, remember players are mostly free to choose the order the complete the dungeons).  We can also see that Arcus completed his run 102 times in this data set, or about 2.2% of the time.  

The picture above gives us a good sense how quickly most runs ended, but it makes it difficult to interpret where runs were *most likely* to end.

## Dangerous Rooms

We're going to look at a simple question while examining my Arcus87 dataset, which rooms in the speedrun kill the most runs?  After exploring and becoming familiar with the data, I thought of two different ways to think about this question. First, I could count the run of times a run ended in particular room, I call this the **reset count**. Second I could calculate how likely the run is to end in that room, I call this the **reset fraction**.

The reset count gives a clear indication of which room are most troublesome in shear numbers.  It is heavily weighted toward the begining of the run, as you can easily see in the above figure.  If the run gets off to a bad start, it's likely to be reset.  The reset fraction however, gives a better indication of the rooms overall difficulty of the room by showing us just how often that room killed a run.

## By reset count
### #5 - 3DD62
### #4 - 1OF81
### #3 - 1OG81
### #2 - 3DH51
### #1 - 3DF61

## By reset fraction
### #10 - 4DG21
### #9 - 1OF81
### #8 - 1OG81
### #7 - 5DE31
### #6 - 9DE51
### #5 - 3DD62
### #4 - 4DH21
### #3 - 3DF61
### #2 - 5DF11 
### #1 - 3DH51 

How does this compare to my previous results

Some biases
- reseting runs based on time
- 30-30 routes
- reset at begining of overworld

Some technical notes
- scraper
- room counting caveats: rooms can be entered more than once, and there are different routes.