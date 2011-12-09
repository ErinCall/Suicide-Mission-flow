class Util():
    def __init__(self, crew, config):
        self.crew = crew
        self.config = config
        self.other_state = []

    def confirm_alive(self, role_name):
        if not self.crew[self.config[role_name]]:
            raise Exception('%(character)s is set to be your %(role_name)s '
                    'specialist, but is already dead' % {
                    'character': self.config[role_name],
                    'role_name': role_name})

    def role_is_loyal(self, role_name):
        return self.char_is_loyal(self.config[role_name])
    def char_is_loyal(self, character):
        return self.crew[character] > 1

    def kill_role(self, role_name):
        self.kill_char(self.config[role_name], role_name)
    def kill_char(self, char, description):
        #print 'killing %s (%s)' % (char, description)
        self.crew[char] = 0


    def kill_one_of(self, vulnerables, description, eligible=lambda x: True):
        self.kill_n_of(vulnerables, 1, description, eligible)

    def kill_n_of(self, vulnerables, deaths, description,
                            eligible=lambda x:True):
        while deaths > 0 and vulnerables:
            candidate = vulnerables[0]
            if eligible(candidate):
                self.kill_char(candidate, description)
                deaths -= 1
            vulnerables.remove(vulnerables[0])
