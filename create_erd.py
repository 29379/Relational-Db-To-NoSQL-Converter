import psycopg2
from eralchemy import render_er

database_uri = "postgresql+psycopg2://postgres:123456@localhost/zbd_czy_dojade"

output_path = "diagram.png"

render_er(database_uri, output_path)
