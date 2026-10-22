# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 01:25:05 2026

@author: dejam
"""

""" Same as the last used encoder.py
    Just pasted here for conveience 
    and organizing purposes """
from pyb import Pin, Timer
from time import ticks_us, ticks_diff   # Use to get dt value in update()


class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, tim, chA_pin, chB_pin):
        '''Initializes an Encoder object'''
        self.tim = tim

        # Tell the timer to count encoder pulses on these two pins
        tim.channel(1, pin=chA_pin, mode=Timer.ENC_AB)
        tim.channel(2, pin=chB_pin, mode=Timer.ENC_AB)

        # Highest number the counter reaches before it rolls over to 0
        self.AR = tim.period()

        self.position   = 0     # Total accumulated position of the encoder
        self.prev_count = 0     # Counter value from the most recent update
        self.delta      = 0     # Change in count between last two updates
        self.dt         = 1     # Amount of time between last two updates (us)
        self.prev_time  = ticks_us()

    def update(self):
        '''Runs one update step on the encoder's timer counter to keep
           track of the change in count and check for counter reload'''
        # How much time has passed since the last update
        now = ticks_us()
        self.dt = ticks_diff(now, self.prev_time)
        self.prev_time = now

        # How much the counter changed since the last update
        count = self.tim.counter()
        self.delta = count - self.prev_count
        self.prev_count = count

        # Fix the counter rolling over.
        # A jump bigger than half the counter range means it wrapped around.
        if self.delta > (self.AR + 1) / 2:
            self.delta -= (self.AR + 1)        # counted past AR, wrapped to 0
        elif self.delta < -(self.AR + 1) / 2:
            self.delta += (self.AR + 1)        # counted below 0, wrapped to AR

        self.position += self.delta

    def get_position(self):
        '''Returns the most recently updated value of position as determined
           within the update() method'''
        return self.position

    def get_velocity(self):
        '''Returns a measure of velocity using the the most recently updated
           value of delta as determined within the update() method.
           dt is in microseconds, so multiply by 1,000,000 to get counts
           per SECOND, which is what main.py labels as "cnt/s".'''
        if self.dt == 0:
            return 0
        return self.delta * 1_000_000 / self.dt

    def zero(self):
        '''Sets the present encoder position to zero and causes future updates
           to measure with respect to the new zero position'''
        self.position = 0
        self.delta = 0
        # Remember where the counter is right now so the next update()
        # only measures movement that happens after this point
        self.prev_count = self.tim.counter()
        self.prev_time = ticks_us()
        