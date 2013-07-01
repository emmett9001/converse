import constants


class Command(object):
    def __init__(self, definition, description):
        self.definition = definition
        self.description = description

        def validator(tokens):
            required_params = [token for token in self.definition.split() if token.startswith("<") and token.endswith(">")]
            if len(tokens) - 1 < len(required_params):
                return False
            return True
        self.validate = validator

        self.name = definition.split()[0]

        self.new_menu = ''

    def __str__(self):
        return "%s\n    %s" % (self.definition, self.description)

    def set_validate_function(self, func):
        self.validate = func

    def set_run_function(self, func):
        self.run = func


class BackCommand(Command):
    def __init__(self, tomenu):
        super(BackCommand, self).__init__('back', 'Back to the %s menu' % tomenu)
        self.new_menu = tomenu

        def _run(tokens):
            return constants.CHOICE_BACK
        self.set_run_function(_run)

        self.default_run = _run


class QuitCommand(Command):
    def __init__(self, name):
        super(QuitCommand, self).__init__('quit', 'Quit %s' % name)

        def _run(tokens):
            return constants.CHOICE_QUIT
        self.set_run_function(_run)

        self.default_run = _run