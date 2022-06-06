import os
import json
import random
from pathlib import Path
import math
from django.shortcuts import render, redirect
from .ai_module import chess_ai
import chess
import stockfish
from stockfish import *
from django.http import HttpResponse
from games.models import *
from django.db.models import Q

fen = None
move_countvalue = None
move_count_status = None
ai_move = ""
move_countvalue = int(500)

BASE_DIR = Path(__file__).resolve().parent.parent
STOCKFISH_PATH = 'stockfish/stockfish_14_x64_bmi2'

# ------------------------------------------------------
# chess AI


def play(request):
    fen = request.GET['fen']
    state = chess.Board(fen)  # initialize a board state using fen
    # search through game tree using board to find best_move
    move = chess_ai.minimax(state)
    return HttpResponse(move.uci())  # return move as a uci string e.g. a2b4


def play_random(request):
    fen = request.GET['fen']
    state = chess.Board(fen)  # initialize a board state using fen
    moves = list(state.legal_moves)
    if moves:
        move = random.choice(moves)
    else:
        move = chess.Move(None, None)

    return HttpResponse(move.uci())  # return move as a uci string e.g. a2b4


def play_stockfish(request):
    sf = stockfish.Stockfish(os.path.join(BASE_DIR, STOCKFISH_PATH))
    fen = request.GET['fen']
    sf.set_fen_position(fen)
    move = sf.get_best_move_time(1000)  # ponder for one second
    print("sf=" + move)
    return HttpResponse(move)  # return move as a uci string e.g. a2b4


def getCurrent_count(request):
    gameid = request.GET['gameid']
    print("Gameid is ", gameid)
    game = Game2.objects.all().filter(id=gameid)[0]
    print("game count is ", game.count)
    return HttpResponse(game.count)


def getcount(request):
    gameid = request.GET['gameid']
    print("Gameid is ", gameid)
    game = Game2.objects.all().filter(id=gameid)[0]
    game.count = game.count-1
    game.save()
    print("game count is ", game.count)
    return HttpResponse(game.count)


# ------------------------------------------------------
# chess move validation

def validate(request):
    fen = request.GET['fen']
    # print("validate="+fen)
    board = chess.Board(fen)
    if(board.is_checkmate()):
        print("checkmate")
        return HttpResponse("Checkmate")
    elif(board.is_insufficient_material()):
        print("Draw")
        return HttpResponse("Draw")
    elif(board.is_check()):
        print("check")
        return HttpResponse("Check")
    else:
        print("false")
        return HttpResponse("False")

# Get the board structure


def fen(request):
    global fen
    fen = request.GET['fen']
    return HttpResponse()

# Get the details about the last move and validate with the fen


def move_validate(request):
    pgn = request.GET['pgn']
    print("pgn="+pgn)
    print(type(pgn))
    move = chess.Move.from_uci(pgn)
    print("views=", move)
    # print(pgn)
    # print(fen)
    board = chess.Board(fen)
    if (move in board.legal_moves):
        # print("legal")
        return HttpResponse("legal")
    else:
        # print("illegal")
        return HttpResponse("illegal")
    # return HttpResponse("illegal")
# ------------------------------------------------------
# total 500 moves


def move_count(request):
    # move_count2=request.GET['move_count2']
    result = request.GET['result']
    # pgn2=request.GET['pgn2']
    global move_countvalue
    # print(move_countvalue)
    global move_count_status
    if (result != "legal" or result == None and move_count_status >= 0):
        move_count_status = move_countvalue
        return HttpResponse(move_count_status)
    else:
        # move_countvalue -= 1;
        # print(move_countvalue)
        # move_count1 = move_count - 1;
        if (move_countvalue <= 0):
            # game = game.game_over();
            return HttpResponse("0")
        elif(result == "legal"):
            move_countvalue -= 1
            # print("views=", move_countvalue)
            # game.move({ from: from_square, to: to_square });
            # move_count = move_count - 1;
            move_count_status = move_countvalue
            return HttpResponse(move_count_status)


def total_count(request):
    # total_count=request.GET['total_count']
    # print(total_count)
    global move_countvalue
    move_countvalue = int(500)
    print(move_countvalue)
    return HttpResponse()

# ------------------------------------------------------
# Elo score


def score(request):
    loser = request.GET['fen']
    print("Loser is ", loser)
    game = Game.objects.get(proper_name="single")
    player = Player.objects.get(user=User.objects.get(username=request.user))
    #ratingset= GameRating(game=game,player=player,rating=3600)
    ratingset = GameRating.objects.get(game=game, player=player)
    player_old_score = ratingset.rating
    print("Old Elo", player_old_score)

    # set constant elo score for AI
    ai_score = 1000
    K = Game.objects.get(proper_name="single").elo_k
    print("K = ", K)
    d = 0 if loser == "White" else 1
    player_new_elo_score, ai_new_score = EloRating(
        player_old_score, ai_score, K, d)

    if GameRating.objects.get(game=game, player=player).fixed == False:
        ratingset.rating = player_new_elo_score
        ratingset.save()
    else:
        player_new_elo_score = player_old_score

    print("New Elo", player_new_elo_score)
    print("data_saved")
    Data = {}
    Data["Player_Score"] = player_new_elo_score
    Data["AI_Score"] = ai_new_score
    Data["Result"] = "Checkmate"
    return HttpResponse(json.dumps(Data))


def Probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def EloRating(Ra, Rb, K, d):
    Pb = Probability(Ra, Rb)
    Pa = Probability(Rb, Ra)
    if (d == 1):
        Ra = Ra + K * (1 - Pa)
        Rb = Rb + K * (0 - Pb)
    else:
        Ra = Ra + K * (0 - Pa)
        Rb = Rb + K * (1 - Pb)
    return round(Ra, 6), round(Rb, 6)
    #print("Updated Ratings:-")
    #print("Ra =", round(Ra, 6)," Rb =", round(Rb, 6))

# ------------------------------------------------------------------------------------------


def current_score(request):

    game = Game.objects.get(proper_name="single")
    player = Player.objects.get(user=User.objects.get(username=request.user))

    try:
        ratingset = GameRating.objects.get(game=game, player=player)
        player_current_elo_score = ratingset.rating

    except:
        rating_set = GameRating(game=game, player=player)
        rating_set.save()
        ratingset = GameRating.objects.get(game=game, player=player)
        player_current_elo_score = ratingset.rating

    # set constant elo score for AI
    ai_current_elo_score = 1000
    Data = {}
    Data["Player_Current_Score"] = player_current_elo_score
    Data["AI_Current_Score"] = ai_current_elo_score
    return HttpResponse(json.dumps(Data))


#------------------------------------------------------------------------------------------

def DualPlayer_current_score(request):
    game = Game.objects.get(proper_name="single")
    player = Player.objects.get(user= User.objects.get(username=request.user))

    try:
        ratingset = GameRating.objects.get(game=game,player=player)
        player_current_elo_score = ratingset.rating
        print("current player ratings : ", player_current_elo_score)
    
    except:
        rating_set= GameRating(game=game,player=player)
        rating_set.save()
        ratingset = GameRating.objects.get(game=game,player=player)
        player_current_elo_score = ratingset.rating
        print("current player ratings : ", player_current_elo_score)

        #getting opponent
    g = Game2.objects.all().filter(Q(owner=request.user) | Q(opponent=request.user)).filter(status=2)
    for i in g:
        x = {}
        if i.owner == request.user:
            x["opponent"] = i.opponent
            print("Opponent : ",i.opponent.username)
            opponent_player = Player.objects.get(user= User.objects.get(username=i.opponent.username))
            x["side"] = i.owner_side

        else:
            x["opponent"] = i.owner
            if i.owner_side == "white":
                x["side"] = "black"
            else:
                x["side"] = "white"  
            opponent_player = Player.objects.get(user= User.objects.get(username=i.owner.username))      
    print("#################")
    if x['side'] == "black":
        x['side'] = "Black"
    else:
        x['side'] = "White"
    print(x)
    print("#################")
    opponent_ratingset = GameRating.objects.get(game=game,player=opponent_player)
    print(opponent_ratingset)
    print("opponent player ratings : ", opponent_ratingset.rating)

    #code ends here  
    Data={}
    Data["Player_Current_Score"]=player_current_elo_score
    Data["AI_Current_Score"]=opponent_ratingset.rating        
    return HttpResponse(json.dumps(Data))  

#----------------------------------------------------
# Dual Players Elo score

def DualPlayerScore(request):
    loser = request.GET['loser']
    print("Loser is ",loser)
    game = Game.objects.get(proper_name="single")
    player = Player.objects.get(user= User.objects.get(username=request.user))
    #ratingset= GameRating(game=game,player=player,rating=3600)
    ratingset = GameRating.objects.get(game=game,player=player)  
    player_old_score = ratingset.rating
    print("Old Elo",player_old_score)

    #getting opponent
    #g = Game2.objects.all().filter(Q(owner=request.user) | Q(opponent=request.user)).filter(status=2)
    g = Game2.objects.all()
    print("out")
    print(g)
    for i in g:
        x = {}
        print("in loop")
        if i.owner == request.user:
            x["opponent"] = i.opponent
            print("Opponent : ",i.opponent.username)
            opponent_player = Player.objects.get(user= User.objects.get(username=i.opponent.username))
            x["side"] = i.owner_side

        else:
            x["opponent"] = i.owner
            if i.owner_side == "white":
                x["side"] = "black"
            else:
                x["side"] = "white"  
            opponent_player = Player.objects.get(user= User.objects.get(username=i.owner.username))      
    print("#################")
    if x['side'] == "black":
        x['side'] = "Black"
    else:
        x['side'] = "White"
    print(x)
    print("#################")
    
    opponent_ratingset = GameRating.objects.get(game=game,player=opponent_player)
    print(opponent_ratingset)
    print("opponent player ratings : ", opponent_ratingset.rating)
    #set constant elo score for AI
    ai_score = opponent_ratingset.rating
    K = Game.objects.get(proper_name="single").elo_k
    print("K = ",K)
    
    d=0 if loser==x['side'] else 1
    player_new_elo_score,ai_new_score = EloRating(player_old_score, ai_score, K, d)
    
    if GameRating.objects.get(game=game,player=player).fixed==False:
        ratingset.rating = player_new_elo_score
        ratingset.save()
    else:
        player_new_elo_score = player_old_score

    print("New Elo",player_new_elo_score)
    print("data_saved")
    Data={}
    Data["Player_Score"]=player_new_elo_score
    Data["AI_Score"]=ai_new_score
    Data["Result"]="Checkmate"        
    return HttpResponse(json.dumps(Data))

