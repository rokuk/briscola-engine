import logging
import itertools
from random import *
import cards, playerfactory


# Setup logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


# Main game class
class Game:

    # Initialize class
    # with playercount argument, which should be an int of players to generate,
    # playcallback argument, providing the play function
    # roundendcallback argument, providing the roundend function
    # gameendcallback argument, providing the gameend function
    def __init__(self, playercount, playcallback, roundendcallback, gameendcallback):
        self.playercount = playercount
        self.playcallback = playcallback
        self.roundendcallback = roundendcallback
        self.gameendcallback = gameendcallback
        self.trump = cards.Card(0, 0, 0)
        self.players = []
        self.deck = []
        self.playedcards = []
        self.roundscores = []
        self.gamescores = []
        self.endscores = []
        self.finished = False
        self.round = 0
        self.turn = 0

    # Game setup method
    # Resets instance variables, generates card deck,
    # initializes players and deals first three cards.
    # Should be called to start a new game.
    # All previous game variables will be reset!
    def start(self):
        logging.info("Initializing a new game:")
        logging.debug("Parameters:")
        logging.debug("playercount=" + str(self.playercount))

        # Reset variables
        self.finished = False
        self.gamescores = []
        self.endscores = []
        self.round = 0

        # Generates a full deck of 40 cards
        logging.debug("Generating deck...")
        self.deck = cards.generatedeck()

        # Initializes players and sets up the player event system
        logging.debug("Generating players...")
        playerfactory.init(self)

        logging.debug("Randomizing player turn...")
        self.turn = randint(0, len(self.players) - 1)
        logging.debug("Player turn: " + str(self.turn))

        # Calls dealcards() 3 times to deal out first cards
        logging.debug("Dealing cards...")
        for _ in range(3):
            self.dealcards()

        # Set trump and add the card to the end of the deck
        logging.debug("Setting trump...")
        self.trump = self.deck.pop()
        self.deck.insert(0, self.trump)
        logging.info("Trump is: " + self.trump.type + str(self.trump.strength))

        logging.info("Setup done!")
        logging.debug("----------------------------")
        logging.info("Starting game.")

        # Game loop
        # Ends when self.finished is True (when there are no more cards to deal)
        while not self.finished:

            # Reset played cards variable from previous round and increment round variable
            self.playedcards = []
            self.roundscores = []
            self.round += 1
            scoresum = 0

            logging.info("Starting round: " + str(self.round))

            # Send a play event to every registered player, prompting them to play a card.
            # Events are fired starting with the player whose turn it is, incrementing to
            # the number of all players, and then starting from 0 to the player whose turn it is.
            logging.debug("Sending play event to players...")
            for playerid in itertools.chain(
                    range(self.turn, len(self.players)),
                    range(self.turn)):
                self.playcallback(self, self.players[playerid])

            # Get the winning card from played cards
            wincard = getwincard(self.playedcards, self.trump)

            # Get the owner of the winning cards
            roundwinner = self.players[wincard.ownerid]
            logging.info("Winner of round " + str(self.round) + " is player " + str(roundwinner.id))

            # Give the winning player cards played in the round
            logging.debug("Giving player: " + str(roundwinner.id) + " won cards...")
            roundwinner.appendcards(self.playedcards)

            logging.debug("Calculating round score...")

            # Add up all the scores
            scoresum = sum(playedcard.value for playedcard in self.playedcards)

            logging.debug("Player %s won %s points.", roundwinner.id, scoresum)

            # Append score sum to the winning player and append 0 to other players
            # Append same values to roundscore list
            for player in self.players:
                if player.id == roundwinner.id:
                    player.appendpoints(scoresum)
                    self.roundscores.append(scoresum)
                else:
                    player.appendpoints(0)
                    self.roundscores.append(0)

            # Append the roundscores list to gamescores
            self.gamescores.append(self.roundscores)

            # Send round end event
            logging.debug("Sending roundend event...")
            self.roundendcallback(self)

            # Set the turn to the winning card's owner
            self.turn = wincard.ownerid

            # Check for game end
            # TODO Fix (Not very reliable)
            if len(self.players[0].cards) == 0:
                self.finished = True
                logging.debug("Detected no more cards, finishing game.")
                break

            # Give everyone a card for the next round if there are any cards left
            if len(self.deck) != 0:
                logging.debug("Dealing cards for round: " + str(self.round + 1))
                self.dealcards()

            logging.debug("End of round %s", self.round)

        logging.info("Game finished!")

        # Calculate game scores
        logging.debug("Calculating scores...")

        for playerid in range(len(self.players)):
            logging.debug("Player %s won %s", playerid, self.players[playerid].wonpoints)

            playerscore = sum(self.players[playerid].wonpoints)

            self.endscores.append(playerscore)
            logging.info("Player %s won %s points", playerid, playerscore)

        # Send game end event
        logging.debug("Sending game end event...")
        self.gameendcallback(self)

        logging.debug("Game loop ended.")

    # Registers the player instance given as argument
    # Appends the player to the list of players,
    # which is used to deliver playcard() events
    def registerplayer(self, player):
        self.players.append(player)

        logging.debug("Registered player: " + str(player.id))

    # Plays a card from players cards if it's the players turn
    def playcard(self, player, card):
        logging.info("Player " + str(player.id) + " played card: " + card.type + str(card.strength))

        player.removecard(card)
        self.playedcards.append(card)

    # Sets the self.finished variable to passed value
    def setfinished(self, value):
        self.finished = value

    # Deals the cards to all registered players,
    # starting with the player whose turn it is.
    # The dealt cards are removed from the deck and set an owner.
    # The nuber of dealt cards is then compared to the nuber of players.
    # If it's not the same an error is raised.
    def dealcards(self):
        count = 0

        for playerid in itertools.chain(range(self.turn, len(self.players)), range(self.turn)):
            player = self.players[playerid]
            card = self.deck.pop()
            player.addcard(card)
            count += 1

        if count != len(self.players):
            logging.error("Something went wrong while dealing cards: "
                          "dealt: " + str(count) + " players: " + str(len(self.players)))


