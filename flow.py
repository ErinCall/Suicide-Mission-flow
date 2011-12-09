#!/usr/bin/env python

import yaml
crew_file = open('crew.yaml')
crew = yaml.load(crew_file.read())

config_file = open('config.yaml')
config = yaml.load(config_file.read())


other_state = []

defenders = {
    'Garrus':  3,
    'Grunt':   3,
    'Jack':    0,
    'Jacob':   1,
    'Kasumi':  0,
    'Legion':  1,
    'Miranda': 1,
    'Morinth': 1,
    'Mordin':  0,
    'Tali':    0,
    'Thane':   1,
    'Zaeed':   3,
}

def confirm_alive(role_name):
    if not crew[config[role_name]]:
        raise Exception('%(character)s is set to be your %(role_name)s '
                'specialist, but is already dead' % {
                'character': config[role_name], 'role_name': role_name})
def role_is_loyal(role_name):
    return char_is_loyal(config[role_name])
def char_is_loyal(character):
    return crew[character] > 1
def kill_role(role_name):
    kill_char(config[role_name], role_name)
def kill_char(char, description):
    #print 'killing %s (%s)' % (char, description)
    crew[char] = 0

#Armor check
if not config['Armor upgrade']:
    kill_char('Jack', 'Armor check')

#Shield check
if not config['Shield upgrade']:
    for vuln in ('Kasumi', 'Legion', 'Tali', 'Thane', 'Garrus', 'Zaeed',
                                                    'Grunt', 'Morinth'):
        if crew[vuln]:
            kill_char(vuln, 'Shield check')
            break

#weapons check
if not config['Cannon upgrade']:
    for vuln in ('Thane', 'Garrus', 'Zaeed', 'Grunt', 'Jack', 'Morinth'):
        if crew[vuln]:
            kill_char(vuln, 'Cannon check')
            break

#The vents
confirm_alive('Vents')
confirm_alive('Fireteam 1')

if config['Vents'] in ('Tali', 'Legion', 'Kasumi') \
and role_is_loyal('Vents') \
and config['Fireteam 1'] in ('Miranda', 'Jacob', 'Garrus') \
and role_is_loyal('Fireteam 1'):
    pass
else:
    kill_role('Vents')

#The long walk
confirm_alive('Biotic')
confirm_alive('Long walk party 1')
confirm_alive('Long walk party 2')
confirm_alive('Fireteam 2')
if config['Biotic'] not in ('Jack', 'Morinth') \
or not role_is_loyal('Biotic'):
    vulnerable = ('Thane', 'Jack', 'Garrus', 'Legion', 'Grunt', 'Jacob',
                        'Mordin', 'Tali', 'Kasumi', 'Zaeed', 'Morinth')
    for vuln in vulnerable:
        if vuln in (config['Long walk party 1'], config['Long walk party 2']):
            kill_char(vuln, 'long-walk party member')
            break
if config['Fireteam 2'] != 'Miranda' \
and (config['Fireteam 2'] not in ('Jacob', 'Garrus') \
                    or not role_is_loyal['Fireteam 2']):
    kill_role('Fireteam 2')

#The crew
if config['Delay missions'] == 0:
        other_state.append('All crew survive')
elif config['Delay missions'] <= 3:
        other_state.append('Half the crew survives')
else:
    other_state.append('Chakwas survives; all other crewmen dead')

#The escort
if config['Crew escort']:
    confirm_alive('Crew escort')
# we'll "kill" them here to ensure they aren't used elsewhere, then stick them
# in other_state if they're loyal and can survive
    kill_role('Crew escort')
    if role_is_loyal('Crew escort'):
        other_state.append(config['Crew escort'])
        other_state.append('All crew survive')
else:
    other_state = other_state[0:-1]
    other_state.append('All crewmen dead (including Chakwas)')

#The final fight
for party_member in ('Final fight party 1', 'Final fight party 2'):
    confirm_alive(party_member)
    if not role_is_loyal(party_member):
        kill_role(party_member)

#Hold the line
del defenders[config['Final fight party 1']]
del defenders[config['Final fight party 2']]
for defender in defenders.keys():
    if not crew[defender]: del defenders[defender]

if defenders:
    total_strength = 0
    for defender in defenders:
        total_strength += defenders[defender]
        if char_is_loyal(defender):
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

    vulnerability_order = ['Mordin', 'Tali', 'Kasumi', 'Jack', 'Miranda',
                            'Jacob', 'Garrus', 'Morinth', 'Legion', 'Thane',
                            'Zaeed', 'Grunt']
    vulnerability = filter(lambda x: not char_is_loyal(x)
                                and x in defenders, vulnerability_order)
    vulnerability.extend(filter(lambda x: char_is_loyal(x)
                                and x in defenders, vulnerability_order))
    while deaths > 0:
        kill_char(vulnerability[0], 'Hold the line')
        vulnerability.remove(vulnerability[0])
        deaths -= 1


survivors = filter(lambda m: crew[m], [m for m in crew])
print "\n".join(sorted(survivors))
if len(survivors) < 2: print "(Shepard dies)"
if other_state: print "\n".join(other_state)
