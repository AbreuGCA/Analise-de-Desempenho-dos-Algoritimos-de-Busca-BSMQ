# Análise de Desempenho de Algoritmos de Ordenação - BSMQ

Este projeto implementa e compara quatro algoritmos de ordenação clássicos (Bubble Sort, Insertion Sort, Merge Sort e QuickSort) em suas versões serial e paralela, analisando seu desempenho em diversos cenários. O código foi desenvolvido em Java com paralelização utilizando threads, e inclui um sistema completo de benchmark e geração de relatórios.

## 📊 Algoritmos Implementados

### 1. Bubble Sort
- **Complexidade**: O(n²) no pior caso
- **Características**: Algoritmo de ordenação por trocas, estável
- **Implementações**: Serial e paralela com divisão de segmentos

### 2. Insertion Sort
- **Complexidade**: O(n²) no pior caso
- **Características**: Eficiente para pequenos conjuntos, estável
- **Implementações**: Serial e paralela com divisão de segmentos

### 3. Merge Sort
- **Complexidade**: O(n log n) em todos os casos
- **Características**: Algoritmo de divisão e conquista, estável
- **Implementações**: Serial e paralela recursiva

### 4. QuickSort
- **Complexidade**: O(n log n) no caso médio, O(n²) no pior caso
- **Características**: Divisão e conquista com pivô, não estável
- **Implementações**: Serial e paralela recursiva

## 🏗️ Estrutura do Projeto

```
projeto-bsmq/
│
├── 📊 Código Fonte Java
│   ├── BubbleSortJava.java
│   ├── InsertionSortJava.java
│   ├── MergeSortJava.java
│   └── QuickSortJava.java
│
├── 📈 Sistema de Análise
│   └── main.py
│
├── 📋 Resultados (gerados automaticamente)
│   ├── resultados_bubblesort_java.csv
│   ├── resultados_insertionsort_java.csv
│   ├── resultados_mergesort_java.csv
│   └── resultados_quicksort_java.csv
│
├── 🌐 Relatórios HTML (gerados automaticamente)
│   ├── index.html
│   ├── bubblesort_analysis.html
│   ├── insertionsort_analysis.html
│   ├── mergesort_analysis.html
│   └── quicksort_analysis.html
│
└── 📊 Gráficos (gerados automaticamente)
    ├── bubblesort_analysis.png
    ├── insertionsort_analysis.png
    ├── mergesort_analysis.png
    └── quicksort_analysis.png
```

## ⚙️ Configurações do Benchmark

### Parâmetros de Teste
- **Tamanhos de Array**: 
  - Bubble Sort & Insertion Sort: 1.000, 5.000, 10.000 elementos
  - Merge Sort & QuickSort: 10.000, 50.000, 100.000 elementos

- **Tipos de Dados**:
  - `random`: Números aleatórios (0-1.000.000)
  - `sorted`: Lista ordenada crescente
  - `reversed`: Lista em ordem decrescente
  - `duplicates`: Lista com valores duplicados (1-5)

- **Níveis de Paralelização**: 0 (serial), 1, 2 e 3 níveis de profundidade
- **Amostras**: 5 execuções para cada configuração
- **Semente Aleatória**: 42 (para resultados reproduzíveis)

## 🚀 Como Executar

### Pré-requisitos
- Java JDK 8 ou superior
- Python 3.7 ou superior
- Bibliotecas Python: pandas, matplotlib, seaborn, numpy

### Execução Completa

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/AbreuGCA/Analise-de-Desempenho-dos-Algoritimos-de-Busca-BSMQ
   cd Analise-de-Desempenho-dos-Algoritimos-de-Busca-BSMQ
   ```

2. **Execute o sistema de análise**:
   ```bash
   python main.py
   ```

### O que acontece durante a execução:

1. **Compilação Automática**: Todos os arquivos Java são compilados
2. **Execução dos Benchmarks**: Cada algoritmo é executado com todas as configurações
3. **Geração de CSVs**: Resultados detalhados são salvos em arquivos CSV
4. **Análise Estatística**: Cálculo de métricas de desempenho
5. **Geração de Gráficos**: Visualizações comparativas para cada algoritmo
6. **Criação de Relatórios HTML**: Páginas web interativas com resultados

### Execução Individual (Opcional)

```bash
# Compilar e executar algoritmos específicos
javac BubbleSortJava.java
java BubbleSortJava

javac InsertionSortJava.java
java InsertionSortJava

javac MergeSortJava.java
java MergeSortJava

