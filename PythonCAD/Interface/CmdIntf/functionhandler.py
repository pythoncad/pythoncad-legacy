

class FunctionHandler(object):
    '''
    This object contains all known commands.
    Commands are registered by "registerCommand" before the are available.
    Evaluation of commands or expressions is done by "evaluate"
    '''

    def __init__(self, edit_ctrl):
        '''
        Defines an dictionary containing all known commands.
        Member 'registerCommand' add's a command to the table.
        Member 'evaluate' execute a command by call its call-back or evaluates an expression.
        '''
        # edit control
        self.__edit_ctrl = edit_ctrl
        # current value
        self._value = None
        # command table
        self._command_table = {}


    def registerCommand(self, name, callback):
        '''
        Register a command with it's callback in the command table.
        Commands are executed by a call to the evaluate function.
        '''
        # a command is at least one character
        if len(name) > 0:
            # the callback is not None
            if not callback is None:
                # commands are always defined in upper case
                self._command_table[name.upper()] = callback


    def evaluate(self, expression):
        '''
        Looks up the expression from the command table.
        If a command is found, it's callback function is called.
        If it is not a command the expression is evaluated.
        Return: command exit, the evaluated expression or "*error*"
        '''
        # commands are always defined in upper case
        command = expression.upper()
        # echo on the comand line
        self.__edit_ctrl.setText(command)
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
        # show result
        if self._value is None:
            self.__edit_ctrl.clear()
        else:
            self.__edit_ctrl.setText(str(self._value))
        return self._value


