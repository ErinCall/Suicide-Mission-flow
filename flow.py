#!/usr/bin/env python

import yaml
import smflow.state
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

state = smflow.state.State(crew, config)

def armor_check():
    if not config['Armor upgrade']:
        state.kill_char('Jack', 'Armor check')

def shield_check():
    if not config['Shield upgrade']:
        state.kill_one_of(shield_vulnerables, 'Shield check')

def weapons_check():
    if not config['Cannon upgrade']:
        state.kill_one_of(weapons_vulnerables, 'Cannon check')

def vents():
    state.confirm_alive_and_distinct(('Vents', 'Fireteam 1'))

    if config['Vents'] not in ('Tali', 'Legion', 'Kasumi') \
    or not state.role_is_loyal('Vents') \
    or config['Fireteam 1'] not in ('Miranda', 'Jacob', 'Garrus') \
    or not state.role_is_loyal('Fireteam 1'):
        state.kill_role('Vents')

def long_walk():
    state.confirm_alive_and_distinct(('Biotic', 'Long walk party 1',
                                'Long walk party 2', 'Fireteam 2'))
    if config['Biotic'] not in ('Jack', 'Morinth', 'Samara') \
    or not state.role_is_loyal('Biotic'):
        party_members = (config['Long walk party 1'], config['Long walk party 2'])
        state.kill_one_of(long_walk_vulnerables, 'Long-walk party member',
                                eligible=lambda x: x in party_members)

    if config['Fireteam 2'] != 'Miranda' \
    and (config['Fireteam 2'] not in ('Jacob', 'Garrus') \
                        or not state.role_is_loyal['Fireteam 2']):
        state.kill_role('Fireteam 2')

def the_crew():
    if config['Delay missions'] == 0:
            state.misc_state.append('All crew survive')
    elif config['Delay missions'] <= 3:
            state.misc_state.append('Half the crew survives')
    else:
        state.misc_state.append('Chakwas survives; all other crewmen dead')

def the_escort():
    if config['Crew escort']:
        state.confirm_alive('Crew escort')
    # we'll "kill" them here to ensure they aren't used elsewhere, then stick them
    # in misc_state if they're loyal and can survive
        state.kill_role('Crew escort')
        if state.role_is_loyal('Crew escort'):
            state.misc_state.append(config['Crew escort'])
            state.misc_state.append('All crew survive')
    else:
        state.misc_state = state.misc_state[0:-1]
        state.misc_state.append('All crewmen dead (including Chakwas)')

def final_fight():
    roles = ('Final fight party 1', 'Final fight party 2')
    state.confirm_alive_and_distinct(roles)
    for party_member in roles:
        if not state.role_is_loyal(party_member):
            state.kill_role(party_member)

def hold_the_line():
    del defenders[config['Final fight party 1']]
    del defenders[config['Final fight party 2']]
    for defender in defenders.keys():
        if not crew[defender]: del defenders[defender]

    if defenders:
        total_strength = 0
        for defender in defenders:
            total_strength += defenders[defender]
            if state.char_is_loyal(defender):
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

        vulnerables = filter(lambda x: not state.char_is_loyal(x)
                                and x in defenders, hold_the_line_vulnerables)
        vulnerables.extend(filter(lambda x: state.char_is_loyal(x)
                                and x in defenders, hold_the_line_vulnerables))
        state.kill_n_of(vulnerables, deaths, 'Hold the line')

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
if state.misc_state: print "\n".join(state.misc_state)
