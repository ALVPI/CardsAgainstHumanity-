from html import unescape
from pathlib import Path
from typing import Annotated
from enum import Enum
from pydantic import AfterValidator, BaseModel, Field
from dataclasses import dataclass
import random 

"""Everyting related with the deck"""
DECK = Path(__file__).parent / "decks"
HAND_SIZE = 5
class BlackCard(BaseModel):
    text: Annotated[str, AfterValidator(unescape)]
    ncards: int = Field(alias="pick")
    
class Deck(BaseModel):
    name: str
    code_name: str = Field(alias="codeName")
    official: bool
    black_cards: list[BlackCard] = Field(alias = "blackCards", default_factory=list)
    white_cards: Annotated[
        list[str], AfterValidator(lambda x: {unescape(e) for e in x})
    ] = Field(alias = "whiteCards", default_factory=list)
    
""""Everything related with the players"""
class Role(str, Enum):
    ZAR: str = "zar"
    PLAYER: str = "player"

@dataclass()
class Player:
    name: str
    id: str
    role : str = ""
    score: int = 0
    cards: list[str] = list

"""Things related with the game and his logic """
def fill_hand(Player: Player, deck: Deck):
    if(len(Player.cards)< HAND_SIZE):
        for _ in range(HAND_SIZE-len(Player.cards)):
            card = random.choice(list(deck.white_cards))
            Player.cards.append(card)
            deck.white_cards.remove(card)
        print(f"{Player.name} has the following cards: {', '.join(Player.cards)}") 

        
def select_winner(answers: list[str], question: BlackCard, players: list[Player]):
    print(f"{question.text}")
    print(answers)
    winner_index = int(input("Type the index of the winner: "))
    print (f"{answers[winner_index]} is the winner of this round")
    find_winner(answers[winner_index], players = players)
    

def find_winner(answer: str, players: list[Player]) -> int:
    for player in players:
        if answer in player.cards:
            return player.id  
            
def act_score(players: list[Player], winner_id: str):
    for player in players:
        if winner_id == player.id:
            player.score += 1              
            
def main():
    deck = Deck.model_validate_json((DECK / "CAH.json").read_bytes())
    runnable: bool = True 
    winner: str = ""
    winner_score: int = 0
    iter: int = 0
    print(f"Welcome to the game of Cards Against Humanity(GUIVERSION)")
    num_players = int(input("Enter number of players: "))
    players = [Player]*num_players
    answers : list[str] = ["" for _ in range(num_players-1)]
    
    for i in range(num_players):
        name = input(f"Enter name for player {i + 1}: ")
        players[i] = Player(name=name, id=str(i + 1), role=Role.PLAYER, score=0, cards=[])
    players[random.randrange(num_players)].role = Role.ZAR
    
    """START THE GAME BOIIIII"""
    while runnable:
        if len(deck.black_cards) == 0 or len(deck.white_cards)/ 5 < len(players):   
            runnable = False
            continue

        for player in players:
            fill_hand(Player=player, deck=deck)
            
        question = random.choice(list(deck.black_cards))
        deck.black_cards.remove(question) 
        print(f"The question is: {question.text}")
        print(f"It's time to get cancelled for the society\n")
        
        for player in players:
            if player.role == Role.ZAR:
                continue
             
            print(f"{player.name}, please select the card that u want to play: \n")
            card_index = int(input(f"Type the index of ur card (0-{len(player.cards)-1}): "))
            if 0 <= card_index < len(player.cards):
                selected_card = player.cards[card_index]
                answers[iter] = selected_card
                iter +=1
                    
        print(f"Zar chooses ur winner")
        
        for player in players:
            if player.role != Role.ZAR:
                continue
            
            print(f"Select the winner of this round (0-{len(players)-1}):\n")
            winner_id: int = select_winner(answers=answers, question=question, players=players)
            act_score(players, winner_id)
   
     
    print("GAME OVER!!!!!!!\n The winner of this match is:")
    for player in players:
        if player.score >= winner_score:
           winner = player.name
           winner_score = player.score
    print(f"{winner} with {player.score} points")
    
if __name__ == "__main__":
    main()
