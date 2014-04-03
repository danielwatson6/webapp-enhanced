import controllers

from lib import server


# Fetch all controllers
app = server.Application(controllers.all_classes())


app.initialize(debug = True)
