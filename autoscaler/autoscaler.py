import os
import redis
import subprocess
import time

HOST_REDIS = os.getenv("REDIS_HOST", "localhost")
PORT_REDIS = int(os.getenv("REDIS_PORT", "30474"))

# Folderul cu main.tf (implicit: ../infra/azure fata de acest fisier)
TF_DIR = os.getenv("TF_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "infra", "azure"))

try:
    r = redis.Redis(host=HOST_REDIS, port=PORT_REDIS, db=0, decode_responses=True)
    r.ping()
    print("[AUTOSCALER] Conectat la banda de productie (Redis)!")
except Exception as e:
    print("[AUTOSCALER] Eroare fatala la conectarea cu Redis:", e)
    exit()

# Variabile de stare
masini_curente = -1
cicluri_coada_goala = 0

print("[AUTOSCALER] Robotul a pornit si supravegheaza banda...")

while True:
    try:
        # 1. (Sarcini noi + Sarcini in lucru)
        sarcini_noi = r.llen('coada_sarcini')
        sarcini_in_lucru = r.llen('coada_procesare')
        lungime_coada = sarcini_noi + sarcini_in_lucru
        
        if lungime_coada > 0 and masini_curente <= 0:
            print(f"[AUTOSCALER] Detectat trafic nou ({lungime_coada} pachete)! Astept 8 secunde sa se umple coada...")
            time.sleep(8)
            
            # Recitim coada ca sa luam decizia pe numarul final de pachete intrat
            sarcini_noi = r.llen('coada_sarcini')
            sarcini_in_lucru = r.llen('coada_procesare')
            lungime_coada = sarcini_noi + sarcini_in_lucru
            print(f"[AUTOSCALER] Coada s-a stabilizat la {lungime_coada} pachete. Incep calculul!")

        print(f"[STATUS] Banda: {sarcini_noi} | Procesare: {sarcini_in_lucru} | TOTAL: {lungime_coada}")

        # 2. LOGICA DE DECIZIE
        if lungime_coada > 1000:
            masini_necesare = 3
            cicluri_coada_goala = 0

        elif lungime_coada > 300:
            # Daca aveam deja 3, le pastram pentru sprintul final!
            masini_necesare = 3 if masini_curente == 3 else 1
            cicluri_coada_goala = 0

        elif lungime_coada > 0:
            # Pastram toate masinile care sunt deja pornite ca sa termine treaba repede
            masini_necesare = masini_curente if masini_curente > 0 else 0
            cicluri_coada_goala = 0

        else:
            # COADA ESTE EXACT ZERO
            if masini_curente > 0:
                if cicluri_coada_goala < 6:
                    print(f"[AUTOSCALER] Nu mai e treaba, dar astept ultimele rezultate ({cicluri_coada_goala + 1}/6)...")
                    cicluri_coada_goala += 1
                    masini_necesare = masini_curente
                else:
                    print("[AUTOSCALER] Timpul de gratie a expirat! Ordon retragerea cloud-ului.")
                    masini_necesare = 0
            else:
                masini_necesare = 0

        # 3. EXECUTIA TERRAFORM
        if masini_necesare != masini_curente:
            print(f"[AUTOSCALER] --> Schimbare detectata! Aducem {masini_necesare} masini in Azure.")

            comanda = ["terraform", "apply", f"-var=numar_masini={masini_necesare}", "-auto-approve"]
            rezultat = subprocess.run(comanda, cwd=TF_DIR)

            if rezultat.returncode == 0:
                print(f"[AUTOSCALER] Succes! Avem {masini_necesare} masini in cloud.")
                masini_curente = masini_necesare
            else:
                print("[AUTOSCALER] EROARE la Terraform! Repornim incercarea in ciclul urmator.")

    except Exception as e:
        print(f"[AUTOSCALER] Eroare neasteptata in bucla: {e}")

    time.sleep(10)