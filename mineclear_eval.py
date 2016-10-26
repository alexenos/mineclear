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
        self.actions = []
        self.move = {'north': -1, 'south': 1, 'east': 1, 'west': -1}
        self.shoot = {'alpha':[(-1, -1), (-1,  1), (1, -1), (1, 1)],
                      'beta': [(-1,  0), ( 0, -1), (0,  1), (1, 0)],
                      'gamma':[(-1,  0), ( 0,  0), (1,  0)],
                      'delta':[( 0, -1), ( 0,  0), (0,  1)]
                     }
        self.field = [] # This is an absolute field
        self.field_size = {'x': 0, 'y': 0}
        self.lowercase_offset = -96 # a = 97 = 1 km
        self.uppercase_offset = -38 # A = 65 = 27 km
    def setup(self, ffile, sfile):
        """ Parses the files and initialies the action list and field """
        # Parse field file and evalute depth
        with open(ffile) as ff:
            field_lines = [l.rstrip('\n') for l in ff.readlines()] # Get without newline characters
            i = 0
            for l in field_lines:
                self.field.append([])
                j = 0
                for c in l:
                    # Detect mine
                    if (c in string.ascii_lowercase) or (c in string.ascii_uppercase):
                        self.field[i].append(self.char_to_depth(c))
                    else: # No mine detected
                        if c != '.':
                            print "Warning: Character " + c + " implies no mine in field at: (" + str(i) + ", " + str(j) + ")"
                        self.field[i].append(None)
                    j = j + 1
                self.field_size['x'] = j if (j > self.field_size['x']) else self.field_size['x']
                i = i + 1
            self.field_size['y'] = i
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
        elif char in string.ascii_lowercase:
            d = ord(char) + self.uppercase_offset
        else: # Character has no determined depth
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
        # No checks: All potential field failure are gracefully interpreted
        # Script Checks
        i = 0
        for s in self.actions:
            if len(s) > 2:
                print "Error: A maximum of two actions per step are allowed: line " + str(i)
                return False
            elif len(s) > 1:
                # Check first action is type shooting
                if s[0] not in self.shoot.keys():
                    print "Error: First of two actions must be a firing pattern: " + s[0]
                    return False
                # Check second is type movement
                if s[1] not in self.move.keys():
                    print "Error: Second of two actions must be a movement pattern: " + s[1]
                    return False
            elif len(s) > 0:
                # Check action is of either type
                if (s[0] not in self.move.keys()) and (s[0] not in self.shoot.keys()):
                    print "Error: Unknown action: " + s[0]
            else:
                continue
        return True





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
        sys.exit(-1)
    # else: continue
    # Play game to completion
    #result, score = game.play()
    # Print result
    #print result + "(" + str(score) + ")"
    return 0 # Successful

def parse_user_args() :
   """ Parses the user arguments and options for the script """
   parser = ap.ArgumentParser(description="Evalues and scores students mine clearing scripts",
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
