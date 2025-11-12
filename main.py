import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
sns.set_theme()

# ==========================================================
# CONFIGURAÇÕES
# ==========================================================
JAVA_FILES = [
    "BubbleSortJava.java",
    "InsertionSortJava.java",
    "MergeSortJava.java",
    "QuickSortJava.java"
]

CSV_FILES = [
    "resultados_bubblesort_java.csv",
    "resultados_insertionsort_java.csv",
    "resultados_mergesort_java.csv",
    "resultados_quicksort_java.csv"
]

ALGORITHM_NAMES = ["BubbleSort", "InsertionSort", "MergeSort", "QuickSort"]

# ==========================================================
# UTIL: parser robusto de CSV (corrige caso 'Tempo_ms' tenha sido escrito com vírgula)
# ==========================================================
def read_csv_flexible(path, expected_header=None, encoding="utf-8"):
    """
    Lê um CSV tentando consertar linhas onde o campo Tempo_ms foi dividido
    porque continha vírgula decimal. Retorna DataFrame com colunas do header.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, "r", encoding=encoding, errors="ignore") as f:
        raw_header = f.readline().strip("\n\r")
        header_cols = [c.strip() for c in raw_header.split(",")]
        rows = []
        for line in f:
            line = line.strip("\n\r")
            if line == "":
                continue
            parts = line.split(",")
            if len(parts) == len(header_cols):
                rows.append(parts)
            elif len(parts) > len(header_cols):
                # Heurística:
                # header: Algoritmo,Modo,Tamanho,Tipo_de_Dados,Profundidade,
                #         Num_Threads_Estimado,Num_Threads_Utilizadas,Amostra,
                #         Tempo_ms,Cpu_Count,Timestamp
                # Vamos reconstruir juntando campos extras que pertencem a Tempo_ms
                # assumimos que CPU_COUNT está na penúltima posição e Timestamp na última.
                # Portanto: juntar partes[8: len(parts)-2] -> Tempo_ms possivelmente com vírgulas
                if len(header_cols) >= 11:
                    pre = parts[:8]  # 0..7
                    cpu = parts[-2]
                    ts = parts[-1]
                    tempo_parts = parts[8:-2]
                    tempo = ",".join(tempo_parts)
                    fixed = pre + [tempo, cpu, ts]
                    # Se ainda tiver diferença de tamanho, pad com empty
                    if len(fixed) == len(header_cols):
                        rows.append(fixed)
                    else:
                        # fallback: truncate or pad
                        fixed = (fixed + [""] * len(header_cols))[:len(header_cols)]
                        rows.append(fixed)
                else:
                    # fallback genérico: truncate/pad to match header
                    fixed = (parts + [""] * len(header_cols))[:len(header_cols)]
                    rows.append(fixed)
            else:
                # menos campos do que header -> pular
                continue

    df = pd.DataFrame(rows, columns=header_cols)
    # remover BOM se necessário
    df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]
    return df

# ==========================================================
# COMPILAÇÃO / EXECUÇÃO JAVA
# ==========================================================
def compile_and_run_java():
    """Compila e executa todos os arquivos Java (se existirem)."""
    print("⚙️ Compilando e executando algoritmos Java...")
    for java_file in JAVA_FILES:
        if not os.path.exists(java_file):
            print(f"✗ Arquivo {java_file} não encontrado. Pulando.")
            continue
        class_name = os.path.splitext(java_file)[0]
        try:
            compile_cmd = f"javac -d . {java_file}"
            r = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"✗ Erro ao compilar {java_file}: {r.stderr.strip()}")
                continue
            print(f"✓ {java_file} compilado.")

            run_cmd = f"java -cp . {class_name}"
            r = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"✗ Erro ao executar {class_name}: {r.stderr.strip()}")
            else:
                print(f"✓ {class_name} executado.")
        except Exception as e:
            print(f"✗ Exceção tratando {java_file}: {e}")

# ==========================================================
# LEITURA E NORMALIZAÇÃO DOS DADOS
# ==========================================================
def load_and_analyze_data():
    dataframes = {}
    for csv_file, algo_name in zip(CSV_FILES, ALGORITHM_NAMES):
        if not os.path.exists(csv_file):
            print(f"✗ {csv_file} não encontrado. Pulando.")
            continue
        try:
            df = read_csv_flexible(csv_file)
            # Normalizar nomes de colunas
            df.columns = [c.strip() for c in df.columns]

            # Colunas esperadas (se o arquivo estiver correto)
            expected = ["Algoritmo","Modo","Tamanho","Tipo_de_Dados","Profundidade",
                        "Num_Threads_Estimado","Num_Threads_Utilizadas","Amostra",
                        "Tempo_ms","Cpu_Count","Timestamp"]

            # Se o header for diferente, tentar mapear pelo conteúdo
            if "Tempo_ms" not in df.columns and any("Tempo" in c for c in df.columns):
                # tenta renomear colunas aproximadas
                for c in df.columns:
                    if "Tempo" in c:
                        df.rename(columns={c: "Tempo_ms"}, inplace=True)
                        break

            # Limpeza do campo Tempo_ms: trocar vírgula decimal por ponto e converter
            if "Tempo_ms" in df.columns:
                df["Tempo_ms"] = df["Tempo_ms"].astype(str).str.replace(".", ".", regex=False)
                # trocar vírgula decimal por ponto
                df["Tempo_ms"] = df["Tempo_ms"].str.replace(",", ".", regex=False)
                df["Tempo_ms"] = pd.to_numeric(df["Tempo_ms"], errors="coerce")

            # Converter outras colunas numéricas
            for col in ["Tamanho","Profundidade","Num_Threads_Utilizadas","Num_Threads_Estimado","Amostra","Cpu_Count"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").str.strip(), errors="coerce")

            # Timestamp: se existir, manter como string (pode ser parseado se necessário)
            if "Timestamp" in df.columns:
                df["Timestamp"] = df["Timestamp"].astype(str).str.strip()

            # Remover linhas sem Tempo_ms
            if "Tempo_ms" in df.columns:
                before = len(df)
                df = df[~df["Tempo_ms"].isna()].copy()
                after = len(df)
                if after < before:
                    print(f"⚠️ {csv_file}: removidas {before-after} linhas sem Tempo_ms numérico.")

            # Forçar colunas de interesse existam (evita KeyError mais abaixo)
            # Se coluna não existir, criar com valores vazios/zeros
            for c in ["Modo","Tamanho","Tipo_de_Dados","Profundidade","Num_Threads_Utilizadas","Tempo_ms","Timestamp"]:
                if c not in df.columns:
                    df[c] = np.nan

            # Ordenar
            df = df.sort_values(by=["Tamanho","Profundidade"]).reset_index(drop=True)

            dataframes[algo_name] = df
            print(f"✓ {csv_file} carregado como '{algo_name}' ({len(df)} linhas válidas).")
        except Exception as e:
            print(f"✗ Erro ao carregar {csv_file}: {e}")

    return dataframes

# ==========================================================
# GRÁFICOS E PÁGINAS
# ==========================================================
def generate_stats_html(algo_name, df, serial_data, parallel_data):
    try:
        total_samples = len(df)
        time_range = "N/A"
        if "Timestamp" in df.columns and df["Timestamp"].notna().any():
            try:
                # pegar os primeiros/últimos strings
                time_range = f"{df['Timestamp'].min()} até {df['Timestamp'].max()}"
            except:
                time_range = "N/A"

        best_serial = serial_data["Tempo_ms"].min() if (not serial_data.empty and "Tempo_ms" in serial_data.columns) else np.nan
        best_parallel = parallel_data["Tempo_ms"].min() if (not parallel_data.empty and "Tempo_ms" in parallel_data.columns) else np.nan
        avg_serial = serial_data["Tempo_ms"].mean() if (not serial_data.empty and "Tempo_ms" in serial_data.columns) else np.nan
        avg_parallel = parallel_data["Tempo_ms"].mean() if (not parallel_data.empty and "Tempo_ms" in parallel_data.columns) else np.nan

        speedup_avg = 0.0
        if pd.notna(avg_serial) and pd.notna(avg_parallel) and avg_parallel > 0:
            speedup_avg = avg_serial / avg_parallel

        def fmt(x):
            if pd.isna(x):
                return "N/A"
            try:
                return f"{x:.2f} ms"
            except:
                return str(x)

        return f"""
            <div class="stats">
                <h3>📈 Estatísticas Gerais</h3>
                <p><strong>Total de Amostras:</strong> {total_samples}</p>
                <p><strong>Período de Execução:</strong> {time_range}</p>
                <p><strong>Melhor Tempo Serial:</strong> {fmt(best_serial)}</p>
                <p><strong>Melhor Tempo Paralelo:</strong> {fmt(best_parallel)}</p>
                <p><strong>Speedup Médio:</strong> {speedup_avg:.2f}x</p>
                <p><strong>Tempo Serial Médio:</strong> {fmt(avg_serial)}</p>
                <p><strong>Tempo Paralelo Médio:</strong> {fmt(avg_parallel)}</p>
            </div>
        """
    except Exception as e:
        return f"<div class='stats'><p>Erro ao gerar estatísticas: {e}</p></div>"

def create_html_template(algo_name, plot_filename, stats_html, df):
    # gerar tabela resumida
    rows = ""
    if all(col in df.columns for col in ['Tamanho','Tipo_de_Dados','Modo','Profundidade','Num_Threads_Utilizadas','Tempo_ms']):
        summary = df.groupby(['Tamanho','Tipo_de_Dados','Modo','Profundidade','Num_Threads_Utilizadas'])['Tempo_ms'].mean().reset_index()
        for _, r in summary.iterrows():
            try:
                tsize = int(r['Tamanho']) if pd.notna(r['Tamanho']) else ""
                pdepth = int(r['Profundidade']) if pd.notna(r['Profundidade']) else ""
                nth = int(r['Num_Threads_Utilizadas']) if pd.notna(r['Num_Threads_Utilizadas']) else ""
                rows += f"""
                <tr>
                    <td>{tsize}</td>
                    <td>{r['Tipo_de_Dados']}</td>
                    <td>{r['Modo']}</td>
                    <td>{pdepth}</td>
                    <td>{nth}</td>
                    <td>{r['Tempo_ms']:.2f}</td>
                </tr>
                """
            except Exception:
                continue
    else:
        rows = "<tr><td colspan='6'>Dados incompletos para gerar tabela</td></tr>"

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="utf-8"><title>Análise - {algo_name}</title>
    <style>
        body{{font-family:Arial;background:#f5f5f5;padding:20px}}
        .container{{max-width:1100px;margin:auto;background:#fff;padding:20px;border-radius:8px}}
        table{{width:100%;border-collapse:collapse}}
        th,td{{padding:8px;border-bottom:1px solid #ddd}}
        th{{background:#3498db;color:#fff}}
        .stats{{background:#ecf0f1;padding:12px;border-radius:6px}}
    </style>
    </head>
    <body>
    <div class="container">
        <h1>📊 Análise de {algo_name}</h1>
        {stats_html}
        <div style="margin:20px 0"><img src="{plot_filename}" style="max-width:100%"></div>
        <h3>📋 Dados Resumidos</h3>
        <table>
            <tr><th>Tamanho</th><th>Tipo</th><th>Modo</th><th>Profundidade</th><th>Threads</th><th>Tempo Médio (ms)</th></tr>
            {rows}
        </table>
        <p style="margin-top:16px"><a href="index.html">← Voltar</a></p>
    </div>
    </body></html>
    """

