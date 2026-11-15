import time

def calculeaza_matematica(start, end):
    """
    Aceeasi functie de forta bruta care va fi rulata si pe cluster.
    """
    numere_prime_gasite = 0
    for num in range(start, end):
        if num > 1:
            is_prime = True
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                numere_prime_gasite += 1
    return numere_prime_gasite

print("==================================================")
print(" INCEPE BENCHMARK-UL LOCAL (Munca Grea: Numere Prime)")
print(" Acest test va ingenunchea procesorul (un singur nucleu)!")
print("==================================================")

# Setarile testului (TREBUIE sa fie identice in dispecer.py)
NUMAR_PACHETE = 10000
START_BASE = 100000
INTERVAL_SIZE = 10000

total_prime_gasite = 0
pachete_procesate = 0

# Pornim cronometrul
timp_start = time.time()

for i in range(NUMAR_PACHETE):
    start_interval = START_BASE + (i * INTERVAL_SIZE)
    end_interval = start_interval + INTERVAL_SIZE
    
    # Printam ca sa vezi cat de greu ii ia sa treaca de la un pachet la altul
    print(f"-> Procesez pachetul {i+1}/{NUMAR_PACHETE}")
    
    # Facem matematica pe un singur nucleu (fara cluster)
    prime_in_pachet = calculeaza_matematica(start_interval, end_interval)
    total_prime_gasite += prime_in_pachet
    pachete_procesate += 1

# Oprim cronometrul
timp_end = time.time()
timp_total = timp_end - timp_start

print("\n==================================================")
print(" CALCUL SECVENTIAL FINALIZAT!")
print("==================================================")
print(f"Total numere prime gasite: {total_prime_gasite}")
print(f"Pachete procesate:         {pachete_procesate}")
print(f"Timp total:                {timp_total:.2f} secunde")
print("==================================================")