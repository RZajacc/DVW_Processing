def clear_scout_file(filename, path_out, suffix=''):
    """
    Method cleares scout file off some data that could make rescouting take longer. It removes
    directions pointed by mouse position in DataVolley (but zones information), and all custom
    codes added by other scouts. It creates new scout file (no changes in place). Method will
    keep the original name so if you decide to save in the same location it actually will 
    overwrite the original file. If you want to save in the same location, and keep both you 
    can use suffix argument. Suffix will be added to resulting file name.
    
    Parameters
    ----------
    filename : str
        Name of .dvw file to be processed
    path_out : str
        Path to the location you want to store updated file
    suffix : str
        Optional parameter. By default its emtpy string. If changed
        to different value it will be added at the end of resulting 
        file name
    """
    
    #Read a file and create output file data as list
    dvvIn = [line.rstrip() for line in open(filename)]
    dvvOut = []
    
    # Loop through lines of file
    for nrow, line in enumerate(dvvIn):
        
        # Select only lines with players actions (main code)
        if line.count(';') == 26 and line[1:3].isnumeric():

            # Divide line into parts (file is ; separated)
            line_list = line.split(';')

            # Check if there is custom code around main element and if yes delete it
            # Custom codes are written to main code from position 15-20
            if len(line_list[0])>15:
                
                # DV fills empty spaces with '~' so after deleting custom code you want to delete them as well
                for ind in range(14,0,-1):
                    
                    # So you loop back to last point holding relevant information (not '~')
                    if line_list[0][ind] != '~':
                        
                        # Save data untill this point as main code to scout data again
                        line_list[0] = line_list[0][:ind+1]
                        break

            #Remove unwanted attack and block part
            if line_list[0][3] == 'A' and len(line_list[0])>13:
                line_list[0] = line_list[0][:13]
            elif line_list[0][3] == 'B' and len(line_list[0])>11:
                line_list[0] = line_list[0][:11]
            
            #------------------------------------------------------------------
            #CHANGE SET AND DEFENSE INDICATION TEST IN TRIAL PHASE
            # STILL IN TEST

            #1. Get the next row first
            next_line = dvvIn[nrow+1]
            next_line_list = next_line.split(';')
            
            #2 Check conditions (first if there is a spike, then if same team)
            if line_list[0][3] == 'E' and line_list[0][5] != '+' and next_line_list[0][3] == 'A':
                
                # Make a list of letters to manage changes easier 
                l_lst = list(line_list[0])
                
                # Check if both set and spike is performed by the same team, otherwise change is not welcome
                if line_list[0][0] == '*' and next_line_list[0][0] == '*':
                    l_lst[5] = '+'
                elif line_list[0][0] == 'a' and next_line_list[0][0] == 'a':
                    l_lst[5] = '+'
                
                # Join into string again
                l_lst_upd = ''.join(l_lst)
                
                # Replace string in original place
                line_list[0] = l_lst_upd
                
            # #3 Check conditions (first if there is a set, then if same team)
            # if line_list[0][3] == 'D' and line_list[0][5] != '+' and next_line_list[0][3] == 'E':
                
            #     print(line_list[0])

            #     # Make a list of letters to manage changes easier 
            #     l_lst = list(line_list[0])
                
            #     # Check if both set and spike is performed by the same team, otherwise change is not welcome
            #     if line_list[0][0] == '*' and next_line_list[0][0] == '*':
            #         l_lst[5] = '+'
            #     elif line_list[0][0] == 'a' and next_line_list[0][0] == 'a':
            #         l_lst[5] = '+'
                
            #     # Join into string again
            #     l_lst_upd = ''.join(l_lst)
                
            #     # Replace string in original place
            #     line_list[0] = l_lst_upd
            #--------------------------------------------------------------------

            # This part deletes indications made with mouse in DV4. They are saved as data on pos 4-6
            for ind in range(4,7):
                
                # If element in the list is not empty string, change it to empty string
                if line_list[ind] != '':
                    
                    # It will delete arrow selection in DV4
                    line_list[ind] = ''
            
            # Form line of data valid for DV4 again (';' separated values)
            line_new = ';'.join(line_list)
            
            # Append data to resulting file
            dvvOut.append(line_new)
        
        # Applies to any other kind of lines that is analysed previously. Basically rewrites all file
        else:
            dvvOut.append(line)
    
    # Some scouts use '.' in filenames so to extract name its safer to cut extension...
    f_name = filename[:-4]
    f_ext = filename[-4:]
    
    # Creating output file
    fileOut = open(path_out+f_name+suffix+f_ext, 'w')
    
    # Writing new content to the file
    for line in dvvOut:
        fileOut.write(line + '\n')
    
    fileOut.close()



