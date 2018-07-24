from PIL import Image
import pytesseract
import argparse
import cv2
import os
import imutils
import numpy as np
import sqlite3 as lite
import sys
import time
import math
import csv


def get_other_info(time,video):
    vidcap.set(cv2.CAP_PROP_POS_MSEC,time)
    success,image = vidcap.read()
    time_image = image[540:600,50:297]
    level_image = image[43:73,585:623]
    rubie_image = image[71:91,697:777]
    key_image = image[112:134,722:751]
    bomb_image = image[133:156,722:751]
    full_hearts, total_hearts = get_num_hearts(image)
    #level = get_number_text(level_image,'single')
    rubies = get_number_text(rubie_image,'multi')
    keys = get_number_text(key_image,'single')
    bombs = get_number_text(bomb_image,'single')
    #time_independent = get_number_text(time_image,'multi')
    #output = [full_hearts, total_hearts, level, rubies, keys, bombs, time_independent]
    output = [full_hearts, total_hearts, rubies, keys, bombs]
    return output
def get_num_hearts(image):
    # definitions:
    lower_full = np.array([0, 15, 70])
    upper_full = np.array([30, 35, 250])
    lower_empty = np.array([150, 160, 220])
    upper_empty = np.array([255, 255, 255])
    full_heart_area_lower = 200
    full_heart_area_upper = 300
    half_heart_area_lower = 60
    half_heart_area_upper = 100

    # define heart image:
    hearts_image = image[98:161,967:1200]  # this the heart region

    # initialize hearts
    full_hearts = 0
    empty_hearts = 0

    # calculate shapes in hearts image
    shapeMask_full = cv2.inRange(hearts_image, lower_full, upper_full)
    shapeMask_empty = cv2.inRange(hearts_image, lower_empty, upper_empty)

    # count full hearts
    cnts_full_hearts = cv2.findContours(shapeMask_full.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_full_hearts = cnts_full_hearts[0] if imutils.is_cv2() else cnts_full_hearts[1]
    for c in cnts_full_hearts:
        if cv2.contourArea(c) >= full_heart_area_lower and cv2.contourArea(c) <= full_heart_area_upper:
            full_hearts = full_hearts +1 
        if cv2.contourArea(c) >= half_heart_area_lower and cv2.contourArea(c) <= half_heart_area_upper:
            full_hearts = full_hearts + 0.5 
    # count empty hearts
    cnts_empty_hearts = cv2.findContours(shapeMask_empty.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_empty_hearts = cnts_empty_hearts[0] if imutils.is_cv2() else cnts_empty_hearts[1]
    for c in cnts_empty_hearts:
        if cv2.contourArea(c) >= full_heart_area_lower and cv2.contourArea(c) <= full_heart_area_upper:
            empty_hearts = empty_hearts +1 
        if cv2.contourArea(c) >= half_heart_area_lower and cv2.contourArea(c) <= half_heart_area_upper:
            empty_hearts = empty_hearts + 0.5 
    return full_hearts, empty_hearts+full_hearts
def get_number_text(image_selection,flag):
    gray = cv2.cvtColor(image_selection, cv2.COLOR_BGR2GRAY)
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)
    if flag == 'multi':
        text = pytesseract.image_to_string(Image.open(filename), lang = 'eng') # options for multi character
    elif flag == 'single':
        text = pytesseract.image_to_string(Image.open(filename), lang = 'eng', config='-psm 10 -c tessedit_char_whitelist=0123456789') # options for single character
    elif flag == 'rubie':
        text = pytesseract.image_to_string(Image.open(filename), lang = 'eng', config='-psm 10 -c tessedit_char_whitelist=X0123456789')
    os.remove(filename)
    return text
def write_results(con,screen_data):
    with con:
        cur = con.cursor() 
        cur.execute("INSERT INTO Screen VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", screen_data)
def init_table(con):
    with con:
        cur = con.cursor() 
        cur.execute("DROP TABLE IF EXISTS Screen")
        cur.execute("CREATE TABLE Screen(Run TEXT, Run_Man INT, Abs_time REAL, Room TEXT, Full_hearts REAL, Total_hearts INT, Rubies TEXT, Keys TEXT, Bombs TEXT)")
def find_next_screen(begin_screen, begin_time, delta_t, vidcap):
    initial_screen = True
    time = begin_time
    while initial_screen:
        time = time + delta_t
        screen = get_screen_at_time(time,vidcap)
        if screen != begin_screen:
            initial_screen = False
    upper_bound_time = time
    end_screen = screen
    return end_screen, upper_bound_time
def find_start_screen(begin_time, delta_t, vidcap):
    not_start = True
    time = begin_time
    while not_start:
        time = time + delta_t
        screen = get_screen_at_time(time,vidcap)
        if screen == 'OH8':
            not_start= False
    upper_bound_time = time
    end_screen = screen
    return end_screen, upper_bound_time
def find_time_room_switch(begin_screen, end_screen, begin_time, end_time, time_resolution,vidcap):
    time = (begin_time + end_time)/2
    new_screen = get_screen_at_time(time,vidcap)
    if new_screen == begin_screen:
        # if the middle time is the begining screen, search the later half
        return find_time_room_switch(begin_screen, end_screen, time, end_time, time_resolution,vidcap)
    else:
        if time - begin_time < time_resolution:
            return time, new_screen
        else:
            return find_time_room_switch(begin_screen, new_screen, begin_time, time, time_resolution,vidcap)
def get_screen_at_time(time,vidcap):
    def in_overworld(image):
        gray_cut = 50 # cutoff for overworld gray
        # convert image to gray scale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # get average of gray scale
        average_gray = np.average(gray)
        # if average of gray scale falls within a range return true, otherwise false
        if average_gray > gray_cut:
            return True
        else:
            return False
    def get_screen_coords(image):
        cutoff_area = 20
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 110, 255, cv2.THRESH_BINARY)[1]
        # find contours in the thresholded image
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        # process contours to find X,Y position of mini-map marker

        if len(cnts) == 1:
        # if only one contour exists, the return the coordinates of its centre
            M = cv2.moments(cnts[0])
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                # if centre cannot be calculated return -1 for cX, cY
                cX = -1
                cY = -1
        elif len(cnts) > 1:
            cnts_real = []
            for cnt in cnts:
                #print('area:',cv2.contourArea(cnt))
                if cv2.contourArea(cnt) > cutoff_area:
                    cnts_real.append(cnt)
            if len(cnts_real) == 1:       
                M = cv2.moments(cnts_real[0])
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    # if centre cannot be calculated return -1 for cX, cY
                    cX = -1
                    cY = -1  
            else:
            # if more than one contour is found return -2 
                cX = -2
                cY = -2
        else:
            # if zero are found return -3
            cX = -3
            cY = -3

        return cX,cY

    vidcap.set(cv2.CAP_PROP_POS_MSEC,time)
    success,image = vidcap.read()
    image = image[70:155, 430:644] # RANGE HERE IS SET FOR MINI MAP ON SCREEN
    X_off = 430
    Y_off = 70
    pixel_cutoff = 4
    overworld_X_coord = np.linspace(435.5,638,16)
    overworld_X_label = ('A', 'B', 'C', 'D','E', 'F', 'G', 'H', 'I','J', 'K', 'L', 'M', 'N', 'O', 'P')
    overworld_Y_coord = np.linspace(75,148.5,8)
    overworld_Y_label = ('1','2','3','4','5','6','7','8')

    dungeon_X_coord = np.linspace(386,683,12)
    dungeon_X_label = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J','K', 'L')
    dungeon_Y_coord = np.linspace(73,149,8)
    dungeon_Y_label = ('1','2','3','4','5','6','7','8')
   

    X,Y = get_screen_coords(image)
    X_adj = X + X_off
    Y_adj = Y + Y_off
    if X < 0:
        screen = 'X' + str(X)
        return screen
    else:
        if in_overworld(image):
            closest = min(abs(np.array(overworld_X_coord - X_adj)))
            closest_ind = np.argmin(abs(np.array(overworld_X_coord - X_adj))) 
            if closest < pixel_cutoff:
                X_L = overworld_X_label[closest_ind]
            else:
                X_L = 'X'
            closest = min(abs(np.array(overworld_Y_coord - Y_adj)))
            closest_ind = np.argmin(abs(np.array(overworld_Y_coord - Y_adj)))             
            if closest < pixel_cutoff:
                Y_L = overworld_Y_label[closest_ind]
            else:
                Y_L = '0'    
            screen = 'O' + X_L + Y_L
            return screen
        else:
            closest = min(abs(np.array(dungeon_X_coord - X_adj)))
            closest_ind = np.argmin(abs(np.array(dungeon_X_coord - X_adj)))        
            if closest < pixel_cutoff:
                X_L = dungeon_X_label[closest_ind]
            else:
                X_L = 'X'
            closest = min(abs(np.array(dungeon_Y_coord - Y_adj)))
            closest_ind = np.argmin(abs(np.array(dungeon_Y_coord - Y_adj)))           
            if closest < pixel_cutoff:
                Y_L = dungeon_Y_label[closest_ind]
            else:
                Y_L = '0'    
            screen = 'D' + X_L + Y_L
            return screen 
