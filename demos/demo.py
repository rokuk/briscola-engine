# Should be executed from parent directory of 'demos' folder (briscola-engine)

import sys
sys.path.append('src')

import briscolaengine as be


def roundend(instance):
    pass


def gameend(instance):
    pass


def play(instance, player):
    instance.playcard(player, player.cards[0]) # za demonstracijo vsak igralec igra s prvo karto, ki je na voljo


if __name__ == "__main__":
    game = be.Game(2, play, roundend, gameend)
    game.start()
