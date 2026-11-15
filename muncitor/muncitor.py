import json
import os
import redis
import time

# Adresa Redis vine din variabile de mediu (vezi README)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "30474"))

# Ne conectam la baza de date
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    r.ping()
    print("[MUNCITOR] Conectat la Redis. Astept ordine!")
except Exception as e:
    print("[MUNCITOR] Eroare fatala de retea:", e)
    exit()

# Luam numele pod-ului (ca sa stim cine a facut munca in clasament)
nume_muncitor = os.getenv("HOSTNAME", "muncitor-local")

def calculeaza_matematica(start, end):
    numere_prime_gasite = 0
    for num in range(start, end):
        if num > 1:
            is_prime = True
            # Impartim numărul la toate numerele pana la radacina lui patrata
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break  # Am gasit un divizor, nu e prim, trecem mai departe
            if is_prime:
                numere_prime_gasite += 1
    return numere_prime_gasite

print(f"[{nume_muncitor}] Gata de munca grea!")

while True:
    # Extragem un pachet folosind metoda sigura (mutam in coada_procesare pt Watchdog)
    sarcina_bruta = r.rpoplpush('coada_sarcini', 'coada_procesare')
    
    if sarcina_bruta:
        sarcina = json.loads(sarcina_bruta)
        
        # Extragem limitele intervalului
        id_pachet = sarcina['id']
        start_interval = sarcina['start']
        end_interval = sarcina['end']
        
        # Facem matematica grea
        rezultat_calcul = calculeaza_matematica(start_interval, end_interval)
        
        # Pregatim raspunsul
        raspuns = {
            'id': id_pachet,
            'rezultat': rezultat_calcul,
            'muncitor': nume_muncitor
        }
        
        # Trimitem raspunsul la colector
        r.lpush('coada_rezultate', json.dumps(raspuns))
        
        # Stergem pachetul din coada_procesare pentru ca l-am rezolvat cu succes
        r.lrem('coada_procesare', 1, sarcina_bruta)
        
    else:
        # Daca banda e goala, se odihneste o secunda si verifica iar
        time.sleep(1)