def remove_blank_screens(screen_list):

    return [screen for screen in screen_list if 'X' not in screen]
def get_run_number(time,video):
    vidcap.set(cv2.CAP_PROP_POS_MSEC,time)
    success,image = vidcap.read()
    run_image = image[312:330,254:296]
    return get_number_text(run_image,'multi')

def print_time_since_start(time, start_time):
    delta_time = time - start_time
    delta_time_sec = delta_time/1000
    mins = math.floor(delta_time_sec/60)
    secs = round(delta_time_sec - mins * 60)
    print(mins, ':', secs)

def load_room_list(room_list_file):
    with open(room_list_file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        room_list = []
        for row in spamreader:
            room_list.append(row[1])
    return room_list

def process_run(start_time, video, dT, run_number, master_room_list, unique_room_list, time_resolution,con):
    kill_room = 'XXX'
    kill_video = False
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) #find_master_end_time(video)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    master_end_time = frame_count/fps *1000

    master_end_time = 18280000
    if run_number is None:
        run_number = 0
    run_number_man = run_number -1 
    screen = get_screen_at_time(start_time,video)
    print(screen)
    if screen != 'OH8':
        screen, known_time_in_room = find_start_screen(start_time, dT, video)
        print(screen,known_time_in_room)
    while kill_video == False:

        verbose_list = []#['8DE41','8DE31'] #['4OI31', '4OJ31'] #['9DE41', 'OH8']

        run_room_list = [master_room_list[0]]
        run_time_list = []
        current_room = master_room_list[0]
        room_ind = 0
        next_room_in = master_room_list[1]

        # get run number
        run_number = get_run_number(known_time_in_room,video)
        print('Run: ', run_number)
        # run some check that that run isn't reset on room 0

        while next_room_in != master_room_list[0] and next_room_in != kill_room :
            if room_ind == 0:
                current_room_time = find_start_time_room(video, current_room, known_time_in_room, dT, time_resolution)
                time = current_room_time
                run_number_man = run_number_man + 1
                print('man run:', run_number_man)
            else:
                room_A = [master_room_list[room_ind-1]]
                room_B = master_room_list[room_ind]
                time_A = [max_time_previous]
                time_B = [known_time_in_room]
                run_count = 0 
                if any(unique_room_list[room_ind] in room for room in verbose_list):
                    print('UNIQUE ID:',unique_room_list[room_ind])
                    print('RoomA:', room_A, 'RoomB:', room_B)
                    print('TimeA:', time_A, 'TimeB:', time_B)
                current_room_time, time = find_start_time_room_2(video, room_A, room_B, time_A, time_B, time_resolution, run_count)
            print('room:',current_room,' time:',current_room_time, 'roomID:' ,unique_room_list[room_ind])
            run_time_list.append(current_room_time)
            room_ind = room_ind + 1
            next_room_in = master_room_list[room_ind]
            rooms_list_selection = master_room_list[room_ind-1:room_ind+3]
            time_previous = [time]
            time_future =[]
            if any(unique_room_list[room_ind] in room for room in verbose_list):
                verbose_mode = True
            else:
                verbose_mode = False
            count = 0
            next_room_out, known_time_in_room, max_time_previous = find_time_next_room_2(video,time_previous, time_future, dT, rooms_list_selection, master_end_time, time_resolution, verbose_mode, count)  
            if any(unique_room_list[room_ind] in room for room in verbose_list):
                print('next_room_out:',next_room_out)
                print('next_room_in:', next_room_in)
                print('known_time_in_room:', known_time_in_room)
                print('max_time_previous:', max_time_previous)
            #next_room_out, known_time_in_room, max_time_previous = find_time_next_room(video,known_time_in_room,dT,rooms_list_selection,master_end_time)
            if next_room_in == next_room_out:
                run_room_list.append(next_room_in)
                current_room = next_room_in
            else: 
                next_room_in = next_room_out

        # grab all info from begining of each screen
        keys_list = []
        bomb_list = []
        rubies_list = []
        #independent_time_list =[]
        #level_list = []
        full_hearts_list =[]
        total_hearts_list =[]
        print('run complete: getting room info')
        for time in run_time_list:
            output = get_other_info(time+800,video)
            full_hearts_list.append(output[0])
            total_hearts_list.append(output[1])
            #level_list.append(output[2])
            rubies_list.append(output[2])
            keys_list.append(output[3])
            bomb_list.append(output[4])
            #independent_time_list.append(output[6])
        # save data to a sql

        if con != False:
            print('saving run')
            for index in range(0,len(run_time_list)):
                screen_data = []
                screen_data.append(run_number)
                screen_data.append(run_number_man)
                screen_data.append(run_time_list[index])
                screen_data.append(unique_room_list[index])
                screen_data.append(full_hearts_list[index])
                screen_data.append(total_hearts_list[index])
                screen_data.append(rubies_list[index])
                screen_data.append(keys_list[index])
                screen_data.append(bomb_list[index])
                write_results(con,screen_data)
            print('save complete')    
        # TESTING MODE
        #print(run_time_list)
        #print(run_room_list)
        #print(full_hearts_list)
        #print(total_hearts_list)
        #print(level_list)
        #print(rubies_list)
        #print(keys_list)
        #print(bomb_list)
        #print(independent_time_list)

        if next_room_in == kill_room:
            kill_video = True
        else:
            kill_video = False

