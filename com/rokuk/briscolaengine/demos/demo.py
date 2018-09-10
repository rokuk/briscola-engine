import com.rokuk.briscolaengine.briscolaengine as be


def roundend(instance):
    pass


def gameend(instance):
    pass


def play(instance, player):
    instance.playcard(player, player.cards[0])


game = be.Game(2, play, roundend, gameend)
game.start()