def create_algorithm_page(algo_name, df):
    try:
        plt.figure()
        plt.close()
        fig, axes = plt.subplots(2,2, figsize=(15,11))
        ax1, ax2, ax3, ax4 = axes.flatten()
        fig.suptitle(f"Análise de Desempenho - {algo_name}", fontsize=16)

        # garantir colunas corretas
        serial_data = df[df['Modo'].astype(str).str.strip() == 'Serial']
        parallel_data = df[df['Modo'].astype(str).str.strip() == 'Paralela']

        # G1: tempo médio por tamanho
        try:
            sgrp = serial_data.groupby('Tamanho')['Tempo_ms'].mean().dropna()
            pgrp = parallel_data.groupby('Tamanho')['Tempo_ms'].mean().dropna()
            if not sgrp.empty:
                ax1.plot(sgrp.index, sgrp.values, marker='o', label='Serial')
            if not pgrp.empty:
                ax1.plot(pgrp.index, pgrp.values, marker='s', label='Paralela')
            ax1.set_xlabel("Tamanho"); ax1.set_ylabel("Tempo (ms)")
            ax1.set_title("Tempo Médio vs Tamanho")
            ax1.legend(); ax1.grid(alpha=0.3)
        except Exception as e:
            ax1.text(0.5,0.5,f"Erro: {e}",ha='center')

        # G2: tempo por tipo de dados
        try:
            types = df['Tipo_de_Dados'].astype(str).unique()
            x = np.arange(len(types))
            svals = [serial_data[serial_data['Tipo_de_Dados']==t]['Tempo_ms'].mean() for t in types]
            pvals = [parallel_data[parallel_data['Tipo_de_Dados']==t]['Tempo_ms'].mean() for t in types]
            ax2.bar(x-0.2, svals, 0.4, label='Serial'); ax2.bar(x+0.2, pvals, 0.4, label='Paralela')
            ax2.set_xticks(x); ax2.set_xticklabels(types, rotation=25)
            ax2.set_title("Desempenho por Tipo de Dados"); ax2.legend(); ax2.grid(alpha=0.3)
        except Exception as e:
            ax2.text(0.5,0.5,f"Erro: {e}",ha='center')

        # G3: speedup por profundidade
        try:
            speedups = []
            depths = sorted([d for d in df['Profundidade'].unique() if pd.notna(d)])
            for d in depths:
                if d == 0: continue
                for size in df['Tamanho'].unique():
                    st = serial_data[serial_data['Tamanho']==size]['Tempo_ms'].mean()
                    pt = df[(df['Tamanho']==size)&(df['Profundidade']==d)]['Tempo_ms'].mean()
                    if pd.notna(st) and pd.notna(pt) and pt>0:
                        speedups.append({'Profundidade':int(d),'Speedup':st/pt})
            if speedups:
                sdf = pd.DataFrame(speedups)
                sns.boxplot(data=sdf, x='Profundidade', y='Speedup', ax=ax3)
                ax3.axhline(1, color='red', linestyle='--')
                ax3.set_title("Ganho (Speedup)")
            else:
                ax3.text(0.5,0.5,"Dados insuficientes para cálculo de speedup", ha='center')
        except Exception as e:
            ax3.text(0.5,0.5,f"Erro: {e}",ha='center')

        # G4: comparação Serial x Paralela por tamanho
        try:
            comb = df[df['Modo'].isin(['Serial','Paralela'])].dropna(subset=['Tempo_ms'])
            if not comb.empty:
                mean_df = comb.groupby(['Modo','Tamanho'])['Tempo_ms'].mean().reset_index()
                sns.barplot(data=mean_df, x='Tamanho', y='Tempo_ms', hue='Modo', ax=ax4)
                ax4.set_title("Serial vs Paralela por Tamanho")
            else:
                ax4.text(0.5,0.5,"Dados insuficientes para comparação",ha='center')
        except Exception as e:
            ax4.text(0.5,0.5,f"Erro: {e}",ha='center')

        plt.tight_layout(rect=[0,0,1,0.97])
        plot_filename = f"{algo_name.lower()}_analysis.png"
        plt.savefig(plot_filename, dpi=200, bbox_inches='tight')
        plt.close(fig)

        stats_html = generate_stats_html(algo_name, df, serial_data, parallel_data)
        html = create_html_template(algo_name, plot_filename, stats_html, df)
        with open(f"{algo_name.lower()}_analysis.html","w",encoding="utf-8") as f:
            f.write(html)
        print(f"✓ Página criada: {algo_name.lower()}_analysis.html")
    except Exception as e:
        print(f"✗ Erro ao criar página de {algo_name}: {e}")

