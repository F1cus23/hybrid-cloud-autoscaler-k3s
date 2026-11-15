import os
import redis
import time

# Adresa Redis vine din variabile de mediu (vezi README)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "30474"))

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    r.ping()
    print("[WATCHDOG AUTOMAT] Pornit! Stau de paza...")
except Exception as e:
    print("[WATCHDOG AUTOMAT] Eroare la conectare.")
    exit()

# Contor pentru a vedea de cat timp e blocat sistemul
suspiciune = 0

while True:
    sarcini_pe_banda = r.llen('coada_sarcini')
    sarcini_in_lucru = r.llen('coada_procesare')

    # REGULA DE BAZA: Devenim suspiciosi DOAR daca nu mai vin pachete noi, 
    # dar au ramas pachete agatate pe mesele de lucru.
    if sarcini_pe_banda == 0 and sarcini_in_lucru > 0:
        suspiciune += 1
        print(f"[WATCHDOG AUTOMAT] Suspiciune ({suspiciune}/3): Banda e goala, dar avem {sarcini_in_lucru} pachete 'in lucru'.")

        # Daca trec 4 cicluri (40 secunde) de blocaj, actionam!
        if suspiciune >= 3:
            print("[WATCHDOG AUTOMAT] CONFIRMAT: Pachete Zombie! Le mut inapoi pe banda.")
            
            pachete_salvate = 0
            while True:
                # Mutam din procesare inapoi pe sarcini
                pachet = r.rpoplpush('coada_procesare', 'coada_sarcini')
                if pachet:
                    pachete_salvate += 1
                else:
                    break
            
            print(f"[WATCHDOG AUTOMAT] Am salvat {pachete_salvate} pachete! Autoscalerul ar trebui sa le vada acum.")
            suspiciune = 0 # Resetam cronometrul
            
    else:
        # Daca sistemul functioneaza normal, curatam suspiciunile
        suspiciune = 0

    # Asteptam 10 secunde
    time.sleep(10)