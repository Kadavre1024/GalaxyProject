from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self.keyboard.unbind(on_key_down=self.on_keyboard_down)
    self.keyboard.unbind(on_key_up=self.on_keyboard_up)
    self.keyboard = None


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.direction_move = -1
    elif keycode[1] == 'right':
        self.direction_move = 1
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.direction_move = 0
    return True


def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_as_started:
        if touch.x > self.width/2:
            self.direction_move = 1
        else:
            self.direction_move = -1
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    self.direction_move = 0
