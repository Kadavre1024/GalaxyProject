
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '600')

import random

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transforms import transform, transform_perspective, transform_2D
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up

    menu_widget = ObjectProperty(None)
    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")
    score_txt = StringProperty("SCORE : 0")

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 10
    V_LINES_SPACING = .2 # percentage in screen width
    vertical_lines = []
    H_NB_LINES = 15
    H_LINES_SPACING = .1  # percentage in screen width
    horizontal_lines = []

    start_index = -int(V_NB_LINES / 2) + 1
    end_index = start_index + V_NB_LINES - 1

    SPEED_line = 8
    current_offset_y = 0

    SPEED_cols = 10
    current_offset_x = 0

    direction_move = 0

    NB_TILES = 10
    tiles = []
    tiles_coordinates = []
    current_y_loop = 0

    SHIP_WIDTH = .1
    SHIP_HEIGHT = .035
    SHIP_BASE_Y = .04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_as_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_lines(self.vertical_lines, self.V_NB_LINES)
        self.init_lines(self.horizontal_lines, self.H_NB_LINES)
        self.init_tiles()
        self.generate_tiles_coordinates()
        self.init_ship()
        self.init_audio()

        if self.is_desktop():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.on_keyboard_down)
            self.keyboard.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1 / 60)

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/Higher.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6
        self.sound_galaxy.play()

    def reset_game(self, level):
        self.current_offset_y = 0
        self.current_offset_x = 0
        self.current_y_loop = 0
        self.direction_move = 0
        self.score_txt = "SCORE : 0"
        if level == "easy":
            self.SPEED_line = 4
            self.SPEED_cols = 8
        elif level == "medium":
            self.SPEED_line = 8
            self.SPEED_cols = 10
        elif level == "hard":
            self.SPEED_line = 12
            self.SPEED_cols = 16

        self.tiles_coordinates = []
        self.init_tiles()
        self.generate_tiles_coordinates()
        self.state_game_over = False
        self.sound_music1.play()

    def is_desktop(self):
        #print(platform)
        if platform in ("linux", "win", "macosx"):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(1, 0.4, .2)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y*self.height
        half_width_ship = self.SHIP_WIDTH*center_x
        self.ship_coordinates[0] = (center_x-half_width_ship, base_y)
        self.ship_coordinates[1] = (center_x, base_y + self.height*self.SHIP_HEIGHT)
        self.ship_coordinates[2] = (center_x+half_width_ship, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collisions(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop +1:
                self.sound_gameover_impact.play()
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        x_min, y_min = self.get_tile_coordinate(ti_x, ti_y)
        x_max, y_max = self.get_tile_coordinate(ti_x+1, ti_y+1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

    def init_tiles(self):
        if len(self.tiles) == 0:
            with self.canvas:
                Color(0, .5, 1)
                for i in range(0, self.NB_TILES):
                    self.tiles.append(Quad())

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]
        if len(self.tiles_coordinates) > 0:
            last_x = self.tiles_coordinates[-1][0]
            last_y = self.tiles_coordinates[-1][1]+1
        r = 1
        rand_min, rand_max = 0, 2
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            if last_x == self.start_index:
                rand_min = 1
            elif last_x == self.end_index-1:
                rand_max = 1
            else:
                rand_min, rand_max = 0, 2

            if self.current_y_loop > 1:
                r = random.randint(rand_min, rand_max)
            # r = 0 -> gauche
            # r = 1 -> avance
            # r = 2 -> droite
            self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            elif r == 0:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1

    def init_lines(self, list_line, nb_lines):
        for i in range(0, nb_lines):
            with self.canvas:
                Color(1, 1, 1, 0)
                list_line.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        space_line = self.width * self.V_LINES_SPACING
        index_offset = index - 0.5
        line_x = central_line_x + index_offset*space_line - self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        line_y = index*(self.height*self.H_LINES_SPACING) - self.current_offset_y
        return line_y

    def get_tile_coordinate(self, index_x, index_y):
        index_y = index_y - self.current_y_loop
        x = self.get_line_x_from_index(index_x)
        y = self.get_line_y_from_index(index_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            x_min, y_min = self.get_tile_coordinate(self.tiles_coordinates[i][0], self.tiles_coordinates[i][1])
            x_max, y_max = self.get_tile_coordinate(self.tiles_coordinates[i][0] + 1, self.tiles_coordinates[i][1] + 1)
            x1, y1 = self.transform(x_min, y_min)
            x2, y2 = self.transform(x_min, y_max)
            x3, y3 = self.transform(x_max, y_max)
            x4, y4 = self.transform(x_max, y_min)

            self.tiles[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        for i in range(self.start_index, self.start_index + self.V_NB_LINES):
            x1, y1 = self.transform(self.get_line_x_from_index(i), 0)
            x2, y2 = self.transform(self.get_line_x_from_index(i), self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(self.get_line_x_from_index(self.start_index), line_y)
            x2, y2 = self.transform(self.get_line_x_from_index(self.end_index), line_y)

            self.horizontal_lines[i].points = [x1, y1, x2, y2]





    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()


        if not self.state_game_over and self.state_game_as_started:
            space_line = (self.height * self.H_LINES_SPACING)

            self.current_offset_y += (self.SPEED_line*self.height/1000) * time_factor
            self.current_offset_x += (self.SPEED_cols*self.width/1000) * time_factor * self.direction_move

            while self.current_offset_y >= space_line:
                self.current_offset_y -= space_line
                self.current_y_loop += 1
                self.score_txt = "SCORE : " + str(self.current_y_loop)
                self.generate_tiles_coordinates()
                if not self.current_y_loop%100:
                    self.SPEED_line += .5
                print(str(self.SPEED_line))
            if not self.check_ship_collisions():
                self.state_game_over = True

                self.menu_title = "G  A  M  E    O  V  E  R"
                self.menu_button_title = "RESTART"
                self.menu_widget.opacity = 1
                Clock.schedule_once(self.play_gameover_voice, 1)

    def play_gameover_voice(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def on_click_start_game(self, level):
        print("BUTTON")
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.reset_game(level)
        self.state_game_as_started = True
        self.menu_widget.opacity = 0

class GalaxyApp(App):
    pass

GalaxyApp().run()