def my_min(list):
    if len(list) > 0:
        return min(list)
    else:
        return list

def find_start_time_room(video, current_room, known_time_in_room, dT, time_resolution):
    time = (known_time_in_room + known_time_in_room-dT)/2
    new_screen = get_screen_at_time(time,video)
    #print(time)
    if new_screen == current_room:
        dT = dT/2
        known_time_in_room = time
        if dT < 100:
            dT = 100
        #print(current_room)
        # if the middle time is the begining screen, search the later half
        return find_start_time_room(video, current_room, known_time_in_room, dT,time_resolution)
    else:
        if known_time_in_room - time < time_resolution:
            return time
        else:
            dT = dT/2
            return find_start_time_room(video, current_room, known_time_in_room, dT,time_resolution)
def find_start_time_room_2(video, room_A, room_B, time_A, time_B, time_resolution, run_count):
    #if room_A 
    #print(room_A)
    #print(room_B)
    #print(time_A)
    #print(time_B)
    run_count = run_count +1
    if any(room_B in room for room in room_A):
        print('ROOMS ARE SAME - BAD')
    if (min(time_B) - max(time_A)) < time_resolution:
        return min(time_B), max(time_B)
    else:

        time = (max(time_A) + min(time_B))/2
        test_screen = get_screen_at_time(time,video)

        if any(test_screen in room for room in room_A):
            time_A.append(time)
            return find_start_time_room_2(video,room_A,room_B, time_A, time_B,time_resolution, run_count)
        elif test_screen == room_B:
            time_B.append(time)
            return find_start_time_room_2(video,room_A,room_B, time_A, time_B,time_resolution, run_count)
        else:
            # if you're in a room without an ID, then step backwards in TR steps until you have the original room
            # or you find next room.  If you find next room, restart with updated times.  If you get to original 
            # room then add

            # are we <= TS away from room_A
            #print('***')
            if (abs(max(time_A)-time) < time_resolution) or run_count > 10:
                room_A.append(test_screen)
                time_A.append(time)
                run_count = 0
                return find_start_time_room_2(video,room_A,room_B, time_A, time_B,time_resolution, run_count)
            else:
                # if not calc array of times
                time_array = [time - time_resolution]
                
            #    print('time:',time)

                array_test = min(time_array) > (max(time_A) + time_resolution)
             #   print(array_test)
                while array_test: 
                    time_array.append(min(time_array) - time_resolution)
                    array_test = min(time_array) > max(time_A) + time_resolution
                
                test_screen_array = []
                for ind_time in time_array:
                    test_screen_ind = get_screen_at_time(ind_time,video)
                    if any(test_screen_ind in room for room in room_A):
                        time_A.append(ind_time)
                #        print('&&&')
                #        print('maxA:',max(time_A))
                #        print('minB:',min(time_B))
                        return find_start_time_room_2(video,room_A,room_B, time_A, time_B,time_resolution, run_count)
                max_test_screen = get_screen_at_time(max(time_array),video)
                time_A.append(max(time_array))
                room_A.append(max_test_screen)
                #print('^^^')
                return find_start_time_room_2(video,room_A,room_B, time_A, time_B,time_resolution, run_count)


            # LEGACY CODE
            # un_id_room = True
            # time_resolution_adapt = time_resolution
            # while un_id_room:
            #     plus_time = time + time_resolution_adapt
            #     minus_time = time - time_resolution_adapt
            #     plus_screen = get_screen_at_time(plus_time,video)
            #     minus_screen = get_screen_at_time(minus_time,video)
            #     if plus_screen == room_A:
            #         time_A.append(plus_time)
            #         un_id_room = False
            #     if plus_screen == room_B:
            #         time_B.append(plus_time)
            #         un_id_room = False
            #     if minus_screen == room_A:
            #         time_A.append(minus_screen)
            #         un_id_room = False
            #     if minus_screen == room_B:
            #         time_B.append(minus_screen)
            #         un_id_room = False
            #     if un_id_room == True:
            #         time_resolution_adapt = time_resolution_adapt + time_resolution
            #     else:
            #         return find_start_time_room_2(video,room_A,room_b, time_A, time_B,time_resolution)
