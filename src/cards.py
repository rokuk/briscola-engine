import random
import logging


# Variable definitions for cards
strengths = [2, 10, 4, 5, 6, 7, 11, 12, 13, 14]
values = [0, 10, 0, 0, 0, 0, 2, 3, 4, 11]
types = ['S', 'C', 'B', 'D']
cardcount = len(types) * len(strengths)


# Class for a card
class Card:
    def __init__(self, type, strength, value):
        self.type = type
        self.strength = strength
        self.value = value
        self.ownerid = -1


# Generates all possible permutations of cards
# and returns a list of all cards
def getallcards():
    cards = []

    for type in types:
        for strength in strengths:
            cards.append(Card(type, strength, values[strengths.index(strength)]))

    return cards


# Generates a random deck of cards and returns it.
def generatedeck():
    logging.debug("Generating a random deck...")

    deck = []

    # Get a list of all possible cards.
    possiblecards = getallcards()

    # While the length of the deck is smaller than the nuber of all cards,
    # chooses a card from a list of possible cards. The card is appended
    # to the deck and removed from the list of possible cards.
    while len(deck) < cardcount:
        card = possiblecards[random.randint(0, len(possiblecards)-1)]
        deck.append(card)
        possiblecards.remove(card)

    return deck
