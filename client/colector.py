import json
import os
import redis
import time

# Adresa Redis vine din variabile de mediu (vezi README)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "30474"))

print("[COLECTOR] Sistem pregatit. Ma conectez la Redis...")

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    r.ping()
    print("[COLECTOR] Conectat cu succes!")
except Exception as e:
    print("[COLECTOR] Eroare la conectare la Redis!")
    exit()

print("[COLECTOR] Astept ca Dispecerul sa anunte numarul de pachete pe panou...")
while True:
    total_str = r.get('numar_total_pachete')
    if total_str is not None:
        NUMAR_PACHETE = int(total_str)
        print(f"[COLECTOR] Am aflat! Trebuie sa strang {NUMAR_PACHETE} rezultate. Start!")
        break
    time.sleep(1)

statistici = {}
suma_totala = 0
count = 0

timp_start = time.time()

while count < NUMAR_PACHETE:
    rezultat_brpop = r.brpop('coada_rezultate', timeout=1)
    
    if rezultat_brpop:
        date_primite = rezultat_brpop[1]
        raspuns = json.loads(date_primite)
        
        suma_totala += raspuns['rezultat']
        
        nume_harnic = raspuns.get('muncitor', 'muncitor-necunoscut (pe laptop)')
        
        if nume_harnic in statistici:
            statistici[nume_harnic] += 1
        else:
            statistici[nume_harnic] = 1
        
        count += 1
        
        if count % 100 == 0:
            print(f"[COLECTOR] Am primit {count}/{NUMAR_PACHETE} rezultate...")

timp_final = time.time()
durata = timp_final - timp_start

print("\n==========================================")
print(f"Timp total: {durata:.2f} secunde")
print(f"Suma totala calculata: {suma_totala}")
print("==========================================")

print("\n=== DOVADA PARALELISM (LOAD BALANCING) ===")
for muncitor, pachete in sorted(statistici.items(), key=lambda x: x[1], reverse=True):
    print(f"-> {muncitor} a rezolvat: {pachete} pachete")
print("==========================================\n")

r.delete('numar_total_pachete')
print("[COLECTOR] Am sters numarul de pe panou. Gata pentru un nou test!")