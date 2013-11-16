#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.config import Config
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.animation import Animation

import os
import config
from datetime import timedelta, datetime
from functools import partial
import random

Builder.load_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ui.kv'))

# don't include this line when compiling for mobile
Window.size = (440,836)

class SelectorWidget(Widget):
    name = StringProperty(None)
    remove_button = ObjectProperty(None)
    text_box = ObjectProperty(None)    
    text_height = 20
    current_index = NumericProperty(None)
    animation_step_time = random.uniform(0.075,0.12)
    current_label = ObjectProperty(None, allow_none = True)

    def __init__(self, name, options, remove_callback = None, **kwargs):
        self.name = name
        self.options = options
        self.remove_callback = remove_callback
        super(SelectorWidget, self).__init__(**kwargs)
        # if the size of the selector widget changes, regenerate the option labels so they still fit
        self.text_box.bind(size=self.make_labels)

    def make_labels(self, *args):
        texture_size = self.text_box.size        
        self.labels = [Label(text = text, size = texture_size) for text in self.options]            

    def on_current_index(self, instance, value):
        # this method needs some TLC. It works beautifully... the first time. After then, not so much.
        old_label = self.current_label
        new_label = self.labels[value]
        away_anim = Animation(y=self.text_box.top, duration = self.animation_step_time)
        away_anim.bind(on_complete = self.remove_label)
        to_anim = Animation(y=self.text_box.y, duration = self.animation_step_time)
        if old_label is not None: away_anim.start(old_label)
        new_label.pos = (self.text_box.x, self.text_box.y - self.text_box.height)
        self.text_box.add_widget(new_label)
        to_anim.start(new_label)
        self.current_label = new_label

    def remove_label(self, instance, value):
        self.text_box.remove_widget(value)

    def spin(self, duration, *args):
        Clock.schedule_interval(self.animation_step, self.animation_step_time)
        self.stop_time = datetime.now() + duration

    def animation_step(self, *args):
        if datetime.now() <= self.stop_time:
            self.next()
        
    def next(self, *args):
        if self.current_index is None:
            self.current_index = 0
        else:
            self.current_index = (self.current_index + 1) % len(self.options)

    def on_touch_down(self, touch):
        if self.remove_button.collide_point(*touch.pos):
            self.remove_callback(self.name)

class SeparatorBar(Widget):
    pass

class PlusButtonWidget(Widget):
    def __init__(self, callback, **kwargs):
        self.callback = callback
        super(PlusButtonWidget, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.callback()


class MainInterface(Widget):
    heading_list = ObjectProperty(None)
    headings = ListProperty(None)
    plus_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainInterface, self).__init__(**kwargs)
        self.plus_button = PlusButtonWidget(self.plus_button_pressed)
        self.heading_texts = config.heading_order[:config.default_num_headings]
        self.headings = [SelectorWidget(x, config.categories[x], remove_callback=self.remove_heading) for x in self.heading_texts]

    def get_next_heading(self):
        all_hidden_headings = [x for x in config.heading_order if x not in self.heading_texts]
        return None if len(all_hidden_headings) == 0 else all_hidden_headings[0]

    def remove_heading(self, name):
        self.heading_texts.remove(name)
        self.headings = [h for h in self.headings if h.name != name]

    def on_headings(self, instance, value):
        self.heading_list.clear_widgets()
        for selector_widget in self.headings:
            self.heading_list.add_widget(selector_widget)
        self.heading_list.add_widget(self.plus_button)
        self.heading_list.add_widget(Widget(size_hint=(1,1)))

    def spin_button_pressed(self):
        for selector in self.headings:
            Clock.schedule_once(partial(selector.spin, timedelta(seconds=random.uniform(1.0,3.0))), random.uniform(0,1.0))

    def plus_button_pressed(self):
        new_heading = self.get_next_heading()
        if new_heading is not None:
            self.heading_texts.append(new_heading)
            self.headings.append(SelectorWidget(new_heading, config.categories[new_heading], remove_callback=self.remove_heading))

if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainInterface())
