from typing import DefaultDict
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
import hashlib


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

    def __unicode__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False

    def profile_image_url(self):
        fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')

        if len(fb_uid):
            return "http://graph.facebook.com/{}/picture?width=40&height=40".format(fb_uid[0].uid)

        return "http://www.gravatar.com/avatar/{}?s=40".format(hashlib.md5(self.user.email.encode('utf-8')).hexdigest())

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class Player(models.Model):
    """A player is a persistent profile that has ratings in various
    games. A player can be human or AI. In either case, the player is
    owned by a particular user account. Generally there will be
    exactly one player for each human user, but there can be zero or
    more AI players per account.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='players')
    is_human = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    description = models.CharField(max_length=2048)


class ApiKey(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE,
                               related_name='api_keys')
    api_id = models.CharField(max_length=255)
    api_salt = models.CharField(max_length=255)
    hashed_api_secret = models.CharField(max_length=255)


class PlayerVersion(models.Model):
    """A player version is a version of an AI that plays the games. This
    will be identified by a string supplied by the client library.
    This class exists so that we can filter episodes etc. by version
    in the UI. Human players will only have one version.
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE,
                               related_name='versions')
    version_string = models.CharField(max_length=255)


class Course(models.Model):
    """A course is the highest-level unit of content. A course contains
    many games."""
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=32, default='GAME-001')
    subscribers = models.ManyToManyField(User, related_name='courses')


class Game(models.Model):
    """A game is a game that players can play."""
    num_players = models.IntegerField(default=2)
    proper_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=32, default='')
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               related_name='games')
    elo_k = models.FloatField(default=40.0)


class MatchRequest(models.Model):
    """A match request is a request to play a particular game. Currently
    the only filter the creator is allowed to use is a minimum ELO
    rating and a maximum ELO rating.

    The issuer of the request may be a player in the proposed game or
    not; humans are allowed to trigger requests for matches they do
    not play in, but AI's are not.
    """
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE,
        related_name='match_requests')
    issuer = models.ForeignKey(
        PlayerVersion, on_delete=models.CASCADE,
        related_name='match_requests_issued')
    players = models.ManyToManyField(
        PlayerVersion,
        related_name='match_requests_accepted')
    # humans are allowed to trigger games that they do not play in
    issuer_plays = models.BooleanField(default=True)
    rating_min = models.IntegerField(null=True)
    rating_max = models.IntegerField(null=True)


class Episode(models.Model):
    """An episode is a single play-through of a game. It has a series of
    timesteps, represented as a JSON field.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='episodes')
    match_request = models.ForeignKey(MatchRequest,
                                      null=True,
                                      on_delete=models.CASCADE,
                                      related_name='episodes')
    timesteps = models.JSONField(default=list)

class Game2(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE,related_name="owner")
    opponent = models.ForeignKey(User, on_delete=models.CASCADE,related_name="opponent", null=True)
    owner_side= models.CharField(max_length=10, default="white")
    owner_online = models.BooleanField(default=False)
    opponent_online = models.BooleanField(default=False)
    count = models.IntegerField(default=500)
    fen = models.CharField(max_length=92, null=True, blank=True)
    pgn = models.TextField(null=True, blank=True)
    winner = models.CharField(max_length=20, null=True, blank=True)
    level = models.CharField(max_length=15, null=True, blank=True)
    CHOICES=(
        (1,"Game Created. Waiting for opponent"),
        (2,"Game Started"),
        (3,"Game Ended"))
    status = models.IntegerField(default=1,choices=CHOICES)


class EpisodePlayerLink(models.Model):
    """An episode player link is a relationship between a player version
    and an episode; the link means that the player version is one of
    the players in the episode. Additionally, it specifies which role
    the given player version is playing in the game.
    """
    player_version = models.ForeignKey(PlayerVersion,
                                       on_delete=models.CASCADE,
                                       related_name='episode_links')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE,
                                related_name='player_version_links')
    # some games have differentiated roles, e.g. white vs. black in
    # chess or go. for games with a defined order of play, this will
    # be the order of play
    player_num = models.IntegerField()


class GameRating(models.Model):
    """An ELO rating for a particular player in a particular game at a
    particular point in time."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='ratings')
    player = models.ForeignKey(Player, on_delete=models.CASCADE,
                               related_name='ratings')
    rating = models.FloatField(default=1000.0)
    date = models.DateTimeField(default=timezone.now)
    # fixed means it won't change in response to winning or losing, so
    # new ratings shouldn't be created (except manually, if desired)
    fixed = models.BooleanField(default=False)
