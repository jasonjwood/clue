import csv
import json

players = {}
my_name = ''
solution_suspect = '?'
solution_weapon = '?'
solution_location = '?'

card_indexes = ['draco', 'crabbe', 'lucius', 'umbridge', 'pettigrew', 'bellatrix', 'draught', 'cabinet', 'portkey',
                'impedimenta', 'petrificus', 'mandrake', 'hall', 'hospital', 'ror', 'potions', 'trophy', 'divination',
                'owlery', 'library', 'doda']

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


def write_card_knowledge():
    with open('knowledge.csv', mode='w') as knowledge_csv:
        header = 'Card,'
        for player in players:
            header = header + player + ","
        knowledge_csv.write(header + '\n')

        for c in card_indexes:
            line = c + ',' \

            for player in players:
                if cards[c]['knowledge'].get(player) is None:
                    line = line + '?,'
                else:
                    line = line + cards[c]['knowledge'][player] + ','

            knowledge_csv.write(line + '\n')


def add_card_to_solution(card):
    global solution_suspect
    global solution_weapon
    global solution_location

    if cards[card]['type'] == 'suspect':
        solution_suspect = card
    elif cards[card]['type'] == 'weapon':
        solution_weapon = card
    elif cards[card]['type'] == 'location':
        solution_location = card

    print('SOLUTION is now: ' + solution_suspect + ' ' + solution_weapon + ' ' + solution_location)


def add_card_to_knowledge(card, player, knowledge_type):
    print('We now know that ' + player + ' ' + knowledge_type + ' ' + card)
    cards[card]['knowledge'][player] = knowledge_type

    # If we just identified someone has a card, then no one else can have it.
    for other in players:
        if other != player:
            if knowledge_type == 'has':
                cards[card]['knowledge'][other] = 'cannot_have'

    # Check if N players 'cannot_have' - must be part of the solution
    if knowledge_type == 'cannot_have':
        everyone_cannot_have = True
        for p in players:
            if not could_player_hold_card(card, p):
                everyone_cannot_have = False
                break

        if everyone_cannot_have:
            add_card_to_solution(card)


def is_player_card_state_unknown(card, player):
    return cards[card]['knowledge'].get(player) is None


def does_player_hold_card(card, player):
    if cards[card]['knowledge'].get(player) is None:
        return False

    return cards[card]['knowledge'][player] == 'has'


def could_player_hold_card(card, player):
    # Return no if the player specifically can't have that card
    if cards[card]['knowledge'].get(player) == 'cannot_have':
        return False

    return True


def read_player_names():
    global players
    with open('players.txt', mode='r') as players_txt:
        previous_name = ''
        first_name = ''
        for player in players_txt:
            name = player.rstrip('\n')

            if first_name is '':
                first_name = name

            players[name] = {'name': name, 'next_player': ''}

            if previous_name is not '':
                players[previous_name]['next_player'] = name

            previous_name = name

        players[previous_name]['next_player'] = first_name

    print('Players: ')
    print(players)


def read_my_cards():
    global my_name
    with open('mycards.txt', mode='r') as my_cards_txt:
        for card in my_cards_txt:
            card = card.rstrip('\n')
            # first row is my name
            if my_name == '':
                my_name = card
            else:
                add_card_to_knowledge(card, my_name, 'has')

        for c in card_indexes:
            if not does_player_hold_card(c, my_name):
                add_card_to_knowledge(c, my_name, 'cannot_have')

    print('Cards:')
    print(cards)


def logic_we_saw_a_card(card_was_shown, card_shown, who_showed_card):
    print('logic_we_saw_a_card')
    if card_was_shown:
        # Validate that the card we just saw doesn't violate all of our logic so far.
        assert (could_player_hold_card(card_shown, who_showed_card))

        print('We just saw a card')
        add_card_to_knowledge(card_shown, who_showed_card, 'has')


def logic_must_have_card_shown(guess_suspect, guess_weapon, guess_location, guess_who_showed_card):
    print('logic_must_have_card_shown')
    could_have_suspect = could_player_hold_card(guess_suspect, guess_who_showed_card)
    could_have_weapon = could_player_hold_card(guess_weapon, guess_who_showed_card)
    could_have_location = could_player_hold_card(guess_location, guess_who_showed_card)

    if not could_have_weapon and not could_have_suspect and not could_have_location:
        raise ValueError('Someone showed a card, but I do not see how they could have it')

    if not could_have_suspect and not could_have_weapon:
        print(guess_who_showed_card + ' must have shown ' + guess_location)
        add_card_to_knowledge(guess_location, guess_who_showed_card, 'has')
    elif not could_have_suspect and not could_have_location:
        print(guess_who_showed_card + ' must have shown ' + guess_weapon)
        add_card_to_knowledge(guess_weapon, guess_who_showed_card, 'has')
    elif not could_have_weapon and not could_have_location:
        print(guess_who_showed_card + ' must have shown ' + guess_suspect)
        add_card_to_knowledge(guess_suspect, guess_who_showed_card, 'has')


def logic_who_failed_to_show_cards(active_player, player_who_showed_card, suspect, weapon, location):
    print('logic_who_failed_to_show_cards')
    stop_at_player = ''
    if player_who_showed_card is not None and len(player_who_showed_card) >  0:
        stop_at_player = player_who_showed_card
    else:
        stop_at_player = active_player

    player = players[active_player]['next_player']

    while player != stop_at_player:
        add_card_to_knowledge(suspect, player, 'cannot_have')
        add_card_to_knowledge(weapon, player, 'cannot_have')
        add_card_to_knowledge(location, player, 'cannot_have')
        player = players[player]['next_player']


def process_guess(guess):
    print('Guess: ')
    print(guess)

    # Validate that the guessed elements are in our list of cards,
    assert (len(cards.get(guess['suspect'])) > 0)
    assert (len(cards.get(guess['weapon'])) > 0)
    assert (len(cards.get(guess['location'])) > 0)
    card_was_shown = False
    if guess.get('card_shown') is not None and len(guess['card_shown']) > 0:
        card_was_shown = True
        assert (cards.get(guess['card_shown']) is not None)

    # If we know which card was shown and who showed it, then add that to knowledge
    logic_we_saw_a_card(card_was_shown, guess['card_shown'], guess['who_showed_card'])

    # If someone can't show a card, we know they don't have it
    logic_who_failed_to_show_cards(guess['active_player'], guess['who_showed_card'], guess['suspect'], guess['weapon'], guess['location'])

    # If we know 2 cards guessed could not be held by the person who showed the card, then infer what was shown
    logic_must_have_card_shown(guess['suspect'], guess['weapon'], guess['location'], guess['who_showed_card'])




def process_guesses():
    # Read csv file representing guesses, building knowledge as we go
    with open('guesses.csv', mode='r') as guesses_csv:
        guess_reader = csv.DictReader(guesses_csv)
        for guess in guess_reader:
            process_guess(guess)


def main():
    read_player_names()
    read_my_cards()

    process_guesses()

    write_card_knowledge()

    print("CARDS:")
    print(json.dumps(cards, indent=1))


main()


# ADD ADDITIONAL CASES