javac QuickSortJava.java
java QuickSortJava
```

## 📈 Métricas Coletadas

Cada execução do benchmark coleta as seguintes informações:

- **Algoritmo**: Nome do algoritmo testado
- **Modo**: Serial ou Paralela
- **Tamanho**: Tamanho do array ordenado
- **Tipo_de_Dados**: Tipo de distribuição dos dados
- **Profundidade**: Nível de paralelização (0 para serial)
- **Num_Threads_Estimado**: Número teórico de threads
- **Num_Threads_Utilizadas**: Número real de threads utilizadas
- **Amostra**: Número da amostra (1-5)
- **Tempo_ms**: Tempo de execução em milissegundos
- **Cpu_Count**: Número de CPUs disponíveis
- **Timestamp**: Data e hora da execução

## 📊 Análise dos Resultados

### Relatórios Gerados

1. **Página Principal** (`index.html`):
   - Visão geral de todos os algoritmos
   - Estatísticas comparativas
   - Links para análises detalhadas

2. **Páginas Individuais por Algoritmo**:
   - Gráficos de desempenho vs tamanho
   - Análise por tipo de dados
   - Cálculo de speedup (ganho com paralelização)
   - Comparação serial vs paralela
   - Tabelas resumidas com métricas

### Gráficos Incluídos

- **Tempo Médio vs Tamanho**: Comportamento assintótico
- **Desempenho por Tipo de Dados**: Sensibilidade aos dados de entrada
- **Speedup por Profundidade**: Eficiência da paralelização
- **Comparação Serial vs Paralela**: Ganhos de performance

## 🔧 Personalização

### Modificando Parâmetros do Benchmark

Edite as constantes no início de cada arquivo Java:

```java
// Exemplo de personalização no BubbleSortJava.java
private static final int[] SIZES = {1000, 5000, 10000, 25000};  // Adicione novos tamanhos
private static final String[] DATA_TYPES = {"random", "sorted", "reversed", "duplicates", "nearly-sorted"};
private static final int[] THREAD_LEVELS = {0, 1, 2, 3, 4};     // Mais níveis de paralelismo
private static final int SAMPLES = 10;                          // Mais amostras para estatística
```

### Adicionando Novos Algoritmos

1. Crie um novo arquivo Java seguindo o padrão existente
2. Implemente as versões serial e paralela
3. Adicione o nome do arquivo e algoritmo em `main.py`:
   ```python
   JAVA_FILES = [..., "NovoAlgoritmo.java"]
   ALGORITHM_NAMES = [..., "NovoAlgoritmo"]
   ```

## 🛠️ Características Técnicas

### Paralelização
- **Bubble/Insertion Sort**: Divisão do array em segmentos + merge
- **Merge/QuickSort**: Recursão paralela com controle de profundidade
- **Thread Pool**: ExecutorService com número otimizado de threads
- **Controle de Recursos**: Limitação baseada no número de CPUs

### Precisão das Medições
- Tempo medido em nanossegundos (convertido para ms)
- Múltiplas amostras para reduzir variabilidade
- Clone de arrays para evitar interferência entre testes

### Robustez do Sistema
- Tratamento de erros em leitura de CSV
- Normalização de formatos numéricos (vírgula/ponto decimal)
- Fallbacks para dados incompletos ou corrompidos

## 📋 Exemplo de Saída

```
Executando benchmark BubbleSort (Java)...

[Wed Dec 06 14:30:15 BRT 2023] Size=   1000 | Type=   random | Mode=  Serial | Depth=0 | EstThreads=  1 | Sample=1 | Time=15.342 ms
[Wed Dec 06 14:30:15 BRT 2023] Size=   1000 | Type=   random | Mode=Paralela | Depth=1 | EstThreads=  2 | Sample=1 | Time=8.156 ms
...

Benchmark concluído. Arquivo salvo: 'resultados_bubblesort_java.csv'
```

## 🔬 Análises Esperadas

1. **Complexidade Assintótica**: Confirmação do comportamento O(n²) vs O(n log n)
2. **Eficiência da Paralelização**: Speedup ideal vs speedup real
3. **Sensibilidade aos Dados**: Impacto do tipo de dados no desempenho
4. **Overhead de Threads**: Custo da comunicação entre threads vs ganhos

## 📝 Licença

Este projeto é destinado para fins educacionais e de pesquisa.

## 👥 Autores

Projeto desenvolvido para análise comparativa de algoritmos de ordenação.
Gabriel Abreu Cunha de Alencar
Pedro Luis Costa Silva

---

**Repositório**: https://github.com/AbreuGCA/Analise-de-Desempenho-dos-Algoritimos-de-Busca-BSMQ

Para dúvidas ou sugestões, abra uma issue no repositório do projeto.
