from szolanc_game import create_app, socketio

app = create_app()

socketio.run(app)