def assign_game_phases(filename, path_out, suffix=''):
    """
    Method assignes custom codes to service information. It consists of 3 basic parts of information.
    First two symbols defines numbers of serve in a row (for example S1, S2, and so on). Next 2 symbols
    defines game phase (for example P1, P2, P3), and last symbol informs about score (for example C, W, L).
    So code 'S1P1C' would mean that player serves first time (S1), game is still in phase 1 (P1), and score difference
    between both teams is not bigger than 3pts (C)
    
    Possible codes for each element:
    1st part - its just counter so 'S' is always there and just means its Service and number is serve count
    
    2nd part - Phase 1 (P1) - is a part of game untill BOTH teams reach at least 8pts (tie-break 5)
               Phase 2 (P2) - Both teams are over 8 pts. Phase last untill both teams have at least 18 pts (tie-break 10)
               Phase 3 (P3) - Both teams are over 18 pts (tie-break over 10)
               
    3rd part - C - 'Concact' - Difference between teams score is lower or equal to 3 pts
               W - 'Winning' - Serving team has more than 3 pts advantage
               L - 'Losing'  - Serving team is more than 3 pts behind other team

    Parameters
    ----------
    filename : str
        Name of .dvw file to be processed
    path_out : str
        Path to the location you want to store updated file
    suffix : str
        Optional parameter. By default its emtpy string. If changed
        to different value it will be added at the end of resulting 
        file name
    """
        
    #Read a file
    dvvIn = [line.rstrip() for line in open(filename)]
    dvvOut = []

    # Information about player performing last serve (it starts with empty and is updated later) and counters
    Player = ''
    
    # Counter for serves in a row by same player. By default 1
    counter = 1
    
    # Score of both teams 
    h_Team_Score = 0
    a_Team_Score = 0 
    
    # Set currently played (5th set has different rules therefore its important information)
    set_count = 1

    # Loop over lines of file
    for row in dvvIn:

        # Check if new set has begun (** begins the code ending set)
        if row[:2] == '**':
            set_count += 1
            Player = ''
            counter = 1
            h_Team_Score = 0
            a_Team_Score = 0
        
         
        # Game part have exactly 26 commas so if its not this just rewrite content
        if row.count(';') != 26:
            
            # Rewrite content
            dvvOut.append(row)

        # If in game part check if its score information part and if yes pass it to a function
        if row.count(';') == 26 and (row[2:4].isnumeric() and row[5:7].isnumeric() and row[1] != "c") :
            h_Team_Score = int(row[2:4])
            a_Team_Score = int(row[5:7])
        
        # If it is serve perform all other operations
        if row.count(';') == 26 and row[1:3].isnumeric() and row[3] == 'S':
            
           
            # Check if same player is on serve and increment counter if yes
            if Player == row[:3]:
                counter +=1
            else:
                counter = 1

            # Update player information
            Player = row[:3]
            
            # First part of the custom code including service and its count
            counterPart = 'S' + str(counter)
            
            # Second part of custom code including game phase
            phasePart = get_phase_part(set_count, h_Team_Score, a_Team_Score)
            
            # Get symbol indicating if team is home or away
            t_symbol = row[0]
            
            # Third part of custom code including score relationship
            scorePart = get_score_part(t_symbol, h_Team_Score, a_Team_Score)
            
            # Build a final string that will be added to scoutfile
            message = counterPart + phasePart + scorePart

            # find first occurence of ';' and add placeholders if its less than 20
            pos = row.find(';')
            placeholder = '~'

            #All positions before 15 must be filled with placeholder in order for it to work in DV4
            if pos < 20 and row[15] == ';':
                
                # Define number of placeholders to add 
                diff = 15 - pos
                
                # Update message to contain appropriate number of placeholders
                message2 = diff * placeholder + message + ';'
                
                # Update content of a scout file
                row = row.replace(row[pos], message2, 1)
            
            # If there was a custom code before just replace it
            elif pos == 20:
                row = row.replace(row[15:20], message)

            # Append row in final form
            dvvOut.append(row)
        
        # If it is serve perform all other operations
        if row.count(';') == 26 and row[3] != 'S':
            dvvOut.append(row)

    # Some scouts use '.' in filenames so to extract name its safer to cut extension...
    f_name = filename[:-4]
    f_ext = filename[-4:]
    
    # Creating output file
    fileOut = open(path_out+f_name+suffix+f_ext, 'w')
    
    for line in dvvOut:
        fileOut.write(line + '\n')

    fileOut.close()