def find_time_next_room_2(video,time_previous, time_future,dT,rooms_list_selection,master_end_time, time_resolution, verbose_mode, count):
    # init code


    previous_room = rooms_list_selection[0]
    next_room = rooms_list_selection[1]
    future_rooms = rooms_list_selection[2:4]
    
    #special code for first room looking for next room
    if previous_room == 'OH8':
        room = 'OH8'
        dt = 2000
        time = max(time_previous)
        while room == 'OH8':
            while room == 'OH8':
                time = time + dt
                room = get_screen_at_time(time,video)
            if room == 'OG8':
                return 'OG8', time, time - dt
            
            X_time = time    
            while room != 'OH8':
                if time - X_time < 2000:
                    time = time + 200
                else:
                    time = time + dT
                room = get_screen_at_time(time,video)
            if time - X_time >= 2000:
                return room, time, time - dT



        # advance in 2 sec incriments looking for other rooms
        # if next room is OG8 then output OG8
        # if next room is not OG8 then output 


    # clean future room list
    if any('X-3' in future_room for future_room in future_rooms):
        future_rooms.remove('X-3')
    if any(previous_room in future_room for future_room in future_rooms):
        future_rooms.remove(previous_room)
    
    if verbose_mode:
        print('rooms_list_selection:', rooms_list_selection)

    if len(time_future) == 0 or count > 5:
        time = max(time_previous) + dT
        e_dT = dT
    else:
        time = (max(time_previous) + min(time_future))/2
        print(time)
        e_dT = time - max(time_previous)

    if verbose_mode:
        print('time: ', time)
    # check for end time
    if time > master_end_time:
        room = 'XXX'
        return room, time, max(time_previous)

    room = get_screen_at_time(time,video)
    if verbose_mode:
        print('room:', room)
    if room == next_room:
        return room, time, max(time_previous)
    elif room == previous_room:
        time_previous.append(time)
        return find_time_next_room_2(video,time_previous, time_future,dT,rooms_list_selection,master_end_time, time_resolution, verbose_mode, count)
    elif room == 'OH8':
        return room, time, max(time_previous)
    elif any(room in future_room for future_room in future_rooms):
        time_future.append(time)
        count = count + 1
        if count > 6:
            time_previous.append(time)
        return find_time_next_room_2(video,time_previous, time_future,dT,rooms_list_selection,master_end_time, time_resolution, verbose_mode, count)
    else:
        if next_room != 'OH8' and count < 6:
            count = count + 1
            #print('count:',count)
            num_bumps = math.floor(e_dT/time_resolution)
            if verbose_mode: 
                print(e_dT/time_resolution)
                print(e_dT % time_resolution == 0)
            if e_dT % time_resolution == 0:
                num_bumps = num_bumps - 1
            bump_times =[]
            for bump in range(1,num_bumps+1):
                bump_times.append(time + bump*time_resolution)
                bump_times.append(time - bump*time_resolution)
            if verbose_mode:

                print('bump times:' ,bump_times)
            for bump_time in bump_times:
                screen_bump = get_screen_at_time(bump_time,video)
                if verbose_mode:
                    print('bump screen: ', screen_bump, 'time', bump_time)
                if screen_bump == next_room:
                    return screen_bump, bump_time, max(time_previous)
                elif screen_bump == previous_room:
                    time_previous.append(bump_time)
                    return find_time_next_room_2(video,time_previous, time_future,dT,rooms_list_selection,master_end_time, time_resolution,verbose_mode, count)
                elif any(screen_bump in future_room for future_room in future_rooms):
                    time_future.append(bump_time)
                    return find_time_next_room_2(video,time_previous, time_future,dT,rooms_list_selection,master_end_time, time_resolution, verbose_mode, count)
                elif screen_bump == 'OH8':
                    return screen_bump, bump_time, max(time_previous)
            if len(bump_times) == 0 and len(time_future) > 0:
                time_future =[]
                future_rooms =[]
            else:
                time = max(bump_times)
            time_previous.append(time)
            return find_time_next_room_2(video,time_previous, time_future,dT,rooms_list_selection,master_end_time, time_resolution, verbose_mode, count)
        else:    
            time_previous.append(time)
            return find_time_next_room_2(video,time_previous, time_future,dT,rooms_list_selection,master_end_time, time_resolution, verbose_mode, count)
