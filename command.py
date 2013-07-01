class Command():
    def __init__(self, definition):
        self.definition = definition

        def validator(tokens):
            required_params = [token for token in self.definition.split() if token.startswith("<") and token.endswith(">")]
            if len(tokens) - 1 < len(required_params):
                return False
            return True
        self.validate = validator

        self.name = definition.split()[0]

        self.new_menu = ''

    def set_validate_function(self, func):
        self.validate = func

    def set_run_function(self, func):
        self.run = func
