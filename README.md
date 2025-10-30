# Análise de Desempenho do QuickSort Serial vs Paralelo

Este projeto implementa e compara diferentes versões do algoritmo QuickSort, analisando seu desempenho em diversos cenários. O código foi desenvolvido em Python e inclui uma implementação serial tradicional e uma versão paralela utilizando threads.

## 📋 Estrutura do Projeto

O projeto consiste em dois arquivos principais:
- `quicksort.py`: Contém as implementações do algoritmo e código de benchmark
- `resultados_quicksort_powerbi.csv`: Arquivo de saída com os resultados das análises

## 🔍 Detalhes da Implementação

### Algoritmos Implementados

1. **QuickSort Serial**
   - Implementação não in-place (didática)
   - Utiliza abordagem de divisão em três partes (left, middle, right)
   - Função: `quicksort_serial()`

2. **QuickSort Paralelo**
   - Implementação com paralelismo usando ThreadPoolExecutor
   - Controle de profundidade para limitar criação de threads
   - Função: `quicksort_parallel()`

### Configurações do Benchmark

- **Tamanhos de Array**: 10.000, 50.000 e 100.000 elementos
- **Tipos de Dados**:
  - `random`: Números aleatórios
  - `sorted`: Lista ordenada
  - `reversed`: Lista em ordem reversa
  - `duplicates`: Lista com valores duplicados
- **Níveis de Thread**: 0 (serial), 1, 2 e 3 níveis de profundidade
- **Amostras**: 5 execuções para cada configuração

## 📊 Coleta de Dados

O benchmark coleta as seguintes informações:
- Algoritmo utilizado
- Modo de execução (Serial/Paralelo)
- Tamanho do array
- Tipo de dados
- Profundidade de threads
- Número estimado de threads
- Número real de threads utilizadas
- Número da amostra
- Tempo de execução (ms)
- Número de CPUs disponíveis
- Timestamp da execução

## 💾 Formato de Saída

Os resultados são salvos em um arquivo CSV (`resultados_quicksort_powerbi.csv`) otimizado para análise no Power BI, contendo todas as métricas coletadas durante a execução.

## 🚀 Como Executar

1. Certifique-se de ter Python instalado
2. Execute o script:
   ```powershell
   python quicksort.py
   ```

## 🛠️ Personalização

Você pode ajustar as seguintes variáveis no início do código:
- `RANDOM_SEED`: Semente para geração de números aleatórios
- `SIZES`: Tamanhos dos arrays para teste
- `DATA_TYPES`: Tipos de dados para teste
- `THREAD_LEVELS`: Níveis de paralelização
- `SAMPLES`: Número de amostras por configuração
- `OUTPUT_CSV`: Nome do arquivo de saída

## 📈 Análise dos Resultados

Os resultados podem ser analisados no Power BI, permitindo a criação de visualizações e comparações detalhadas entre:
- Desempenho serial vs paralelo
- Impacto do tamanho do array
- Efeito dos diferentes tipos de dados
- Eficiência da paralelização em diferentes níveis

## 🔬 Características Técnicas

- Utiliza `ThreadPoolExecutor` para gerenciamento de threads
- Implementa controle de profundidade para otimizar uso de recursos
- Considera o número de CPUs disponíveis para limitar threads
- Inclui medição precisa de tempo usando `time.perf_counter()`
- Gera datasets variados para teste abrangente

## 📌 Observações

- A implementação do QuickSort é didática (não in-place) para facilitar compreensão
- O número real de threads utilizadas é limitado pelo número de CPUs disponíveis
- Os resultados podem variar dependendo do hardware e carga do sistema