# ==========================================================
# INDEX
# ==========================================================
def create_index_page(dataframes):
    cards = ""
    for algo, df in dataframes.items():
        avg = df['Tempo_ms'].mean() if 'Tempo_ms' in df.columns else np.nan
        cards += f"""
            <div style="background:#ecf0f1;padding:12px;border-radius:8px;margin-bottom:10px;">
                <h3>{algo}</h3>
                <p>Amostras: {len(df)}</p>
                <p>Tempo médio: {avg:.2f} ms</p>
                <a href="{algo.lower()}_analysis.html">Ver detalhes</a>
            </div>
        """
    html = f"""<html><head><meta charset="utf-8"><title>Benchmark</title></head>
    <body style="font-family:Arial;background:#f5f5f5;padding:20px">
    <div style="max-width:1000px;margin:auto;background:#fff;padding:20px;border-radius:8px">
        <h1>🏆 Benchmark</h1>
        {cards}
    </div></body></html>"""
    with open("index.html","w",encoding="utf-8") as f:
        f.write(html)
    print("✓ index.html criado.")

# ==========================================================
# MAIN
# ==========================================================
def main():
    print("🚀 Iniciando benchmark")
    print("="*40)
    # 1) compilar e executar java (opcional)
    compile_and_run_java()

    # 2) carregar CSVs
    print("\n📊 Carregando dados...")
    dataframes = load_and_analyze_data()
    if not dataframes:
        print("❌ Nenhum dado válido carregado. Verifique os CSVs.")
        return

    # 3) gerar páginas por algoritmo
    for algo, df in dataframes.items():
        create_algorithm_page(algo, df)

    # 4) index
    create_index_page(dataframes)
    print("\n✅ Concluído. Arquivos HTML e PNG gerados.")

if __name__ == "__main__":
    main()
