

class FunctionHandler(object):

    def __init__(self, document):
        # reference to the document object
        self._document = document
        # current value
        self._value = None
        # command table
        self._command_table = {}


    def RegisterCommand(self, name, callback):
        if len(name) > 0:
            self._command_table[name] = callback


    def Evaluate(self, expression):
        result = None
        # commands are allways defined in upper case
        command = expression.upper()
        # is it a command from the command table?
        if self._command_table.has_key(command):
            # call function
            self._value = self._command_table[command]()
        else:
            try:
                # let python evaluate expression
                self._value = eval(expression)
            except:
                self._value = "*error*"
        return self._value


