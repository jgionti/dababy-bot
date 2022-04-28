from lib.database import Database

db = Database()
db.write("test", "Chungus", {"testest" : 123})
print(db.read("test", "Chungus"))

pass