def find_time_next_room(video,known_time_in_room,dT,rooms_list_selection,master_end_time):
    current_room = rooms_list_selection[0]
    time = known_time_in_room
    next_room = rooms_list_selection[1]
    time = time + dT
    if time > master_end_time:
        room = 'XXX'
        return room, time
    room = get_screen_at_time(time,video)
    if room == current_room:
        return find_time_next_room(video,time,dT,rooms_list_selection,master_end_time)
    elif room == next_room:
        return room, time
    elif room == rooms_list_selection[2] or room == rooms_list_selection[3]: # if in a future room, reduce time until room found
        dT = -1* abs(dT)/2
        return find_time_next_room(video,time,dT,rooms_list_selection,master_end_time)
    elif room == 'OH8':
        return room, time
    else:
        #print(time)
        bump_time = time + 200
        test_room = get_screen_at_time(bump_time,video)
        #print('test room :', test_room)
        if test_room == next_room:
        #    print('a')
        #    print(test_room, bump_time)
            return test_room, bump_time
        elif test_room == current_room:
        #    print('b')
            return find_time_next_room(video,bump_time,dT,rooms_list_selection,master_end_time)
        elif test_room == rooms_list_selection[2] or test_room == rooms_list_selection[3]:
            dT = -1* abs(dT)/2
            if abs(dT) < 100:
                dT = -100
        #    print('c')
            return find_time_next_room(video,bump_time,dT,rooms_list_selection,master_end_time)
        else:
        #    print('d')
            return find_time_next_room(video,time,dT,rooms_list_selection,master_end_time)
