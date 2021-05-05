'''
Provide RPG style dice spec parsing and number generation.
Many games use a random number specification based on a number of, and type of dice to roll, with an optional 
constant to be added to the final number.  

e.g. 3D4+2 would mean roll 3 4-sided dice, add the numbers together (sum) and add 2 to the final sum.

A dice spec can be a single int, meaning generate a random number between 1 and int
or, a range "2-5", meaning generate a number between 2 and 5, this is the same as 1D4+1
or, 4D8+3, this means roll 4 8-sided dice, sum the rolls and add 3 to the final

the dice rolles can be modified by +, -, *, /.  Although most games only use addition(+) and subtraction(-)

'''
import random
import re

def roll(spec, prev={}):
    if spec in prev:
        d=prev[spec]
        return d.roll()
    if isinstance(spec, Dice):
        return spec.roll()
    else:
        d=Dice()
        d.parse(spec)
        prev[spec] = d
        return d.roll()
    raise ValueError

class Dice:
    _dice_re = re.compile('^(\d*)[dD](\d*)(.*)$')
    _range_re = re.compile('^(\d+)-(\d+)$')
    _int_re = re.compile('^(\d+)$')

    def __init__(self, spec=None):
        random.seed()
        self.spec = spec
        self.number_of_dice = 1
        self.dice_max = 6
        self.ops = []
        if spec:
            self.parse(spec)

    def __str__(self):
        return self.spec

    def __repr__(self):
        return str((self.spec,
            self.number_of_dice,
            self.dice_max,
            self.ops))


    def parse(self, spec):
        '''Parse dice specification of the form of 3d4+2*100
        Roll 3 6sided dice and add 2 to the sum
        '''
        # if int then gen random number
        if isinstance(spec, int):
            self.dice_max = spec
            return
        if not spec or not len(spec):
            return
        parts = Dice._int_re.match(spec)
        if parts:
            self.dice_max = int(spec);
            return
        #compress spaces
        spec = spec.replace(' ', '')
        self.spec = spec
        #is this a range spec? goblin htk is 2-5, same as 1d4+1
        parts = Dice._range_re.match(spec)
        if parts:
            parts = parts.groups()
            self.number_of_dice = 1
            self.dice_max = int(parts[1]) - int(parts[0]) + 1 # 2-5 := 5-2 = 3 + 1 := 1d4
            acc = int(parts[0]) - 1 # 2-5 := 2-1 = 1 := +1
            self.ops.append(("+", acc))
            return
        #is this a classic DnD dice spec?
        parts = Dice._dice_re.match(spec)
        if parts:
            parts = parts.groups()
        self.number_of_dice = int(parts[0]) if parts[0] else 1
        self.dice_max = int(parts[1]) if parts[1] else 6
        if parts[2]:
            op=None
            acc=-1
            for c in parts[2]+'@': #use @ as terminator to save last op
                if c in ' \t\n':
                    continue
                if c in '+-*/%@':
                    if op:
                        self.ops.append((op, acc))
                    op = c
                    acc= 0
                elif c in '1234567890':
                    acc = acc * 10 + ord(c) - ord('0')


    def roll(self, spec=None):
        if spec:
            d=Dice()
            d.parse(spec)
            return d.roll()

        if not self.spec:
            return 0

        dmg = 0
        for x in range(self.number_of_dice):
            dmg = dmg + random.randint(1, self.dice_max)
        for op in self.ops:
            if op[0] == '+':
                dmg += op[1]
            elif op[0] == '-':
                dmg -= op[1]
            elif op[0] == '*':
                dmg *= op[1]
            elif op[0] == '/':
                dmg = int((dmg / op[1]) +.5)
            elif op[0] == '%':
                dmg = dmg % op[1]
            else:
                raise NotImplementedError('Operation '+op[0])

        return dmg


    def __iter__(self):
        return self


    def __next__(self):
        return self.roll()


if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--repeat", type=int, help="",default=1)
    parser.add_argument("dicespec", type=str, nargs='+',
                                help="3d6[+1]")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        d = Dice('3d6')
        print(d.roll())
    else:
        for spec in args.dicespec:
            for n in range(0,args.repeat):
                d = Dice(spec)
                print(d.roll())
