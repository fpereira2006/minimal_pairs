from kokoro import KPipeline
import soundfile as sf
import numpy as np
import os
import string

# uv run kokoro_basic.py
# https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md

# --- Nova função para cortar o áudio ---
def trim_audio_start(audio_data, samplerate, duration_ms):
    """
    Corta o início do array de áudio com base na duração especificada em milissegundos.
    """
    # Calcula o número de amostras a serem removidas
    # (amostras por segundo) * (segundos a remover)
    # 1000 ms = 1 segundo
    samples_to_remove = int(samplerate * (duration_ms / 1000.0))
    
    # Retorna o array fatiado, começando após as amostras removidas
    return audio_data[samples_to_remove:]
# ---------------------------------------

# Configurações iniciais
lang_code = "a"
pipeline = KPipeline(lang_code)
speed = 0.80
output_folder = "audios"
input_file = "input.txt" # Nome do arquivo de entrada
output_samplerate = 24000 # Taxa de amostragem padrão (usada na geração e no salvamento)
trim_duration_ms = [870, 690, 600, 940] # <-- Define quantos milissegundos remover do início
voices = ['af_heart', 'am_eric', 'af_kore', 'am_michael']

# Cria a pasta de saída se não existir
os.makedirs(output_folder, exist_ok=True)

print(f"Lendo frases do arquivo: {input_file}")

# Abre e lê o arquivo linha por linha
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Erro: O arquivo '{input_file}' não foi encontrado.")
    exit()

# Processa cada linha do arquivo
for line_text in lines:
    i = 1
    for voice in voices:
        # ... (código existente para preparar a frase e nome do arquivo) ...
        phrase = 'What is ' + line_text.strip()
    #    phrase = line_text.strip()
        
        if not phrase:
            continue

        translator = str.maketrans('', '', string.punctuation)
        filename_base = phrase.translate(translator)
        filename_base = filename_base.replace('What is ', '')
        filename_base = filename_base.replace(' ', '_')
        filepath = os.path.join(output_folder, f"{filename_base}_{i}.wav")

        print(f"Gerando áudio para a frase: '{phrase}'")
        generator = pipeline(
            phrase,
            voice, # Exemplo de voz, verifique as opções na documentação do Kokoro
            speed=speed
        )

        audio_chunks = []
        for gs, ps, audio in generator:
            audio_chunks.append(audio)

        audio_all = np.concatenate(audio_chunks)

        # --- Aplica o corte de 1200 ms aqui ---
        if len(audio_all) > 0 and trim_duration_ms[i-1] > 0:
            audio_trimmed = trim_audio_start(audio_all, output_samplerate, trim_duration_ms[i-1])
            print(f"Áudio cortado: Removidos {trim_duration_ms[i-1]} ms do início.")
        else:
            audio_trimmed = audio_all

        # Salva o arquivo de áudio na pasta "audios" (usando a versão cortada)
        sf.write(filepath, audio_trimmed, samplerate=output_samplerate)
        print(f"Arquivo salvo em: {filepath}\n")
        i += 1

print("Processamento concluído.")
