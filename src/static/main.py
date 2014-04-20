import controllers

from lib.server import webapp_enhanced


app = webapp_enhanced()

app.route(controllers.all_classes())

app.start()
