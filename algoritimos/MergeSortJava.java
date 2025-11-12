package algoritimos;
import java.util.*;
import java.util.concurrent.*;
import java.io.*;

public class MergeSortJava {
    
    // Configurações
    private static final int RANDOM_SEED = 42;
    private static final int[] SIZES = {10000, 50000, 100000};
    private static final String[] DATA_TYPES = {"random", "sorted", "reversed", "duplicates"};
    private static final int[] THREAD_LEVELS = {0, 1, 2, 3};
    private static final int SAMPLES = 5;
    private static final String OUTPUT_CSV = "resultados_mergesort_java.csv";
    
    private static Random random = new Random(RANDOM_SEED);
    
    // Merge Sort Serial
    public static int[] mergesortSerial(int[] arr) {
        if (arr.length <= 1) {
            return arr;
        }
        
        int mid = arr.length / 2;
        int[] left = Arrays.copyOfRange(arr, 0, mid);
        int[] right = Arrays.copyOfRange(arr, mid, arr.length);
        
        int[] leftSorted = mergesortSerial(left);
        int[] rightSorted = mergesortSerial(right);
        
        return merge(leftSorted, rightSorted);
    }
    
    // Função merge
    private static int[] merge(int[] left, int[] right) {
        int[] merged = new int[left.length + right.length];
        int i = 0, j = 0, k = 0;
        
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) {
                merged[k++] = left[i++];
            } else {
                merged[k++] = right[j++];
            }
        }
        
        while (i < left.length) {
            merged[k++] = left[i++];
        }
        
        while (j < right.length) {
            merged[k++] = right[j++];
        }
        
        return merged;
    }
    
    // Merge Sort Paralelo
    public static int[] mergesortParallel(int[] arr, int maxDepth) throws Exception {
        if (arr.length <= 1) {
            return arr;
        }
        
        int mid = arr.length / 2;
        int[] leftPart = Arrays.copyOfRange(arr, 0, mid);
        int[] rightPart = Arrays.copyOfRange(arr, mid, arr.length);
        
        if (maxDepth <= 0) {
            int[] leftSorted = mergesortSerial(leftPart);
            int[] rightSorted = mergesortSerial(rightPart);
            return merge(leftSorted, rightSorted);
        }
        
        ExecutorService executor = Executors.newFixedThreadPool(2);
        try {
            Future<int[]> leftFuture = executor.submit(() -> 
                mergesortParallel(leftPart, maxDepth - 1));
            Future<int[]> rightFuture = executor.submit(() -> 
                mergesortParallel(rightPart, maxDepth - 1));
            
            int[] leftSorted = leftFuture.get();
            int[] rightSorted = rightFuture.get();
            
            return merge(leftSorted, rightSorted);
        } finally {
            executor.shutdown();
        }
    }
    
    // Geração de datasets
    public static int[] generateDataset(int size, String dataType) {
        int[] data = new int[size];
        
        switch (dataType) {
            case "random":
                for (int i = 0; i < size; i++) {
                    data[i] = random.nextInt(1000000);
                }
                break;
            case "sorted":
                for (int i = 0; i < size; i++) {
                    data[i] = i;
                }
                break;
            case "reversed":
                for (int i = 0; i < size; i++) {
                    data[i] = size - i;
                }
                break;
            case "duplicates":
                int[] choices = {1, 2, 3, 4, 5};
                for (int i = 0; i < size; i++) {
                    data[i] = choices[random.nextInt(choices.length)];
                }
                break;
            default:
                throw new IllegalArgumentException("Tipo de dado inválido: " + dataType);
        }
        return data;
    }
    
    // Benchmark
    public static void benchmarkMergesort() {
        int cpuCount = Runtime.getRuntime().availableProcessors();
        List<String[]> results = new ArrayList<>();
        
        String[] header = {
            "Algoritmo", "Modo", "Tamanho", "Tipo_de_Dados", "Profundidade",
            "Num_Threads_Estimado", "Num_Threads_Utilizadas", "Amostra",
            "Tempo_ms", "Cpu_Count", "Timestamp"
        };
        
        System.out.println("Executando benchmark MergeSort (Java)...\n");
        
        try {
            for (int size : SIZES) {
                for (String dataType : DATA_TYPES) {
                    int[] baseData = generateDataset(size, dataType);
                    
                    for (int depth : THREAD_LEVELS) {
                        int estimatedThreads = (depth == 0) ? 1 : (int) Math.pow(2, depth);
                        int numThreadsUsed = Math.min(estimatedThreads, cpuCount);
                        
                        for (int sample = 1; sample <= SAMPLES; sample++) {
                            int[] dataCopy = baseData.clone();
                            long startTime = System.nanoTime();
                            
                            String mode;
                            if (depth == 0) {
                                mergesortSerial(dataCopy);
                                mode = "Serial";
                            } else {
                                mergesortParallel(dataCopy, depth);
                                mode = "Paralela";
                            }
                            
                            long endTime = System.nanoTime();
                            double elapsedMs = (endTime - startTime) / 1_000_000.0;
                            
                            String timestamp = new Date().toString();
                            
                            String[] row = {
                                "MergeSort", mode, String.valueOf(size), dataType,
                                String.valueOf(depth), String.valueOf(estimatedThreads),
                                String.valueOf(numThreadsUsed), String.valueOf(sample),
                                String.format(Locale.US, "%.6f", elapsedMs), String.valueOf(cpuCount),
                                timestamp
                            };
                            
                            results.add(row);
                            
                            System.out.printf("[%s] Size=%7d | Type=%9s | Mode=%8s | Depth=%d | EstThreads=%3d | Sample=%d | Time=%.3f ms%n",
                                timestamp, size, dataType, mode, depth, estimatedThreads, sample, elapsedMs);
                        }
                    }
                }
            }
            
            // Escrever resultados no CSV
            try (PrintWriter writer = new PrintWriter(new FileWriter(OUTPUT_CSV))) {
                writer.println(String.join(",", header));
                for (String[] row : results) {
                    writer.println(String.join(",", row));
                }
            }
            
            System.out.println("\nBenchmark concluído. Arquivo salvo: '" + OUTPUT_CSV + "'");
            
        } catch (Exception e) {
            System.err.println("Erro durante o benchmark: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public static void main(String[] args) {
        benchmarkMergesort();
    }
}