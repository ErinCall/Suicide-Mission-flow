#!/usr/bin/env python

import yaml
import smflow.utils
from smflow import (
    defenders,
    shield_vulnerables,
    weapons_vulnerables,
    long_walk_vulnerables,
    hold_the_line_vulnerables,
)

crew_file = open('crew.yaml')
crew = yaml.load(crew_file.read())

config_file = open('config.yaml')
config = yaml.load(config_file.read())

util = smflow.utils.Util(crew, config)

def armor_check():
    if not config['Armor upgrade']:
        util.kill_char('Jack', 'Armor check')

def shield_check():
    if not config['Shield upgrade']:
        util.kill_one_of(shield_vulnerables, 'Shield check')

def weapons_check():
    if not config['Cannon upgrade']:
        util.kill_one_of(weapons_vulnerables, 'Cannon check')

def vents():
    util.confirm_alive('Vents')
    util.confirm_alive('Fireteam 1')

    if config['Vents'] not in ('Tali', 'Legion', 'Kasumi') \
    or not util.role_is_loyal('Vents') \
    or config['Fireteam 1'] not in ('Miranda', 'Jacob', 'Garrus') \
    or not util.role_is_loyal('Fireteam 1'):
        util.kill_role('Vents')

def long_walk():
    util.confirm_alive('Biotic')
    util.confirm_alive('Long walk party 1')
    util.confirm_alive('Long walk party 2')
    util.confirm_alive('Fireteam 2')
    if config['Biotic'] not in ('Jack', 'Morinth', 'Samara') \
    or not util.role_is_loyal('Biotic'):
        party_members = (config['Long walk party 1'], config['Long walk party 2'])
        util.kill_one_of(long_walk_vulnerables, 'Long-walk party member',
                                eligible=lambda x: x in party_members)

    if config['Fireteam 2'] != 'Miranda' \
    and (config['Fireteam 2'] not in ('Jacob', 'Garrus') \
                        or not util.role_is_loyal['Fireteam 2']):
        util.kill_role('Fireteam 2')

def the_crew():
    if config['Delay missions'] == 0:
            util.other_state.append('All crew survive')
    elif config['Delay missions'] <= 3:
            util.other_state.append('Half the crew survives')
    else:
        util.other_state.append('Chakwas survives; all other crewmen dead')

def the_escort():
    if config['Crew escort']:
        util.confirm_alive('Crew escort')
    # we'll "kill" them here to ensure they aren't used elsewhere, then stick them
    # in other_state if they're loyal and can survive
        util.kill_role('Crew escort')
        if util.role_is_loyal('Crew escort'):
            util.other_state.append(config['Crew escort'])
            util.other_state.append('All crew survive')
    else:
        util.other_state = util.other_state[0:-1]
        util.other_state.append('All crewmen dead (including Chakwas)')

def final_fight():
    for party_member in ('Final fight party 1', 'Final fight party 2'):
        util.confirm_alive(party_member)
        if not util.role_is_loyal(party_member):
            util.kill_role(party_member)

def hold_the_line():
    del defenders[config['Final fight party 1']]
    del defenders[config['Final fight party 2']]
    for defender in defenders.keys():
        if not crew[defender]: del defenders[defender]

    if defenders:
        total_strength = 0
        for defender in defenders:
            total_strength += defenders[defender]
            if util.char_is_loyal(defender):
                total_strength += 1
        avg_strength = float(total_strength)/len(defenders)
        deaths = 0
        if len(defenders) == 5:
            if 1.5 <= avg_strength < 2: deaths = 1
            elif 0.5 <= avg_strength < 1.5: deaths = 2
            elif 0 <= avg_strength < 0.5: deaths = 3
        elif len(defenders) == 4:
            if 1 < avg_strength < 2: deaths = 1
            elif 0.5 <= avg_strength <= 1: deaths = 2
            elif 0 < avg_strength < 0.5: deaths = 3
            elif 0 == avg_strength: deaths = 4
        elif len(defenders) == 3:
            if 1 <= avg_strength < 2: deaths = 1
            elif 0 < avg_strength < 1: deaths = 2
            elif 0 == avg_strength: deaths = 3
        elif len(defenders) == 2:
            if 0 < avg_strength < 2: deaths = 1
            elif 0 == avg_strength: deaths = 2
        elif len(defenders) == 1:
            if avg_strength < 2: deaths = 1

        vulnerables = filter(lambda x: not util.char_is_loyal(x)
                                and x in defenders, hold_the_line_vulnerables)
        vulnerables.extend(filter(lambda x: util.char_is_loyal(x)
                                and x in defenders, hold_the_line_vulnerables))
        util.kill_n_of(vulnerables, deaths, 'Hold the line')

armor_check()
shield_check()
weapons_check()
vents()
long_walk()
the_crew()
the_escort()
final_fight()
hold_the_line()

survivors = filter(lambda m: crew[m], [m for m in crew])
print "\n".join(sorted(survivors))
if len(survivors) < 2: print "(Shepard dies)"
if util.other_state: print "\n".join(util.other_state)
