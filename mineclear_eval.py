#! /usr/bin/env python
# dax garner

"""
Evaluates and scores students mine clearing scripts.
"""

import sys
import os
import argparse as ap
import string

# Defines game object
class Game:
    def __init__(self):
        """ Initializes game with nothing to do """
        self.setup_valid = False
        self.actions = []
        self.move = {'north': [0, -1], 'south': [0, 1], 'east': [1, 0], 'west': [-1, 0]}
        self.shoot = {'alpha':[[-1, -1], [-1,  1], [1, -1], [1, 1]],
                      'beta': [[-1,  0], [ 0, -1], [0,  1], [1, 0]],
                      'gamma':[[-1,  0], [ 0,  0], [1,  0]],
                      'delta':[[ 0, -1], [ 0,  0], [0,  1]]
                     }
        self.field = []
        self.ship = (0, 0, 0)
        self.lowercase_offset = -96 # a = 97 = 1 km
        self.uppercase_offset = -38 # A = 65 = 27 km
        self.success = False
        self.score = 0
        self.shoot_penalty = 0
        self.move_penalty = 0
        self.shoot_init = 0
        self.move_init = 0
    def setup(self, ffile, sfile):
        """ Parses the files and initialies the action list and field """
        # Parse field file and evalute depth
        with open(ffile) as ff:
            field_lines = [l.rstrip('\n') for l in ff.readlines()] # Get without newline characters
            i = 0
            for l in field_lines:
                j = 0
                for c in l:
                    # Detect mine
                    if (c in string.ascii_lowercase) or (c in string.ascii_uppercase):
                        # Add to field
                        self.field.append([j, i, self.char_to_depth(c)])
                        # Update starting score
                        self.score += 10
                        self.shoot_init += 5
                        self.move_init += 3
                    else: # No mine detected
                        if c != '.':
                            print "Warning: Character " + c + " implies no mine in field at: (" + str(i) + ", " + str(j) + ")"
                    j = j + 1
                i = i + 1
        # Parse script action list
        with open(sfile) as sf:
            action_lines = sf.readlines()
            for l in action_lines:
                self.actions.append(l.split())
    def char_to_depth(self, char):
        """ Evaluates a character in the game as a integer depth level """
        d = 0
        if char in string.ascii_lowercase:
            d = ord(char) + self.lowercase_offset
        elif char in string.ascii_uppercase:
            d = ord(char) + self.uppercase_offset
        else: # Character has no determined depth
            "Warning: Unknown object, assumed not to be a mine: " + c
            d = 0
        return d
    def depth_to_char(self, depth):
        """ Evaluates an integer depth level in the game as an ascii character """
        c = '*'
        if (depth > 0) and (depth <= 26):
            c = chr(depth - self.lowercase_offset)
        elif (depth > 26) and (depth <= 52):
            c = chr(depth - self.uppercase_offset)
        elif depth > 52:
            print "Warning: Depth exceeds detectable limit of 52 km: " + str(depth)
            c = '%' # for debugging purposes
        else: # A mine is at level or above
            c = '*'
        return c
    def valid(self):
        """ Checks the inputs to the game are valid prior to playing """
        # Field Checks
        if not self.field:
            print "Warning: No mines... you've already won!"
        # Script Checks
        i = 0
        for s in self.actions:
            if len(s) > 2:
                print "Error: A maximum of two actions per step are allowed: line " + str(i)
                return False
            elif len(s) > 0:
                m = 0
                sh = 0
                for a in s:
                    # Check action is of either type
                    if (a not in self.move.keys()) and (a not in self.shoot.keys()):
                        print "Error: Unknown action: " + a
                        return False
                    if a in self.move.keys():
                        m += 1
                    if a in self.shoot.keys():
                        sh += 1
                if (m > 1) or (sh > 1):
                    print "Error: Cannot shoot or move twice in one step: " + s[0] + " " + s[1]
                    return False
            else:
                continue
        self.setup_valid = True
        return True

    def init(self):
        # Set ship location offset and update mine locations
        if self.field:
            self.ship = (sum(m[0] for m in self.field)/len(self.field), sum(m[1] for m in self.field)/len(self.field))
            print self.ship
            for m in self.field:
                m[0] = m[0] - self.ship[0]
                m[1] = m[1] - self.ship[1]
        else:  # strange case
            self.ship = (0, 0)

    def play(self):
        """ Cyclical operations of the game after a valid setup """
        if not self.setup_valid:
            print "Error: Game was not properly setup"
            return "fail", 0
        self.init()
        i = 1
        while(not self.end()):
            print "Step " + str(i) + '\n'
            self.print_field()
            self.step()
            self.print_field()
            i = i + 1
        result = "pass" if self.success else "fail"
        return result, self.score

    def end(self):
        """ Checks for all end conditions and sets score """
        # 2 - script complete
        if not self.actions:
            self.success = True
            if self.field:
                self.success = False
                self.score = 0
            return True
        # 3 - no more mines
        if not self.field:
            self.success = True
            if self.actions:
                self.success = True
                self.score = 1
            return True
        # 1 - passed mine
        if min(m[2] for m in self.field) <= 0:
            self.success = False
            self.score = 0
            return True
        # 4 - conditions 2 & 3, already checked
        return False

    def print_field(self):
        """ Displays the current field """
        if not self.field: # base case
            print '.\n'
            return
        # else: figure it out
        # Get max abs of x, y axis
        x = max(abs(m[0]) for m in self.field)
        y = max(abs(m[1]) for m in self.field)
        mxy = [[m[0], m[1]] for m in self.field]
        for j in range(-y, y + 1):
            display = ""
            for i in range(-x, x + 1):
                index = [idx for idx, xy in enumerate(mxy) if xy == [i, j]]
                if index:
                    display += self.depth_to_char(self.field[index[0]][2])
                else:
                    display += '.'
            print display
        print ""

    def step(self):
        """ Executes the actions and updates the relative field """
        # Get and print action
        act = self.get_action()
        for a in act:
            self.execute(a)
        self.drop()
    def get_action(self):
        """ Gets the next action and prints """
        act = self.actions[0]
        self.actions = self.actions[1:] # Remove action
        display = ""
        for a in act:
            display += a + " "
        if not act:
            display = "no action"
        print display + '\n'
        return act
    def execute(self, act):
        """ Updates the field based on the action """
        mxy = [[m[0], m[1]] for m in self.field]
        if act in self.shoot.keys():
            for t in self.shoot[act]:
                index = [idx for idx, xy in enumerate(mxy) if xy == t]
                if index:
                    del self.field[index[0]]
                # else: continue
            # Update Score
            if self.shoot_penalty <= self.shoot_init:
                if (self.shoot_penalty + 5) <= self.shoot_init:
                    self.shoot_penalty += 5
                    self.score -= 5
                else:
                    self.score -= self.shoot_init - self.shoot_penalty
                    self.shoot_penalty = self.shoot_init
        elif act in self.move.keys():
            # Move ship
            move = self.move[act]
            for m in self.field:
                m[0] -= move[0]
                m[1] -= move[1]
            # Update Score
            if self.move_penalty <= self.move_init:
                if (self.move_penalty + 2) <= self.move_init:
                    self.move_penalty += 2
                    self.score -= 2
                else:
                    self.score -= self.move_init - self.move_penalty
                    self.move_penalty = self.move_init
        else: # do nothing
            pass
    def drop(self):
        for m in self.field:
            m[2] -= 1

def main():
    """ Top-level executing function """
    # Parse user arguments
    args = parse_user_args()
    # Check user arguments
    validate_args(args)
    # Setup and define game
    game = Game()
    game.setup(args.field, args.script)
    # Check for valid game
    if not game.valid():
        print "Error: Game setup is not valid"
        sys.exit(-1)
    # else: continue
    # Play game to completion
    result, score = game.play()
    # Print result
    print result + " (" + str(score) + ")"
    return 0 # Successful

def parse_user_args() :
   """ Parses the user arguments and options for the script """
   parser = ap.ArgumentParser(description="Evalues and scores students' mine clearing scripts",
         formatter_class=ap.ArgumentDefaultsHelpFormatter)
   parser.add_argument('field', type=str, help="Field input file",
         default="field1.txt")
   parser.add_argument('script', type=str, help="Script input file",
         default="script1.txt")
   return parser.parse_args()

def validate_args(args):
    """ Validates the input arguments """
    if not os.path.isfile(args.field):
        print "Error: The field file does not exist: " + args.field
        sys.exit(-1)
    if not os.path.isfile(args.script):
        print "Error: The script file does not exist: " + args.script
        sys.exit(-1)

# Allows the script to act like an executable
if __name__ == "__main__":
    sys.exit(main())
