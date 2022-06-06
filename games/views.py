from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from .forms import ProfileForm

from .models import Game2, Player


def index(request):
    return render(request, 'index.html')


def games(request):
    return render(request, 'games/games.html')


def game_chess(request):
    return render(request, 'games/chess.html')


def game_chess_ai(request):
    return render(request, 'games/game-chess.html')


def game_ai(request, ):
    # return render(request, "game/game.html", {"game_id":game_id})
    return render(request, 'games/game-chess.html', {"game_id": 0 })


def game_clicks(request):
    return render(request, 'games/game-clicks.html')


@login_required
def lobby(request):
    return render(request, 'game/lobby.html')


class profile(View):
    #context ={}
    #context['form']= ProfileForm()
    # return render(request, "home.html", context)
    # return render(request, 'games/profile.html',context)
    def get(self, request):
        context = {}
        context['form'] = ProfileForm()
        return render(request, 'games/profile.html', context)

    def post(self, request):
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        short_desc = request.POST["short_desc"]
        long_desc = request.POST["long_desc"]
        try:
            userdata = Player(is_human=True, user=User.objects.get(username=request.user), first_name=first_name,
                              last_name=last_name, short_description=short_desc, description=long_desc)
            userdata.save()

        except Exception as e:
            print(e)
            messages.add_message(request, messages.ERROR,
                                 "Something went wrong!")
            return HttpResponseRedirect(reverse("profile"))
        messages.add_message(request, messages.SUCCESS,
                             "Profile Created successfully")
        return HttpResponseRedirect("/")


@login_required
def multiplayerchess(request):
    games = []
    l = Game2.objects.all().filter(owner=request.user).filter(status=1)
    g = Game2.objects.all().filter(Q(owner=request.user) |
                                   Q(opponent=request.user)).filter(status=2)
    for i in g:
        x = {}
        if i.owner == request.user:
            x["opponent"] = i.opponent
            x["side"] = i.owner_side
        else:
            x["opponent"] = i.owner
            if i.owner_side == "white":
                x["side"] = "black"
            else:
                x["side"] = "white"
        x["link"] = f"/game/{i.pk}"
        games.append(x)
    return render(request, "game/ongoing.html", {"public": l, "ongoing": games})


@login_required
def newchess(request):
    l = Game2.objects.all().filter(status=1).exclude(owner=request.user)
    pub = []
    for i in l:
        g = {}
        if i.owner_side == "white":
            g["side"] = "Black"
        else:
            g["side"] = "White"
        g["link"] = f"/game/{i.pk}"
        g["owner"] = i.owner
        g["level"] = i.level
        pub.append(g)
    return render(request, "game/lobby.html", {"public": pub})


@login_required
def game(request, game_id):
    game = get_object_or_404(Game2, pk=game_id)
    if game.status == 3:
        messages.add_message(
            request, messages.ERROR, "This game has already been completed! Start another")
        return HttpResponseRedirect(reverse("lobby"))
    if request.user != game.owner:
        if game.opponent == None:
            game.opponent = request.user
            game.status = 2
            game.save()
            messages.add_message(request, messages.SUCCESS,
                                 "You have joined this game successfully")
        elif game.opponent != request.user:
            messages.add_message(
                request, messages.ERROR, "This game already has enough participants. Try joining another")
            return HttpResponseRedirect(reverse("lobby"))
    return render(request, "game/game.html", {"game_id": game_id})


@login_required
def single(request):
    return render(request, "game/single.html")


class createGame(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "game/create.html")

    def post(self, request):
        username = request.POST["username"]
        side = request.POST["side"]
        level = request.POST["level"]
        if username:
            try:
                u = User.objects.get(username=username)
                if u == request.user:
                    messages.add_message(
                        request, messages.ERROR, "You can't play a game with yourself!")
                    return HttpResponseRedirect(reverse("create"))
                g = Game2(owner=request.user, opponent=u,
                          owner_side=side, status=2)
                g.save()
                return HttpResponseRedirect('/game/'+str(g.pk))
            except Exception as e:
                print(e)
                messages.add_message(
                    request, messages.ERROR, "The username entered does not exist")
                return HttpResponseRedirect(reverse("create"))
        else:
            if level == "undef":
                messages.add_message(
                    request, messages.ERROR, "Please choose a level if you are creating a public room!")
                return HttpResponseRedirect(reverse("create"))
            l = Game2(owner=request.user, owner_side=side, level=level)
            l.save()
            messages.add_message(
                request, messages.SUCCESS, "Game created and displayed in Lobby. Check Ongoing Games to see status")
            return HttpResponseRedirect(reverse("lobby"))


@login_required
def ongoing(request):
    games = []
    l = Game2.objects.all().filter(owner=request.user).filter(status=1)
    g = Game2.objects.all().filter(Q(owner=request.user) |
                                   Q(opponent=request.user)).filter(status=2)
    for i in g:
        x = {}
        if i.owner == request.user:
            x["opponent"] = i.opponent
            x["side"] = i.owner_side
        else:
            x["opponent"] = i.owner
            if i.owner_side == "white":
                x["side"] = "black"
            else:
                x["side"] = "white"
        x["link"] = f"/game/{i.pk}"
        games.append(x)
    return render(request, "game/ongoing.html", {"public": l, "ongoing": games})
