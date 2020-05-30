import random, glob
import requests
import xml.etree.ElementTree as ET

class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Player():
    def __init__(self):
        self.name = None
        self.faction = None
        self.player = None

    def __str__(self):
        return f"{self.name} {self.faction} {self.player}"

class GameInstance(metaclass=Singleton):
    
    def __init__(self):
        self.MAX_PLAYERS = 5 
        self.waiting = []
        self.factionMats = []
        self.playerMats = []

    def reset(self):
        self.waiting = []        
        self.factionMats = []
        self.playerMats = []
        
    def addWaiting(self, name):
        if name in self.waiting:
            self.lastError = f"{name} is already waiting"
            return 1
        self.waiting.append(name)
        return 0
        
    def removeWaiting(self, name):
        if name in self.waiting:
            self.waiting.remove(name)
            return 0
        self.lastError = f"{name} is not currently waiting"
        return 1

    def pickRandom(self):
        random.shuffle(self.waiting)
        return self.waiting.pop()