def return_file_name_no_extension(full_path_filename):
    base=os.path.basename(full_path_filename)
    filename_no_ext = os.path.splitext(base)[0]
    return filename_no_ext

def convert_room_list(room_list):
    converted_room_list = []
    for room in room_list:
        converted_room = room[1:4]
        convert_room_list.append(convert_room)
    return convert_room_list

wall_start_time = time.time()

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True,
    help="path to the video image")
ap.add_argument("--room_list", required=False,
    help="path to room list csv file, defaults to double hundo")
ap.add_argument("--verbose", required=False,
    help="flag for more output", action="store_true")
ap.add_argument("-t", "--start", required=False,
    help="start time")
ap.add_argument("-i", "--init", required=False,
    help="initialize table?", action="store_true")
ap.add_argument("-d", "--delta", required=False,
    help="delta time")
ap.add_argument("-nosave", required=False,
    help="don't save", action="store_true")
ap.add_argument("-manual_mode", required=False,
    help="not forced by end room list", action="store_true")
ap.add_argument("-end", required=False,
    help="end_time")
ap.add_argument("-run", required=False,
    help="run number")

args = vars(ap.parse_args())
video = args["video"]
room_list_file = args["room_list"]
verbose = args["verbose"]
run_start_time = args["start"]
delta_time = args["delta"]
nosave = args["nosave"]
initialize_table = args["init"]
manual_mode = args["manual_mode"]
run_number = args["run"]


