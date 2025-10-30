# insertionsort_powerbi.py
import random
import time
import csv
import os
from concurrent.futures import ThreadPoolExecutor

# -------------------------------
# Configurações (ajuste se desejar)
# -------------------------------
RANDOM_SEED = 42       
SIZES = [1_000, 5_000, 10_000]  # Tamanhos reduzidos para Insertion Sort
DATA_TYPES = ["random", "sorted", "reversed", "duplicates"]
THREAD_LEVELS = [0, 1, 2, 3] 
SAMPLES = 5
OUTPUT_CSV = "resultados_insertionsort_powerbi.csv"

random.seed(RANDOM_SEED)

# -------------------------------
# Insertion Sort Serial
# -------------------------------
def insertionsort_serial(arr):
    if len(arr) <= 1:
        return arr
    
    # Trabalha in-place para eficiência de memória
    data = arr.copy()
    
    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
    
    return data

# -------------------------------
# Insertion Sort Paralelo (divisão por segmentos)
# -------------------------------
def insertionsort_segment(arr_segment):
    """Ordena um segmento usando insertion sort"""
    if len(arr_segment) <= 1:
        return arr_segment
    
    data = arr_segment.copy()
    
    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
    
    return data

def merge_sorted_segments(segments):
    """Funde múltiplos segmentos ordenados em uma única lista ordenada"""
    if len(segments) == 1:
        return segments[0]
    
    # Função merge similar à do MergeSort
    def merge_two(left, right):
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
    
    # Funde recursivamente os segmentos
    while len(segments) > 1:
        new_segments = []
        for i in range(0, len(segments), 2):
            if i + 1 < len(segments):
                new_segments.append(merge_two(segments[i], segments[i + 1]))
            else:
                new_segments.append(segments[i])
        segments = new_segments
    
    return segments[0]

def insertionsort_parallel(arr, max_depth=0):
    if len(arr) <= 1:
        return arr
    
    # Divide a lista em segmentos para processamento paralelo
    num_segments = min(2 ** max_depth, len(arr))
    segment_size = max(1, len(arr) // num_segments)
    
    segments = []
    for i in range(0, len(arr), segment_size):
        segments.append(arr[i:i + segment_size])
    
    if max_depth <= 0:
        # Serial: ordena cada segmento sequencialmente
        sorted_segments = [insertionsort_segment(seg) for seg in segments]
    else:
        # Paralelo: ordena segmentos em threads separadas
        with ThreadPoolExecutor(max_workers=num_segments) as executor:
            futures = [executor.submit(insertionsort_segment, seg) for seg in segments]
            sorted_segments = [future.result() for future in futures]
    
    # Funde todos os segmentos ordenados
    return merge_sorted_segments(sorted_segments)

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
def benchmark_insertionsort():
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

    print("Executando benchmark InsertionSort (formato Power BI)...\n")

    # Se o arquivo já existe, carregar resultados anteriores
    existing_results = []
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader)  # Pular cabeçalho
            existing_results = list(reader)
        print(f"Carregados {len(existing_results)} resultados existentes")

    for size in SIZES:
        for data_type in DATA_TYPES:
            base_data = generate_dataset(size, data_type)
            for depth in THREAD_LEVELS:
                # Verificar se já foi executado
                already_done = any(
                    len(row) > 4 and
                    row[2] == str(size) and 
                    row[3] == data_type and 
                    row[4] == str(depth)
                    for row in existing_results
                )
                
                if already_done:
                    print(f"Pulando: size={size}, type={data_type}, depth={depth}")
                    continue

                estimated_threads = 1 if depth == 0 else 2 ** depth
                num_threads_used = min(estimated_threads, cpu_count) if estimated_threads > 0 else 1

                for sample in range(1, SAMPLES + 1):
                    # Pular amostras específicas já feitas
                    sample_done = any(
                        len(row) > 7 and
                        row[2] == str(size) and 
                        row[3] == data_type and 
                        row[4] == str(depth) and 
                        row[7] == str(sample)
                        for row in existing_results
                    )
                    
                    if sample_done:
                        continue

                    data_copy = base_data.copy()
                    t0 = time.perf_counter()
                    if depth == 0:
                        insertionsort_serial(data_copy)
                        mode = "Serial"
                    else:
                        insertionsort_parallel(data_copy, max_depth=depth)
                        mode = "Paralela"
                    t1 = time.perf_counter()
                    elapsed_ms = (t1 - t0) * 1000.0

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                    row = [
                        "InsertionSort",
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

                    # Salvar progresso a cada amostra
                    with open(OUTPUT_CSV, "a", newline="") as f:
                        writer = csv.writer(f)
                        if os.path.getsize(OUTPUT_CSV) == 0:
                            writer.writerow(header)
                        writer.writerow(row)

    print(f"\nBenchmark concluido. Arquivo salvo: '{OUTPUT_CSV}'")
    print("Dica: importe este CSV no Power BI (Obter Dados -> Texto/CSV).")

if __name__ == "__main__":
    benchmark_insertionsort()