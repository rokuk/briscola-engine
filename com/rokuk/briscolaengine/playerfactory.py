import logging


# Used to keep track of last id, used in player init method
lastid = 0


# Player class
# Contains player id and current cards of the player
class Player:

    # Initalizes id and card variables
    # and registers the player in the game instance
    def __init__(self, game):
        global lastid
        self.id = lastid
        self.cards = []
        self.woncards = []
        self.wonpoints = []

        lastid += 1
        game.registerplayer(self)

    # Adds the card passed as argument to the self.card list
    def addcard(self, card):
        logging.debug("Adding card: " + card.type + str(card.strength) + " to player: " + str(self.id))
        card.ownerid = self.id
        self.cards.append(card)

    # Removes the card passed as argument from the card list.
    # Called when playing the card.
    def removecard(self, card):
        logging.debug("Removing card: " + card.type + str(card.strength) + " from player: " + str(self.id))
        self.cards.remove(card)

    # Append cards to player's won cards list.
    # Called at the end of a round, if the player has won.
    def appendcards(self, cards):
        self.woncards.append(cards)

    # Append points to player's won points list.
    # Called at the end of a round, if the player has won.
    def appendpoints(self, points):
        self.wonpoints.append(points)


# Initializes the number of players to register for the game instance passed as an argument
# and returns the list of player objects. Also passes the game instance to the player.
def init(game):
    playerlist = []

    for i in range(0, game.playercount):
        playerlist.append(Player(game))

    return playerlist