# run_end_time = args["end"]
# end_time_array = []
# end_time_array.append(run_end_time)
# set DT_t to default value if not set

# set default values
if delta_time is not None:
    DT_i = delta_time
else:
    DT_i = 3000

if run_number is not None:
    run_number = int(run_number)
else:
    run_number = 1

if start_time is None:
    start_time = 1


run_start_time = int(run_start_time)
vidcap = cv2.VideoCapture(video)  

filename = os.path.basename(video)
data_file = os.path.splitext(filename)[0] + '.db'

if nosave == False:
    con = lite.connect(data_file)
    if initialize_table:
        init_table(con)
else:
    con = False

# load room list, if a roomlist insn't provided, use 
if room_list_file is None:
    room_list_file = '../data/unique_room_list_double_hundo_with_index.csv'
room_list = convert_room_list(load_room_list(room_list_file))
unique_room_list = load_room_list(unique_room_list_file)


#start_time = run_start_time
#screen = get_screen_at_time(start_time,vidcap)
screen_list = []
time_list = []

if manual_mode == False:
    process_run(run_start_time, vidcap, DT_i, run_number, room_list, unique_room_list, 100,con)
else:
    start_time = float(run_start_time)
    screen = get_screen_at_time(start_time,vidcap)
    while start_time < run_end_time:
        screen_list.append(screen)
        time_list.append(start_time)
        new_screen, upper_bound_time = find_next_screen(screen, start_time, DT_i, vidcap)
        new_time, new_screen = find_time_room_switch(screen,new_screen,start_time,upper_bound_time,100,vidcap)
        print(new_screen , new_time)
        start_time = new_time
        screen = new_screen
        if screen == 'OH8':
            print_time_since_start(start_time,run_start_time)
    screen_list.append(screen)
    time_list.append(start_time)
    print(screen_list)
    print(time_list)
    csvfile = 'full_room_' + str(DT_i) + '.csv'
    data_export = np.column_stack((time_list, screen_list))
    with open(csvfile, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for item in data_export:
            writer.writerow(item)

#print('number of rooms:', len(time_list))
#print('number of valid rooms:', len(remove_blank_screens(screen_list)))
wall_end_time = time.time()
elapsed = wall_end_time - wall_start_time
print(elapsed)

#print(screen_list)

#csvfile = 'output_DT_' + str(DT_i) + '.csv'

# data_export = np.column_stack((time_list, screen_list))

# with open(csvfile, "w", newline='') as csv_file:
#     writer = csv.writer(csv_file, delimiter=',')
#     for item in data_export:
#         writer.writerow(item)

#print(time_list)
# initial screen