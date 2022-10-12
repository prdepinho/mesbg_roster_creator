from random import randint, choices, shuffle
import math

class Hero:
    def __init__(self, quantity, name, points, retinue, options):
        self.quantity = quantity
        self.name = name
        self.points = points
        self.retinue = retinue
        self.options = options
    def copy(hero):
        return Hero(hero.quantity, hero.name, hero.points, hero.retinue, hero.options)
    def __hash__(self):
        return hash(self.name + self.options)

class Warrior:
    def __init__(self, quantity, name, points, bow, options):
        self.quantity = quantity
        self.name = name
        self.points = points
        self.bow = bow
        self.options = options
    def copy(warrior):
        return Warrior(warrior.quantity, warrior.name, warrior.points, warrior.bow, warrior.options)
    def __hash__(self):
        return hash(self.name + self.options)

# This program is designed to use your own collection of MESBG to create a roster that is optimized to 
# use all your heroes' retinue capacity and fill up all your points without losing time figuring
# out how you are going to close that 6 points gap in your roster.
# It's quick, it's efficient, and it's quite random.

# How to use:
# Edit the target points and bow ratio below and input your collection separated as heroes and warriors.
# For each type of model, input the quantity you have of it, its name, points, the retinue capacity, bow, and options.
# Then, run on the terminal:
# python3 mesbg_roster_creator.py

# Note: this program does not take into consideration any army-building special rules, like Elrond's, for example.
# Note: this program does not work with alliances.
# Note: if you have two versions of the same hero, like armored and unarmored Glorfindel, for example, then they might
# appear together in the same roster. If you want to assure that only one appears, then take out the other one from
# the collection.

# If you didn't like how the roster came out, with too many banners for example, then tweak your collection,
# try again, and see what happens.
# If you are using the Serpent Horde, then you might want to change bow_ratio to 1 / 2.
# If you want to use a specific hero, like Elrond for example, then take most of the other heroes away and edit
# your Knights to have bow set as False (which will take his army building ability into effect).
# Even if you retry a dozen times you'll still save time compared with creating the roster by yourself.

target_points = 500
bow_ratio = 1 / 3

heroes = [
        #         no,  name,                  points,     retinue,    options
        Hero (    1,   "Elrond",              180,        18,         "Heavy Armor" ),
        Hero (    1,   "Glorfindel",          145,        15,         "" ),
        Hero (    1,   "Glorfindel",          160,        15,         "Armor of Gondolin" ),
        Hero (    2,   "High Elf Captain",    80,         12,         "Shield" ),
        Hero (    1,   "High Elf Captain",    95,         12,         "Horse, Lance, Elf Bow" ),
        ]

warriors = [
        #         no,  name,                  points,     bow,        options
        Warrior ( 10,  "High Elf Warrior",    9,          False,      "" ),
        Warrior ( 8,   "High Elf Warrior",    11,         True,       "Elf Bow" ),
        Warrior ( 9,   "High Elf Warrior",    11,         False,      "Shield, Spear" ),
        Warrior ( 1,   "High Elf Warrior",    41,         True,       "Bow, Horn" ),
        Warrior ( 2,   "High Elf Warrior",    34,         False,      "Banner" ),
        Warrior ( 4,   "Rivendell Knight",    21,         True,       "" ),
        Warrior ( 1,   "Rivendell Knight",    46,         True,       "Banner" ),
        ]

class Army:
    def __init__(self, target_points):
        self.target_points = target_points
        self.heroes = []
        self.warriors = []
        self.roster = []
        for hero in heroes:
            for i in range(hero.quantity):
                self.heroes.append(Hero.copy(hero))
        shuffle(self.heroes)
        for warrior in warriors:
            for i in range(warrior.quantity):
                self.warriors.append(Warrior.copy(warrior))
        shuffle(self.warriors)
        self.total_bows = 0
        self.total_warriors = 0
        self.total_points = 0

    def generate_roster(self):
        number_of_rosters = randint(1, 6)
        i = 0
        while i <= number_of_rosters and len(self.heroes) > 0 and len(self.warriors) > 0:
            warband = self.generate_warband()
            
            if self.target_points < self.total_points:
                self.total_bows -= warband.bows
                self.total_points -= warband.points
                self.total_warriors -= warband.quantity
                return self.roster
            else:
                self.roster.append(warband)
                i += 1

        return self.roster

    def generate_warband(self):
        warband = Warband()
        warband.hero = self.heroes.pop()
        warband.points += warband.hero.points
        self.total_points += warband.hero.points

        while warband.quantity < warband.hero.retinue and len(self.warriors) > 0:
            warrior = self.warriors.pop()
            if warrior.bow and self.total_bows >= math.floor(self.total_warriors * bow_ratio):
                pass
            else:
                if self.target_points < self.total_points + warrior.points:
                    return warband
                if warrior.__hash__() not in warband.warriors:
                    warband.warriors[warrior.__hash__()] = [0, warrior]
                warband.warriors[warrior.__hash__()][0] += 1
                warband.points += warrior.points
                self.total_points += warrior.points
                warband.quantity += 1
                self.total_warriors += 1
                if warrior.bow:
                    warband.bows += 1
                    self.total_bows += 1
        return warband


class Warband:
    def __init__(self):
        self.hero = None
        self.warriors = {}
        self.points = 0
        self.quantity = 0
        self.bows = 0


def print_warband(warband):
    print(" # %s (%s), %d warriors, [%d pts]:" % (warband.hero.name, warband.hero.options, warband.quantity, warband.points))
    for hash in warband.warriors:
        quantity = warband.warriors[hash][0]
        warrior = warband.warriors[hash][1]
        print("  %d x %s (%s)" % (quantity, warrior.name, warrior.options))

def print_army(army):
    print(" Roster %d warriors, %d bows [%d pts]:" % (army.total_warriors, army.total_bows, army.total_points))
    for warband in army.roster:
        print_warband(warband)


def genetic_level(army):
    level = 0
    for warband in army.roster:
        level += warband.hero.retinue - warband.quantity
    level += army.target_points - army.total_points 
    return level


if __name__ == "__main__":
    total_candidates = 10000
    army = Army(target_points)
    army.generate_roster()

    for i in range(total_candidates):
        candidate = Army(target_points)
        candidate.generate_roster()
        if genetic_level(candidate) == 0:
            army = candidate
            break
        else:
            if genetic_level(candidate) < genetic_level(army):
                army = candidate

    print_army(army)

