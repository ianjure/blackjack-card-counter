def getCount(card):
    rank = ""

    if len(card) == 2:
        rank = card[0] # -- 2 3 4 5 6 7 8 9
        if rank == "A":
            rank = "14" # -- ACE
        elif rank == "K": # -- KING
            rank = "13"
        elif rank == "Q": # -- QUEEN
            rank = "12"
        elif rank == "J": # -- JACK
            rank = "11"
    else:
        rank = card[0:2] # -- 10
    
    rank = int(rank)

    if rank <= 6: # -- 2 3 4 5 6
        return 1
    elif (rank >= 7) and (rank <= 9): # -- 7 8 9
        return 0
    else: # -- 10 J Q K A
        return -1
    
    
