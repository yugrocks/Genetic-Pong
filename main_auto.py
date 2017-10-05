from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from time import sleep
import sys
import numpy as np
from functools import partial
from random import random, uniform

# pykeyboard is not working with kivy code, and is not required
"""
try:
    from pykeyboard import PyKeyboard
except ImportError:
    sys.exit("You need to install pykeyboard. Install it by running 'pip install pyuserinput'")


kb = PyKeyboard()"""
auto_mode = 1
max_width =  800
max_height =  600
max_score = 5

class PongPaddle(Widget):
    score = NumericProperty(0)
    pseudo_score = 0
    def bounce_ball(self, ball, p1=False):
        if self.collide_widget(ball):
            self.pseudo_score+=1
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.0
            #ball.velocity = vel.x, vel.y #keep velocity constant
            if p1:
                ball.velocity = vel.x, vel.y + uniform(-5, 5)
            else:
                ball.velocity = vel.x, vel.y + offset

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    game_over = False
    result = StringProperty('')
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    motion = 10
    
    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_keyboard_down)
        self._keyboard.bind(on_key_up = self._on_keyboard_up)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard.unbind(on_key_up = self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w':
            self.player1.center_y += self.motion
            self.motion += 2
            if self.player1.center_y > self.height:
                self.player1.center_y = self.height
        if keycode[1] == "s":
            self.player1.center_y -= self.motion
            self.motion += 2
            if self.player1.center_y < 0:
                self.player1.center_y = 0
        if keycode[1] == "up":
            self.player2.center_y += self.motion
            self.motion += 2
            if self.player2.center_y > self.height:
                self.player2.center_y = self.height
        if keycode[1] == "down":
            self.player2.center_y -= self.motion
            self.motion += 2
            if self.player2.center_y < 0:
                self.player2.center_y = 0
        return True

    def _on_keyboard_up(self, keyboard, keycode):
	    self.motion = 10
	    return True

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel
        sleep(0.1)

    def update(self,dt, model):
        self.ball.move()
        # bounce of paddles
        self.player1.bounce_ball(self.ball, p1=True)
        self.player2.bounce_ball(self.ball)

        """if (auto_mode == 1 and self.ball.velocity_x > 0 and abs(self.player1.center_y - self.height//2) > 10):
            if (self.player1.center_y < self.height//2):
                self.player1.center_y += self.motion
                self.motion += 2
                if self.player1.center_y > self.height:
                        self.player1.center_y = self.height
                #kb.press_key('w')
                #kb.release_key('w')
            else:
                self.player1.center_y -= self.motion
                self.motion += 2
                if self.player1.center_y < 0:
                        self.player1.center_y = 0
                #kb.press_key('s')
                #kb.release_key('s')"""

        #auto moving player 1. This perfect player was used to train player 2 on its own
        if (auto_mode == 1 and self.ball.velocity_x < 0):
            if(abs(self.player1.center_y - self.ball.center_y) > 10):
                if (self.player1.center_y < self.ball.center_y):
                    #self.player1.center_y += self.motion
                    self.player1.center_y = self.ball.pos[1]
                    self.motion += 4
                    if self.player1.center_y > self.height:
                        self.player1.center_y = self.height
                else:
                   # self.player1.center_y -= self.motion
                    self.player1.center_y = self.ball.pos[1]
                    self.motion += 4
                    if self.player1.center_y < 0:
                        self.player1.center_y = 0
        #Learning and moving player 2
        if (auto_mode == 1):
            features = np.array([[1.0,
                                  self.ball.velocity_y / self.ball.velocity_x,

                                  (self.ball.pos[1] - self.player2.center_y)/max_height,
                                  (self.player2.center_y)/max_height
                                  ]])
            #move = moves[model.predict(features)]
            move = model.predict(features)
            if move == "up":
                self.player2.center_y += 2
                self.motion += 2
                if self.player2.center_y > self.height:
                    self.player2.center_y = self.height
            elif move == "down":
                self.player2.center_y -= 2
                self.motion += 2
                if self.player2.center_y < 0:
                    self.player2.center_y = 0
            


        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            if self.player2.score == max_score:
                #self.result = "Player 2 Wins!"
                self.game_over = True
                #Clock.unschedule(self.update)
            
            elif self.player1.score == max_score:
                #self.result = "Player 1 Wins!"
                self.game_over = True
                #Clock.unschedule(self.update)
                
            if not self.game_over:
                self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            if self.player2.score == max_score:
                #self.result = "Player 2 Wins!"
                self.game_over = True
                #Clock.unschedule(self.update)
    
            elif self.player1.score == max_score:
                #self.result = "Player 1 Wins!"
                self.game_over = True
                #Clock.unschedule(self.update)
        
            if not self.game_over:
                self.serve_ball(vel=(-4, 0))
                  

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    event = None
    def build(self):
        game = PongGame()
        game.serve_ball()
        self.event = Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game
"""

if __name__ == '__main__':
    app = PongApp()
    app.run()
    
"""
