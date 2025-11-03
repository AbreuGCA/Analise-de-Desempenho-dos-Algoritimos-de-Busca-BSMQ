import java.util.*;
import java.util.concurrent.*;
import java.io.*;

public class InsertionSortJava {
    
    // Configurações
    private static final int RANDOM_SEED = 42;
    private static final int[] SIZES = {1000, 5000, 10000};
    private static final String[] DATA_TYPES = {"random", "sorted", "reversed", "duplicates"};
    private static final int[] THREAD_LEVELS = {0, 1, 2, 3};
    private static final int SAMPLES = 5;
    private static final String OUTPUT_CSV = "resultados_insertionsort_java.csv";
    
    private static Random random = new Random(RANDOM_SEED);
    
    // Insertion Sort Serial
    public static int[] insertionsortSerial(int[] arr) {
        if (arr.length <= 1) {
            return arr;
        }
        
        int[] data = arr.clone();
        
        for (int i = 1; i < data.length; i++) {
            int key = data[i];
            int j = i - 1;
            
            while (j >= 0 && data[j] > key) {
                data[j + 1] = data[j];
                j--;
            }
            data[j + 1] = key;
        }
        return data;
    }
    
    // Insertion Sort para segmento
    private static int[] insertionsortSegment(int[] arrSegment) {
        if (arrSegment.length <= 1) {
            return arrSegment;
        }
        
        int[] data = arrSegment.clone();
        
        for (int i = 1; i < data.length; i++) {
            int key = data[i];
            int j = i - 1;
            
            while (j >= 0 && data[j] > key) {
                data[j + 1] = data[j];
                j--;
            }
            data[j + 1] = key;
        }
        return data;
    }
    
    // Função merge para segmentos ordenados (reutilizada do BubbleSort)
    private static int[] mergeSortedSegments(List<int[]> segments) {
        if (segments.size() == 1) {
            return segments.get(0);
        }
        
        while (segments.size() > 1) {
            List<int[]> newSegments = new ArrayList<>();
            for (int i = 0; i < segments.size(); i += 2) {
                if (i + 1 < segments.size()) {
                    newSegments.add(mergeTwo(segments.get(i), segments.get(i + 1)));
                } else {
                    newSegments.add(segments.get(i));
                }
            }
            segments = newSegments;
        }
        return segments.get(0);
    }
    
    private static int[] mergeTwo(int[] left, int[] right) {
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
    
    // Insertion Sort Paralelo
    public static int[] insertionsortParallel(int[] arr, int maxDepth) throws Exception {
        if (arr.length <= 1) {
            return arr;
        }
        
        int numSegments = Math.min((int) Math.pow(2, maxDepth), arr.length);
        int segmentSize = Math.max(1, arr.length / numSegments);
        
        List<int[]> segments = new ArrayList<>();
        for (int i = 0; i < arr.length; i += segmentSize) {
            int end = Math.min(i + segmentSize, arr.length);
            segments.add(Arrays.copyOfRange(arr, i, end));
        }
        
        if (maxDepth <= 0) {
            List<int[]> sortedSegments = new ArrayList<>();
            for (int[] seg : segments) {
                sortedSegments.add(insertionsortSegment(seg));
            }
            return mergeSortedSegments(sortedSegments);
        }
        
        ExecutorService executor = Executors.newFixedThreadPool(numSegments);
        try {
            List<Future<int[]>> futures = new ArrayList<>();
            for (int[] seg : segments) {
                futures.add(executor.submit(() -> insertionsortSegment(seg)));
            }
            
            List<int[]> sortedSegments = new ArrayList<>();
            for (Future<int[]> future : futures) {
                sortedSegments.add(future.get());
            }
            
            return mergeSortedSegments(sortedSegments);
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
    public static void benchmarkInsertionsort() {
        int cpuCount = Runtime.getRuntime().availableProcessors();
        List<String[]> results = new ArrayList<>();
        
        String[] header = {
            "Algoritmo", "Modo", "Tamanho", "Tipo_de_Dados", "Profundidade",
            "Num_Threads_Estimado", "Num_Threads_Utilizadas", "Amostra",
            "Tempo_ms", "Cpu_Count", "Timestamp"
        };
        
        System.out.println("Executando benchmark InsertionSort (Java)...\n");
        
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
                                insertionsortSerial(dataCopy);
                                mode = "Serial";
                            } else {
                                insertionsortParallel(dataCopy, depth);
                                mode = "Paralela";
                            }
                            
                            long endTime = System.nanoTime();
                            double elapsedMs = (endTime - startTime) / 1_000_000.0;
                            
                            String timestamp = new Date().toString();
                            
                            String[] row = {
                                "InsertionSort", mode, String.valueOf(size), dataType,
                                String.valueOf(depth), String.valueOf(estimatedThreads),
                                String.valueOf(numThreadsUsed), String.valueOf(sample),
                                String.format("%.6f", elapsedMs), String.valueOf(cpuCount),
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
        benchmarkInsertionsort();
    }
}