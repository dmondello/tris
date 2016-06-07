# Full Stack Nanodegree Project 4 Design a Game

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 Note: There are two versions in the folder "version_no_api" with my
 two versions og tris:
 - tris.py with a UI by shell
 - simply_tris without no UI
 
##Game Description:
Tris is a game for two players, who put X or 0 filling spaces in a 3×3 grid. 
Who succeeds in placing three symbols (X or 0) in a vertical, horizontal or diagonal row wins!
Each game can be retrieved or played by using the path parameter `urlsafe_game_key`.


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Score Keeping:
The score will be based on the highest net win to game ratio, which will be defined as (number of wins - number of losses) / (total of games).


##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name must correspond to an
    existing user - will raise a NotFoundException if not. 
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **cancel_game**

    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: Deletes game provided with key. Game must not have finished yet.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, board_position": "-,-,-,-,-,-,-,-,-" you have substituite "-" with "X" or "O" 
    - Returns: GameForm with new game state.
    - Description: Accepts numers to indicate the new board position from the top 
    left corner to the buttom right corner and returns the updated state of the game 
    and what Computer moves.
 
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player.
    Will raise a NotFoundException if the User does not exist.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 -  **get_game_history**

    - **Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage containing history
    - Description: Returns the move history of a game inside the board    
    
 - **get_active_game_count**
    - Path: 'games/average_moves_per_game'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of moves madefor all finished games from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name, (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
 
