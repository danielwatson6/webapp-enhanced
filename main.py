import controllers

from lib.server import Application

#
# This is the main script for the application.
# It simply consists of an application instance
# that maps all of the controllers (arguments for
# the constructor).
# 
# The default argument simply takes all regular
# controllers to the main application.
# If you don't want all of the existing controllers
# in the application, import all the ones to be in,
# and instead of having the default argument.
# as argument, add all of the controllers as arguments.
# You may also include as arguments other controllers
# before the default argument.
#

app = Application(*controllers.all_classes())