def get_phase_part(set_count, h_Team_Score, a_Team_Score):
    """
    Function returning phase part out of scout file
    
    Parameters
    ----------
    set_count : int
        Current set count
    h_Team_score : int
        Home team score
    a_Team_score : int
        Away team score
        
    Returns
    -------
    String
        String indicating set phase
    """
    
    # First four sets have different criteria than 5th
    if set_count < 5:
        if h_Team_Score < 8 or a_Team_Score < 8 :
            return 'P1'
        elif (h_Team_Score >= 8 and a_Team_Score >= 8) and not (h_Team_Score >=18 and a_Team_Score >=18) :
            return 'P2'
        else:
            return 'P3'

    # Phases rules for tie-break
    else:
        if h_Team_Score < 5 or a_Team_Score < 5 :
            return 'P1'
        elif (h_Team_Score >= 5 and a_Team_Score >= 5) and not (h_Team_Score >=10 and a_Team_Score >=10) :
            return 'P2'
        else:
            return 'P3'

def get_score_part(t_symbol, h_Team_Score, a_Team_Score):
    """
    Function returning phase part out of scout file
    
    Parameters
    ----------
    t_symbol : str
        Symbol indicating home ('*') or away ('a') team
    h_Team_score : int
        Home team score
    a_Team_score : int
        Away team score
        
    Returns
    -------
    String
        String indicating score relationship between teams
    """
    
    # Comparison must be made to current team on serve, so home or away
    if t_symbol == '*':
        if abs(h_Team_Score - a_Team_Score) <= 3:
            return 'C'
        elif abs(h_Team_Score - a_Team_Score) >= 3:
            if h_Team_Score > a_Team_Score:
                return 'W'
            else:
                return 'L'

    # Comparison must be made to current team on serve, so home or away
    if t_symbol == 'a':
        if abs(h_Team_Score - a_Team_Score) <= 3:
            return 'C'
        elif abs(h_Team_Score - a_Team_Score) >= 3:
            if h_Team_Score > a_Team_Score:
                return 'L'
            else:
                return 'W'


def change_video_path(filename, path_out, dir_new, suffix=''):
    """
    This function replace video paths in Data Volley 4 scout files (dvw) 
    to desired new ones and places changed files in folders desired for coaches.
    Keep in mind that folders has to be created manually in order to run. 
    
    Parameters
    ----------
    filename : str
        Name of .dvw file to be processed
    path_out : str
        Path to the location you want to store updated file
    dir_new : str
        Directory on drive to which you want to change your path into
    suffix : str
        Optional parameter. By default its emtpy string. If changed
        to different value it will be added at the end of resulting 
        file name
    """     
    
    # Open file from path
    file_in = open(filename, 'r')

    # Save each line to a list and delete new line key at the end
    file_data = [line.rstrip() for line in file_in]

    # Index of section containing video path
    section_ind = file_data.index('[3VIDEO]')

    # Video path is stored next line to section header
    vid_path = file_data[section_ind+1] 

    # Divide path into prefix ('Camera0') and file path
    vid_split = vid_path.split('=')

    # Divide video path into segments
    path_split = vid_split[1].split('\\')

    # Video name and format is last element in the path
    vid_name = path_split[-1]

    # Build new file path
    path_new = dir_new + vid_name

    # Replace paths in original file (prefix + '=' + file name)
    file_data[section_ind+1] = vid_split[0] + '=' + path_new

    # Split file name to add suffix for coach
    fname_split = filename.split('.')

    # Create new file with suffix in name 
    file_out = open(path_out + fname_split[0] + suffix + '.' + fname_split[1], 'w')

    # Write content to file
    for line in file_data:
        file_out.write(line + '\n')

    # Close files
    file_out.close()
    file_in.close()