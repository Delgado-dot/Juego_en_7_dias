import db.database_manager as db

print("🧪 Creando personaje...")
db.crear_personaje("Guerrero", 100, 20, 15)

print("\n📋 Personajes:")
for p in db.obtener_personajes():
    print(p)

print("\n🏆 Agregando puntajes...")
db.guardar_puntaje(500, 1)
db.guardar_puntaje(800, 1)
db.guardar_puntaje(300, 1)

print("\n📊 Ranking del día:")
for r in db.ranking_del_dia():
    print(r)