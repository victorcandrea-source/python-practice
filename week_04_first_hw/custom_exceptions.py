# This is a custom exception class that inherits from the built-in Exception class.
class custom_exception(Exception):
   
   def __init__(self, message):
        self.message = message
        super().__init__(self.message)

   def invalid_input_error(self):
        return f"Invalid input: {self.message}"

   def TaskNotFoundError(self):
        return f"Task not found: {self.message}"
   
   def InvalidStatusTransitionError(self):
        return f"Invalid status transition: {self.message}"
   
   def EmptyUndoStackError(self):
        return f"Undo stack is empty: {self.message}"
   
   def CantDecodeFileError(self):
        return f"Cannot decode file: {self.message}"