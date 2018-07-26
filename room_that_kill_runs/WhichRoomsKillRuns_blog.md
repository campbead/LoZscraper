###Legend of Zelda speedrunning-  Which rooms kill runs?
This is the part 2 of my series on analyzing speedrunning of Legend of Zelda  (check out part 1: Legend of Zelda speedrunning - top 5 time wasting rooms)

Back to the Legend of Zelda.  If you're like me you spent many hours as a kid playing this game.  I remember this game for being the first I played with an open world.  I could choose how I wanted to go around the world and play the game.  This game wasn't like Super Mario Bros. having me play the game in the order the game wanted me to. In Legend of Zelda, I was free to choose, and I liked that.

## The Project

A few months ago I got pretty into watch Arcus87 on Twitch, and at the time he was speedrunning the Legend of Zelda (speedrunning is where players try to complete the game in the fastest time possible).  Arcus has this casual animated quality that really makes him a ton of fun to watch.  I was on board with his mission of beating Legend of Zelda in under 30 minutes. 

At the time I was also deciding that I wanted to leave the academic world and try to get into data science.  To accomplish that goal, I decided that I needed to learn Python since it's a major language used in data science.  I had already mastered Matlab with years of building models and data analysis during my PhD/postdoc, but I knew that wouldn't cut it in the data science field.  So I decided I needed a project to force myself to learn Python.  I picked scraping Arcus' stream and doing this data analysis you see here today.  So enjoy!

## Speedrunning Legend of Zelda

A few things you should know about speedrunning before we get started.  The Legend of Zelda has different rooms (also called screens), that the player has to travel through to eventually win the game.  The Legend of Zelda is open in that the player is free to choose different paths to accomplish this goal.  In speedrunning however, predefined routes are used to beat the game is the shortest time possible.  

Arcus mostly ran what he called the "Double Hundo" route, name for the two 100 rubie secret rooms you must visit on the route.  He did a lot of runs (9472) in this push but I only was able to dowload vides for the last 4581 of Arcus's runs.  Let's take a look at the rooms where those runs ended.

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
### #10 - 4DG21 - Vire (before boss)
Here Arcus must deafeat 5 Vires before moving on to the next room.  Coming into the room with a maximum of 4 hearts means the margin for error here is small.  Vires, once they are hit split into two red Keese meaning there are actually 15 enemies to defeat on this screen.  Arcus mitigates this using bombs, which are capable of killing Vires and the Keese they spawn.  This room resulted in a death/reset about 12% of the time or 105 times in the runs I examined.

### #9 - 1OF81 - Screen wrap
### #8 - 1OG81 - Screen wrap

I'm count these rooms together since they are sequetial rooms and they really have the same root cause of failure, the screen wrap.  At a few points in the run, Arcus must perform a neat little trick calle the screen wrap which allows him to warp Link from the right edge of the screen to the left edge of the screen.  I'll fully admit I spent about 30 minutes trying to do this technique at home and was not successful once!  These room are the 2nd and 3rd rooms of the run.  So Arcus doesn't accept any failures here, if he misses a screen wrap here, he just resets the run.  There are some screen wraps later in the run where a failure to execute move is tolerated.  

Individually, he's able to pull off the move about 87% of the time.  Which means that taken together these rooms kill about 1/4 runs, or 1054 runs total.  WOW!

### #7 - 5DE31 - Digdogger (boss)
The Digdogger is a fast moving boss that needs to be killed a particular way.  First the flute is used to transform the Digdogger into his second form.  Then Arcus uses bomb to damage the boss and finishes him off with the sword.  All the while he's being shot at by Stone Statues.  This room resulted in a death/reset about 14% of the time or 47 times in the runs I examined.

### #6 - 9DE51 - Gannon (final boss)
Gannon, the big boss.  I was happy to see that Gannon made this list.  He's a tough boss and 15% of the time, Arcus would be defeated by him.  I mean that's actually pretty amazing that he's able to defeat him 85% of the time.  It's probably a testament to all the work he has put into practicing these end-game rooms.

### #5 - 3DD62 - Red Darknut 2 
In this room, Arcus faces off against 5 Darknuts.  He must kill the Darknuts before the lower door opens allowing him to advance. This is a formidible task as this is his first Dungeon of the game and he only has a maximum of 3 hearts here.  18% the time he enters this room his run ends here.  

*note: he actually enters this room twice, the statistics quoted here only refer the the 2nd time he enters this room, and has to defeat the Darknuts*

### #4 - 4DH21 - Geelok (boss)
The Geelok is a tough boss the kills Arcus runs 24% of the time.  This multi-headed boss gets more powerful as you damage it, with heads detaching from the main body and flying around to attack Link.  

### #3 - 3DF61 - Red Darknut 1
This is the first big test for Arcus in his speedrun.  In this room he has to quickly get a bomb move on to the next room.  If picks up an early bomb, he can move along early, otherwise he is forced to defeat all three for an early bomb drop.  25% of the time his run ends here.  As mentioned in my previous blog post, this room has big spread of times is takes to clear, 5.4 seconds difference between his median time and the top 10% of times.

### #2 - 5DF11 - Blue Darknut 2 (aka the Olive Garden)
Of all the rooms that standout as troublesome while watching Arcus play, the Olive Garden stands out as being the most troublesome.  This room is brutal.  He has to defeat 6 Blue Darknuts here to move on to grab the flute (or Breadstick, if you're a fan of Arcus).  An enornmous 30% of runs end here and when he is able to complete this room, there is an 8.2 second spread between his median completion time and his 10% best times.  

### #1 - 3DH51 - Manhandla (boss)
This boss a tough one.  Arcus comes into this room with only 3 hearts max, so the margin for error is small.  A bad bomb placement here can kill the run.  Even if he does defeat the boss, if the total run time is too high here, he's likely to just reset the run himself.  The Manhandla room gets the best of 34% the rooms. 

## Which rooms never kill runs?  

Most of them! In my dataset, 134 of the 234 rooms I define never result in a death.  The big story here is how different dungeons are from the overworld.  61 of 141 (43%) of dungeon rooms had zero deaths.  In the overworld it's 71 out of 93 (76%) never resulted in death.  Of the 4479 runs that weren't completed, 3162 (70%) ended in a dungeon.  Only 1315 runs (30% of non-completed runs) ended in the overworld.  If we filter the first overworld push where resets are frequent due to missed screen wraps, then that number drops to 68 (2% of non-completed runs).  

The takeaway here: Dungeons are hard. This is by far where most deaths/resets occur.

Some technical notes
- scraper
- room counting caveats: rooms can be entered more than once, and there are different routes.