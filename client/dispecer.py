import json
import os
import redis
import uuid

# Adresa Redis vine din variabile de mediu (vezi README)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "30474"))

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    r.ping()
    print("[DISPECER] Conectat cu succes la Redis!")
except Exception as e:
    print("[DISPECER] Eroare fatala de retea:", e)
    exit()

r.delete('coada_sarcini')
r.delete('coada_procesare')
r.delete('coada_rezultate')
r.delete('numar_total_pachete') # stergem si panoul vechi
print("[DISPECER] Am curatat cozile vechi. Incepem un test nou!")


NUMAR_PACHETE = 2500
START_BASE = 100000
INTERVAL_SIZE = 10000

r.set('numar_total_pachete', NUMAR_PACHETE)
print(f"[DISPECER] Am anuntat in Redis ca trimit {NUMAR_PACHETE} pachete...")

print("[DISPECER] Generez pachetele local si le impachetez...")

conducta = r.pipeline()

for i in range(NUMAR_PACHETE):
    
    start_interval = START_BASE + (i * INTERVAL_SIZE)
    end_interval = start_interval + INTERVAL_SIZE
    
    sarcina = {
        'id': str(uuid.uuid4()),
        'start': start_interval,
        'end': end_interval
    }
    
    conducta.lpush('coada_sarcini', json.dumps(sarcina))

print("[DISPECER] Trimit intregul container prin internet...")
conducta.execute()

print(f"[DISPECER] Gata! Toate cele {NUMAR_PACHETE} de pachete sunt pe banda.")
print("[DISPECER] Muncitorii pot incepe sa le preia.")