# Returns the winning card from all played cards and trump
def getwincard(playedcards, trump):
    logging.debug("Checking for winning card...")

    # Create a foo card to compare the first checked card and later keep track of the best card.
    bestcard = playedcards[0]
    logging.debug("Setting bestcard to: " + bestcard.type + str(bestcard.strength) + ", because it's the first.")

    # Check every card played in order and identify the winning card.
    for cardid in range(1, len(playedcards)):
        logging.debug("Starting card check loop: " + str(cardid))

        # Get the card from playedcards list by the index it was played.
        card = playedcards[cardid]

        # Logging stuff
        logging.debug("Card is: " + card.type + str(card.strength))
        if bestcard != 0:
            logging.debug("Bestcard is: " + bestcard.type + str(bestcard.strength))
        else:
            logging.debug("Bestcard is: nil")
            logging.debug("Trump is: " + trump.type + str(trump.strength))

        # Check if the trump was played.
        if card.type == trump.type:
            logging.debug("Card is same type as trump.")

            # Check if bestcard is the same type as trump.
            if bestcard.type == trump.type:
                logging.debug("Bestcard is same type as trump.")

                # Check if card trump is higher than the bestcard trump, if yes, set card as best.
                if card.strength > bestcard.strength:
                    bestcard = card
                    logging.debug("Card is higher than bestcard.")

            # Bestcard is not the same type as trump, therefore card is the bestcard.
            else:
                bestcard = card
                logging.debug("Best card is not the same type as trump, therefore card is best card.")

        # The trump card was not played.
        # Check if card is the same type as the first card.
        elif card.type == playedcards[0].type:
            logging.debug("Card is same type as first card.")

            # Check if card strength is higher than first card's strength.
            if card.strength > playedcards[0].strength:
                logging.debug("Card is higher than first card.")

                # Check if cards strength is higher than the bestcard's strength, if yes, set card as best.
                if card.strength > bestcard.strength:
                    bestcard = card
                    logging.debug("Card is same higher than bestcard.")

    logging.debug("Winning card is: " + bestcard.type + str(bestcard.strength))

    return bestcard
