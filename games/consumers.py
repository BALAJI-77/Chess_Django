import json
import math
from time import time

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer, JsonWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
import chess_ai.views
from .models import Game2
from .chessAI import call_AI
from .chessAI import stockfish_AI

game_id = None


class NewChessConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('GameConsumer.connect')
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        global game_id
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        if(self.game_id == 0):
            print("single")
            await self.accept()
            await self.send_json({"command": "join", "orientation": "white"})

        if(self.game_id != 0):
            try:
                print("multi")
                self.game_id = int(self.game_id)
            except:
                await self.close()
                return
            side = await self.verify(self.game_id)
            print(side)
            # for i in side:
            # print(i)
            if side == False:
                await self.close()
                return
            await self.accept()
            await self.join_room(side)
            if side[2]:
                # print(side[2])
                await self.opp_online()

    async def receive_json(self, content):
        command = content.get("command", None)
        try:
            if command == "new-move-AI":
                move = stockfish_AI(content["fen"])
                await self.send_json({"command": "new-move-AI", "move": move})
                # await self.new_move_AI(content[move])
            if command == "count":
                await self.count_move()

            if command == "new-move":
              
                await self.new_move(content["source"], content["target"], content["fen"], content["pgn"])

            elif command == "game-over":
                await self.game_over(content["result"])
            elif command == "resign":
                await self.resign()
                await self.game_over(content["result"])
        except:
            pass

    async def disconnect(self, code):
        if(self.game_id == 0):
            pass
        if(self.game_id != 0):
            await self.disconn()
            await self.opp_offline()

    async def join_room(self, data):
        if game_id == 0:
            pass

        if game_id != 0:
            await self.channel_layer.group_add(
                str(self.game_id),
                self.channel_name,
            )
            await self.send_json({
                "command": "join",
                "orientation": data[0],
                "pgn": data[1],
                "opp_online": data[2],
                # "count": data[3]
            })

    async def opp_offline(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "offline.opp",
                'sender_channel_name': self.channel_name
            }
        )

    async def offline_opp(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send_json({
                "command": "opponent-offline",
            })
            print("sending offline")

    async def opp_online(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "online.opp",
                'sender_channel_name': self.channel_name
            }
        )

    async def online_opp(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send_json({
                "command": "opponent-online",
            })

    async def resign(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "resign.game",
                'sender_channel_name': self.channel_name
            }
        )

    async def resign_game(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send_json({
                "command": "opponent-resigned",
            })

    async def new_move(self, source, target, fen, pgn):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "move.new",
                "source": source,
                "target": target,
                "fen": fen,
                "pgn": pgn,
                'sender_channel_name': self.channel_name
            }
        )

    async def count_move(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "move.count",
                'sender_channel_name': self.channel_name
            }
        )

    @database_sync_to_async
    def count(self):
        print("hello")
        game = Game2.objects.all().filter(id=self.game_id)[0]
        print(game.count)
        game.count = game.count-1
        # game.save()
        print(game.count)
        game.save()
        return game.count

    async def move_new(self, event):
        if self.channel_name != event['sender_channel_name']:
            # game = Game2.objects.all().filter(id=self.game_id)[0]
            await self.send_json({
                "command": "new-move",
                "source": event["source"],
                "target": event["target"],
                "fen": event["fen"],
                "pgn": event["pgn"],
                # "count": await self.count(),
                "count": "hello",
            })
        await self.update(event["fen"], event["pgn"])

    async def move_count(self, event):
        if self.channel_name != event['sender_channel_name']:
            # game = Game2.objects.all().filter(id=self.game_id)[0]
            await self.send_json({
                "command": "move_count",
                "count": await self.count(),
                # "count": "hello",
            })

    @database_sync_to_async
    def game_over(self, result):
        game = Game2.objects.all().filter(id=self.game_id)[0]
        if game.status == 3:
            return
        game.winner = result
        game.status = 3
        game.save()

    @database_sync_to_async
    def verify(self, game_id):
        game = Game2.objects.all().filter(id=game_id)[0]
        # game.count = game.count-1
        if not game:
            return False
        user = self.scope["user"]
        side = "white"
        opp = False
        if game.opponent == user:
            game.opponent_online = True
            if game.owner_side == "white":
                side = "black"
            else:
                side = "white"
            if game.owner_online == True:
                opp = True
            print("Setting opponent online")
        elif game.owner == user:
            game.owner_online = True
            if game.owner_side == "white":
                side = "white"
            else:
                side = "black"
            if game.opponent_online == True:
                opp = True
            print("Setting owner online")
        else:
            return False

        game.save()
        return [side, game.pgn, opp, game.count]

    @database_sync_to_async
    def disconn(self):
        user = self.scope["user"]
        game = Game2.objects.all().filter(id=self.game_id)[0]
        if game.opponent == user:
            game.opponent_online = False
            print("Setting opponent offline")
        elif game.owner == user:
            game.owner_online = False
            print("Setting owner offline")
        game.save()

    @database_sync_to_async
    def update(self, fen, pgn):
        game = Game2.objects.all().filter(id=self.game_id)[0]

        if not game:
            print("Game not found")
            return
        game.fen = fen
        game.pgn = pgn
        # print("hello")
        # # game = Game2.objects.all().filter(id=self.game_id)[0]
        # print(game.count)
        # game.count = game.count-1
        # # game.save()
        # print(game.count)
        game.save()
        print("Saving game details")


class ClicksConsumer(WebsocketConsumer):
    def connect(self):
        # There needs to be a unique one of these for
        # each instance of each game. For now, we hardcode
        # this for a single instance of one game.
        self.room_group_name = 'game_clicks_1'
        self.last_click_time = None
        self.clicks = []

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        x = text_data_json['x']
        y = text_data_json['y']

        # print curr click
        print(f"curr (x,y) = ({x},{y})")

        #
        delta_time = None
        now = time()
        reward = 0

        #
        if self.last_click_time:
            delta_time = now - self.last_click_time
            nearest_distance = 99999999

            # find nearest prev click
            for z in self.clicks:
                zx = z[0]
                zy = z[1]
                distance = math.sqrt(math.pow(x - zx, 2) + math.pow(y - zy, 2))

                # print each prev click and its dist
                # print(z)
                #print(f"distance = {distance}")

                #
                if distance < nearest_distance:
                    nearest_distance = distance

            #
            reward = delta_time*(nearest_distance - 20)

            # print nearest
            print(f"nearest distance = {nearest_distance}")

        self.last_click_time = now
        self.clicks.append((x, y))

        # print dt
        print(f"delta time = {delta_time}")

        # print reward
        print(f"reward = {reward}")
        print("\n")

        # send x,y to consumers of other players via channel layer
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'x': x,
                'y': y
            }
        )

        # send reward to consumers of other players via channel layer
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'cl_reward',
                'reward': reward,
                'channel_name': self.channel_name
            }
        )

    # receive x,y from a player's consumer and send to single front-end
    def chat_message(self, event):
        x = event['x']
        y = event['y']

        # send to front-end
        self.send(text_data=json.dumps({
            'x': x,
            'y': y
        }))

    # receive reward from a player's consumer and send to single front-end
    # if reward is from a different player, then negate before sending
    def cl_reward(self, event):
        reward = event['reward']
        reward_channel_name = event['channel_name']

        # negate if diff player
        if self.channel_name != reward_channel_name:
            reward = -reward

        # send to front-end
        self.send(text_data=json.dumps({
            'reward': reward
        }))
