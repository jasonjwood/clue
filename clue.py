import csv

players = {}
my_name = ''
solution = {}

# Initialize knowledge store
cards = {'draco': {'type': 'suspect', 'knowledge': {}},
         'crabbe': {'type': 'suspect', 'knowledge': {}},
         'lucius': {'type': 'suspect', 'knowledge': {}},
         'umbridge': {'type': 'suspect', 'knowledge': {}},
         'pettigrew': {'type': 'suspect', 'knowledge': {}},
         'bellatrix': {'type': 'suspect', 'knowledge': {}},
         'draught': {'type': 'weapon', 'knowledge': {}},
         'cabinet': {'type': 'weapon', 'knowledge': {}},
         'portkey': {'type': 'weapon', 'knowledge': {}},
         'impedimenta': {'type': 'weapon', 'knowledge': {}},
         'petrificus': {'type': 'weapon', 'knowledge': {}},
         'mandrake': {'type': 'weapon', 'knowledge': {}},
         'hall': {'type': 'location', 'knowledge': {}},
         'hospital': {'type': 'location', 'knowledge': {}},
         'ror': {'type': 'location', 'knowledge': {}},
         'potions': {'type': 'location', 'knowledge': {}},
         'trophy': {'type': 'location', 'knowledge': {}},
         'divination': {'type': 'location', 'knowledge': {}},
         'owlery': {'type': 'location', 'knowledge': {}},
         'library': {'type': 'location', 'knowledge': {}},
         'doda': {'type': 'location', 'knowledge': {}},
         }


def add_card_to_knowledge(card, player, knowledge_type):
    print('We now know that ' + player + ' ' + knowledge_type + ' ' + card)
    cards[card]['knowledge'][player] = knowledge_type

    for other in players:
        if other['name'] != player:
            cards[card]['knowledge'][other] = 'cannot_have'


def does_player_hold_card(card, player):
    return cards[card]['knowledge'][player] == 'has'


def could_player_hold_card(card, player):
    # Return no if the player specifically can't have that card
    if cards[card]['knowledge'][player] == 'cannot_have':
        return False

    return True


def main():
    # Read csv file representing player names
    global players
    with open('players.txt', mode='r') as players_txt:
        previous_name = ''
        first_name = ''
        for player in players_txt:
            name = player.rstrip('\n')

            if first_name is None:
                first_name = name

            players[name] = {'name':name, 'next_player':''}

            if previous_name is not None:
                players[previous_name]['next_player'] = name

            previous_name = name

        players[previous_name]['next_player'] = first_name




    print('Players: ')
    print(players)

    # Read my cards and update knowledge
    global my_name
    with open('mycards.txt', mode='r') as my_cards_txt:
        for card in my_cards_txt:
            card = card.rstrip('\n')
            # first row is my name
            if my_name == '': 
                my_name = card
            else:
                add_card_to_knowledge(card, my_name, 'has')

    print('Cards:')
    print(cards)

    # Read csv file representing guesses, building knowledge as we go
    with open('guesses.csv', mode='r') as guesses_csv:
        guess_reader = csv.DictReader(guesses_csv)
        for guess in guess_reader:
            print('Guess: ')
            print(guess)

            # If we know which card was shown and who showed it, then add that to knowledge
            if 'card_shown' in guess:
                print('We just saw a card')
                add_card_to_knowledge(guess['card_shown'], guess['who_showed_card'], 'has')

            # If we know 2 cards guessed could not be held by the person who showed the card, then infer what was shown
            cannot_have_suspect = could_player_hold_card(guess['suspect'], guess['who_showed_card'])
            cannot_have_weapon = could_player_hold_card(guess['weapon'], guess['who_showed_card'])
            cannot_have_location = could_player_hold_card(guess['location'], guess['who_showed_card'])

            if cannot_have_weapon and cannot_have_suspect and cannot_have_location:
                raise ValueError('Someone showed a card, but I do not see how they could have it')

            if cannot_have_suspect and cannot_have_weapon:
                print(guess['who_showed_card'] + ' must have shown ' + guess['location'])
                add_card_to_knowledge(guess['location'], guess['who_showed_card'], 'has')
            elif cannot_have_suspect and cannot_have_location:
                print(guess['who_showed_card'] + ' must have shown ' + guess['weapon'])
                add_card_to_knowledge(guess['weapon'], guess['who_showed_card'], 'has')
            elif cannot_have_weapon and cannot_have_location:
                print(guess['who_showed_card'] + ' must have shown ' + guess['suspect'])
                add_card_to_knowledge(guess['suspect'], guess['who_showed_card'], 'has')

            # If someone can't show a card, we know they don't have it


            #TEST THE CASES I'VE WRITTEN SO FAR

            #COMMIT

            #REFACTOR FUNCTIONS OUT OF MAIN

            #ADD ADDITIONAL CASES




main()
