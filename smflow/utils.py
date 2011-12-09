class Util():
    def __init__(self, crew, config):
        self.crew = crew
        self.config = config

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

