class State():
    def __init__(self, crew, choices):
        self.crew = crew
        self.choices = choices
        self.misc_state = []

    def confirm_alive(self, role_name):
        if not self.crew[self.choices[role_name]]:
            raise Exception('%(character)s is set to be your %(role_name)s '
                    'specialist, but is already dead' % {
                    'character': self.choices[role_name],
                    'role_name': role_name})

    def confirm_alive_and_distinct(self, roles):
        for role_name in roles:
            self.confirm_alive(role_name)
        performed_roles = {}
        for role in roles:
            #c'mon just let me have ||=, just let me have ti
            performed_roles[self.choices[role]] = \
                        performed_roles.get(self.choices[role],[])
            performed_roles[self.choices[role]].append(role)
        for character in performed_roles:
            if len(performed_roles[character]) > 1:
                raise Exception('%(character)s has been assigned '
                        'multiple roles: %(roles)s' % {
                        'character': character,
                        'roles': performed_roles[character]})

    def role_is_loyal(self, role_name):
        return self.char_is_loyal(self.choices[role_name])
    def char_is_loyal(self, character):
        return self.crew[character] > 1

    def kill_role(self, role_name):
        self.kill_char(self.choices[role_name], role_name)
    def kill_char(self, char, description):
        #print 'killing %s (%s)' % (char, description)
        self.crew[char] = 0


    def kill_one_of(self, vulnerables, description, eligible=lambda x: True):
        self.kill_n_of(vulnerables, 1, description, eligible)

    def kill_n_of(self, vulnerables, deaths, description,
                            eligible=lambda x:True):
        while deaths > 0 and vulnerables:
            candidate = vulnerables[0]
            if self.crew[candidate] and eligible(candidate):
                self.kill_char(candidate, description)
                deaths -= 1
            vulnerables.remove(vulnerables[0])
