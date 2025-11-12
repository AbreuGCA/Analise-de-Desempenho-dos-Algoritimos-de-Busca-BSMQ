package algoritimos;
import java.util.*;
import java.util.concurrent.*;
import java.io.*;

public class QuickSortJava {
    
    // Configurações
    private static final int RANDOM_SEED = 42;
    private static final int[] SIZES = {10000, 50000, 100000};
    private static final String[] DATA_TYPES = {"random", "sorted", "reversed", "duplicates"};
    private static final int[] THREAD_LEVELS = {0, 1, 2, 3};
    private static final int SAMPLES = 5;
    private static final String OUTPUT_CSV = "resultados_quicksort_java.csv";
    
    private static Random random = new Random(RANDOM_SEED);
    
    // QuickSort Serial
    public static int[] quicksortSerial(int[] arr) {
        if (arr.length <= 1) {
            return arr;
        }
        
        int pivot = arr[arr.length / 2];
        List<Integer> left = new ArrayList<>();
        List<Integer> middle = new ArrayList<>();
        List<Integer> right = new ArrayList<>();
        
        for (int x : arr) {
            if (x < pivot) {
                left.add(x);
            } else if (x == pivot) {
                middle.add(x);
            } else {
                right.add(x);
            }
        }
        
        int[] leftSorted = quicksortSerial(listToArray(left));
        int[] middleArr = listToArray(middle);
        int[] rightSorted = quicksortSerial(listToArray(right));
        
        return concatenateArrays(leftSorted, middleArr, rightSorted);
    }
    
    // QuickSort Paralelo
    public static int[] quicksortParallel(int[] arr, int maxDepth) throws Exception {
        if (arr.length <= 1) {
            return arr;
        }
        
        int pivot = arr[arr.length / 2];
        List<Integer> left = new ArrayList<>();
        List<Integer> middle = new ArrayList<>();
        List<Integer> right = new ArrayList<>();
        
        for (int x : arr) {
            if (x < pivot) {
                left.add(x);
            } else if (x == pivot) {
                middle.add(x);
            } else {
                right.add(x);
            }
        }
        
        if (maxDepth <= 0) {
            int[] leftSorted = quicksortSerial(listToArray(left));
            int[] middleArr = listToArray(middle);
            int[] rightSorted = quicksortSerial(listToArray(right));
            return concatenateArrays(leftSorted, middleArr, rightSorted);
        }
        
        ExecutorService executor = Executors.newFixedThreadPool(2);
        try {
            Future<int[]> leftFuture = executor.submit(() -> 
                quicksortParallel(listToArray(left), maxDepth - 1));
            Future<int[]> rightFuture = executor.submit(() -> 
                quicksortParallel(listToArray(right), maxDepth - 1));
            
            int[] leftSorted = leftFuture.get();
            int[] middleArr = listToArray(middle);
            int[] rightSorted = rightFuture.get();
            
            return concatenateArrays(leftSorted, middleArr, rightSorted);
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
    
    // Métodos auxiliares
    private static int[] listToArray(List<Integer> list) {
        return list.stream().mapToInt(i -> i).toArray();
    }
    
    private static int[] concatenateArrays(int[]... arrays) {
        int totalLength = 0;
        for (int[] array : arrays) {
            totalLength += array.length;
        }
        
        int[] result = new int[totalLength];
        int currentIndex = 0;
        for (int[] array : arrays) {
            System.arraycopy(array, 0, result, currentIndex, array.length);
            currentIndex += array.length;
        }
        return result;
    }
    
    // Benchmark
    public static void benchmarkQuicksort() {
        int cpuCount = Runtime.getRuntime().availableProcessors();
        List<String[]> results = new ArrayList<>();
        
        String[] header = {
            "Algoritmo", "Modo", "Tamanho", "Tipo_de_Dados", "Profundidade",
            "Num_Threads_Estimado", "Num_Threads_Utilizadas", "Amostra",
            "Tempo_ms", "Cpu_Count", "Timestamp"
        };
        
        System.out.println("Executando benchmark QuickSort (Java)...\n");
        
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
                                quicksortSerial(dataCopy);
                                mode = "Serial";
                            } else {
                                quicksortParallel(dataCopy, depth);
                                mode = "Paralela";
                            }
                            
                            long endTime = System.nanoTime();
                            double elapsedMs = (endTime - startTime) / 1_000_000.0;
                            
                            String timestamp = new Date().toString();
                            
                            String[] row = {
                                "QuickSort", mode, String.valueOf(size), dataType,
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
        benchmarkQuicksort();
    }
}