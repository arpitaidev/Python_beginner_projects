import random
import time
import os
from groq import Groq

# Setting up the API key
api_key = os.environ.get("GROQ_API_KEY")
if api_key:
    print("API Key found! We are good to go.\n")
else:
    print("API Key NOT found! The smart computer might crash.\n")

# Initialize the Groq client
client = Groq()

def print_board(board):
    """Prints the current state of the board."""
    print("\n")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print("\n")

def check_win(board, player):
    """Checks if the given player has won."""
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columns
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] == player:
            return True
    return False

def get_smart_move(board):
    """Calls the Groq API to decide the best move for 'O'"""
    # Find empty spots so we can tell the AI what's available
    available_spots = []
    for i in range(len(board)):
        if board[i] == " ":
            available_spots.append(str(i + 1))
            
    # I made a string representation of the board to send to the AI
    board_status = f"""
     {board[0] or '1'} | {board[1] or '2'} | {board[2] or '3'} 
    ---+---+---
     {board[3] or '4'} | {board[4] or '5'} | {board[5] or '6'} 
    ---+---+---
     {board[6] or '7'} | {board[7] or '8'} | {board[8] or '9'} 
    """
    
    # Giving the AI instructions
    prompt = f"""
    You are playing Tic Tac Toe as 'O'.
    The current board looks like this:
    {board_status}
    
    The available spots are: {', '.join(available_spots)}
    
    Look at the board and decide the best move to either win or block 'X'.
    Reply with ONLY the number of the spot you want to play. Do not say any other words. Just the number.
    """
    
    try:
        # Request to Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-120b",
            temperature=0.5,
        )
        
        # Getting the response string
        reply = chat_completion.choices[0].message.content.strip()
        
        # Convert to an integer and adjust for our 0-indexed list
        move = int(reply) - 1
        
        # Check if the AI tried to cheat or pick a taken spot
        if move >= 0 and move <= 8 and board[move] == " ":
            return move
        else:
            print("AI picked an invalid spot. Falling back to random...")
            # returns a random spot instead
            return random.choice([i for i, spot in enumerate(board) if spot == " "])
            
    except Exception as e:
        # If the API fails or gives us text instead of a number, just pick random so it doesn't crash
        print("AI got confused. Falling back to random...")
        return random.choice([i for i, spot in enumerate(board) if spot == " "])

def play_game(mode):
    """Main game loop for Player vs Computer."""
    board = [" " for _ in range(9)]
    human = "X"
    computer = "O"
    current_player = human     # I go first
    
    print("\nStarting game...")
    print("Use numbers 1-9 to place your move on the board:")
    print(" 1 | 2 | 3 \n---+---+---\n 4 | 5 | 6 \n---+---+---\n 7 | 8 | 9 ")

    while True:
        print_board(board)
        
        # 1. HUMAN TURN
        if current_player == human:
            try:
                move = int(input("Your turn! Choose a spot (1-9): ")) - 1
            except ValueError:
                print("Invalid input! Please enter a number between 1 and 9.")
                continue
                
            if move < 0 or move > 8:
                print("Out of bounds! Please pick a number from 1 to 9.")
                continue
            if board[move] != " ":
                print("That spot is already taken! Try again.")
                continue
                
        # 2. COMPUTER TURN
        else:
            print("Computer is thinking...")
            time.sleep(1) 
            
            if mode == "normal":
                # Random normal computer move
                available_spots = [i for i, spot in enumerate(board) if spot == " "]
                move = random.choice(available_spots)
            elif mode == "smart":
                # Smart computer move using Groq
                move = get_smart_move(board)
                
            print(f"Computer chooses spot {move + 1}")
            
        # 3. Update the board
        board[move] = current_player
        
        # 4. Check for a win
        if check_win(board, current_player):
            print_board(board)
            if current_player == human:
                print(" You win! ")
            else:
                print("The Computer wins! ")
            break
            
        # 5. Check for a tie
        if " " not in board:
            print_board(board)
            print("It's a tie!")
            break
            
        # 6. Switch players
        if current_player == human:
            current_player = computer
        else:
            current_player = human


# menu selection to select which mode to play 
def main_menu():
    while True:
        print("\n=== TIC TAC TOE MENU ===")
        print("1. Play vs Normal Computer (Random Moves)")
        print("2. Play vs Smart Computer (Intelligent)")
        print("3. Exit Game")
        
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == "1":
            play_game(mode="normal")
        elif choice == "2":
            play_game(mode="smart")
        elif choice == "3":
            print("Thanks for playing! Bye!")
            break
        else:
            print("Invalid choice. Please type 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()
