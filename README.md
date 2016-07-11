# Tic-Tac-Toe Back End

## Description:
##### Tic-Tac-Toe back end written in Python and running on Google App Engine
Tic-Tac-Toe is a two player game, which is played on a 3x3 grid.  
One player has the X-Token and the other one has the O-Token.  
The player who places three tokens in a horizontal, vertical or diagonal row, wins.


## Set-Up Instructions:
1. Update the value of application in app.yaml to the app ID you have registered in the App Engine admin console and would like to use to host your instance of this sample.
2. Run the app with the devserver using dev_appserver.py DIR, and ensure it's running by visiting the API Explorer - by default location:8080/_ah/api/explorer.
3. (Optional) Generate your client library(ies) with the endpoints tool. Deploy your application.

## Files Included:
- api.py: Contains endpoints and game playing logic.
- app.yaml: App configuration.
- cron.yaml: Conjob configuration.
- main.py: Handler for taskqueue handler.
- models.py: Entity and message definitions including helper methods.
- utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

## Api Endpoints:

- **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique.   
    Will raise a ConflictException if a User with that user_name already exists.
    
- **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: player_one_name, player_two_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. player_one_name and player_two_name must correspond to an existing user  - will raise a NotFoundException if not.
    
- **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
- **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, player_name, x, y
    - Returns: GameForm with new game state.
    - Description: Accepts the players name and the coordinates of the board 
    
- **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm with new game state.
    - Description: Cancels an active game.

- **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: player_name
    - Returns: ActiveGameForm with a list of urlsafe_game_key.
    - Description: Returns a list of active games of the given user.

- **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: 
    - Returns: UserRankingsForm with a list of player names ordered by the number of won games.
    - Description: Returns the ranking of all players ordered by the number of won games.

- **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameMoveHistoryForm with a list of played moves.
    - Description: Returns a list of the played game moves of the given game.
 
## Models Included:
- **User**
    - Stores unique user_name and (optional) email address.
    
- **GameState**
    - The state of a game

- **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
## Forms Included:
- **GameForm**
    - Representation of a Game's state (urlsafe_key, player_one_name, player_two_name, board, game_state, message).
    
- **NewGameForm**
    - Used to create a new game (player_one_name, player_two_name).
    
- **MakeMoveForm**
    - Inbound make move form (player_name, x, y).

- **ActiveGamesForm**
    - Representation of the active games of the given player (games).

- **GameHistoryForm**
    - Representation of the move history of the given game (histories).

- **UserRankingsForm**
    - Representation of the rankings of all users.
    
- **StringMessage**
    - General purpose String container.