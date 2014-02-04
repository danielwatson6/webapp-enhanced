__all__ = ["db", "server", "utils"]


class ValidationError(Exception):
	"""Error thrown by validators when the given value is bad."""
	
	def __init__(self, msg, validator=None, field=None):
		super(ValidationError, self).__init__(msg)
		logging.error(msg + '\n' + "Validator: %r" % validator + ", input: %s" % field)
