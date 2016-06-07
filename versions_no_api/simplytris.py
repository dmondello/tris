import random

def get_input(turn):
    valid = False
    while not valid:
        try:
            user = raw_input("Where would you like to place X (1-9)? ")
            user = int(user)
            if user >= 1 and user <= 9:
                return user-1
            else:
                print "That is not a valid move! Please try again.\n"
            # print_instructions()
        except Exception as e:
            print user + " is not a valid move! Please try again.\n"
            # print_instructions()


def check_win(board):
    win_cond = ((1, 2, 3), (4, 5, 6), (7, 8, 9), (1, 4, 7), (2, 5, 8), (3, 6, 9), (1, 5, 9), (3, 5, 7))
    for each in win_cond:
        try:
            if board[each[0]-1] == board[each[1]-1] and board[each[1]-1] == board[each[2]-1]:
                return board[each[0]-1]
        except:
            pass
    return -1


def quit_game(board, msg):
    #print_board(board)
    print msg
    quit()


def main():
    # setup game
    #  alternate turns
    #  check if win or end
    #  quit and show the board
    #  print_instructions()
    board = []
    for i in range(9):
        board.append(-1)
    game_over = False
    move = 0
    # print board;


    while not game_over:
        #print_board(board)
        # print "Turn Player " + str(move + 1)
        if move % 2 == 0:
            # print board;
            print "You Turn"
            turn = 'X'
            user = get_input(turn)
            while board[user] != -1:
                print "Invalid move! Cell already taken. Please try again.\n"
                user = get_input(turn)
        else:
            print "Turn Player 0"
            turn = 'O'
            # get user input
            user = random.randrange(1, 9, 1)
            while board[user] != -1:
                # print "Invalid move! Cell already taken. Please try again.\n"
                user = random.randrange(1, 9, 1)
        board[user] = 1 \
            if turn == 'X' \
            else 0
        # advance move and check for end game
        move += 1

        if move > 4:
            winner = check_win(board)
            if winner != -1:
                out = "The winner is "
                out += "X" \
            if winner == 1 else "O"
                out += " :)"
                quit_game(board, out)
            elif move == 9:
                quit_game(board, "No winner :(")
if __name__ == "__main__":
    main()
