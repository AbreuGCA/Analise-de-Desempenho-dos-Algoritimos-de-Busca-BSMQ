# mergesort_powerbi.py
import random
import time
import csv
import os
from concurrent.futures import ThreadPoolExecutor

# -------------------------------
# Configurações (ajuste se desejar)
# -------------------------------
RANDOM_SEED = 42       
SIZES = [10_000, 50_000, 100_000]  
DATA_TYPES = ["random", "sorted", "reversed", "duplicates"]
THREAD_LEVELS = [0, 1, 2, 3] 
SAMPLES = 5
OUTPUT_CSV = "resultados_mergesort_powerbi.csv"

random.seed(RANDOM_SEED)

# -------------------------------
# Merge Sort Serial (recursivo, retorna nova lista)
# -------------------------------
def merge(left, right):
    i = j = 0
    merged = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    if i < len(left):
        merged.extend(left[i:])
    if j < len(right):
        merged.extend(right[j:])
    return merged

def mergesort_serial(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort_serial(arr[:mid])
    right = mergesort_serial(arr[mid:])
    return merge(left, right)

# -------------------------------
# Merge Sort Paralelo (profundidade controlada)
# -------------------------------
def mergesort_parallel(arr, max_depth=0):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left_part = arr[:mid]
    right_part = arr[mid:]

    if max_depth <= 0:
        left_sorted = mergesort_serial(left_part)
        right_sorted = mergesort_serial(right_part)
        return merge(left_sorted, right_sorted)

    with ThreadPoolExecutor(max_workers=2) as executor:
        left_future = executor.submit(mergesort_parallel, left_part, max_depth - 1)
        right_future = executor.submit(mergesort_parallel, right_part, max_depth - 1)
        left_sorted = left_future.result()
        right_sorted = right_future.result()
        return merge(left_sorted, right_sorted)

# -------------------------------
# Geração de datasets
# -------------------------------
def generate_dataset(size, data_type="random"):
    if data_type == "random":
        return [random.randint(0, 1_000_000) for _ in range(size)]
    elif data_type == "sorted":
        return list(range(size))
    elif data_type == "reversed":
        return list(range(size, 0, -1))
    elif data_type == "duplicates":
        return [random.choice([1, 2, 3, 4, 5]) for _ in range(size)]
    else:
        raise ValueError("Tipo de dado inválido.")

# -------------------------------
# Benchmark adaptado para Power BI
# -------------------------------
def benchmark_mergesort():
    cpu_count = os.cpu_count() or 1
    results = []

    header = [
        "Algoritmo",
        "Modo",                 
        "Tamanho",              
        "Tipo_de_Dados",        
        "Profundidade",         
        "Num_Threads_Estimado", 
        "Num_Threads_Utilizadas", 
        "Amostra",              
        "Tempo_ms",             
        "Cpu_Count",            
        "Timestamp"             
    ]

    print("Executando benchmark MergeSort (formato Power BI)...\n")

    for size in SIZES:
        for data_type in DATA_TYPES:
            base_data = generate_dataset(size, data_type)
            for depth in THREAD_LEVELS:
                estimated_threads = 1 if depth == 0 else 2 ** depth
                num_threads_used = min(estimated_threads, cpu_count) if estimated_threads > 0 else 1

                for sample in range(1, SAMPLES + 1):
                    data_copy = base_data.copy()
                    t0 = time.perf_counter()
                    if depth == 0:
                        mergesort_serial(data_copy)
                        mode = "Serial"
                    else:
                        mergesort_parallel(data_copy, max_depth=depth)
                        mode = "Paralela"
                    t1 = time.perf_counter()
                    elapsed_ms = (t1 - t0) * 1000.0

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                    row = [
                        "MergeSort",
                        mode,
                        size,
                        data_type,
                        depth,
                        estimated_threads,
                        num_threads_used,
                        sample,
                        round(elapsed_ms, 6),
                        cpu_count,
                        timestamp
                    ]

                    results.append(row)

                    print(f"[{timestamp}] Size={size:7d} | Type={data_type:9s} | Mode={mode:8s} | "
                          f"Depth={depth} | EstThreads={estimated_threads:3d} | Sample={sample} | Time={elapsed_ms:.3f} ms")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(results)

    print(f"\n✅ Benchmark concluído. Arquivo salvo: '{OUTPUT_CSV}'")
    print("Dica: importe este CSV no Power BI (Obter Dados → Texto/CSV).")

if __name__ == "__main__":
    benchmark_mergesort()
