# Detector de Distração (Python)

Detector de distração em tempo real usando webcam ou vídeo, com foco em confiabilidade temporal.

## O que detecta

- **Sem rosto visível** por um período contínuo (em segundos).
- **Olhos fechados** por um período contínuo (em segundos).
- **Rosto fora do centro** por um período contínuo (em segundos).
- **Recuperação com histerese**: precisa manter atenção por alguns segundos antes de sair de alerta.

## Requisitos

- Python 3.10+
- Webcam (para modo ao vivo)

## Instalação

### Opção A (recomendada para desenvolvimento)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Opção B (instalação simples)

```bash
python -m venv .venv
source .venv/bin/activate
pip install opencv-python pytest
```

## Execução

### 1) Ajuda da CLI

```bash
detector-distracao --help
```

### 2) Webcam padrão

```bash
detector-distracao
```

### 3) Testar com arquivo de vídeo

```bash
detector-distracao --source caminho/para/video.mp4
```

### 4) Ajustar confiabilidade temporal (segundos)

```bash
detector-distracao \
  --no-face-threshold 1.2 \
  --eyes-closed-threshold 0.8 \
  --looking-away-threshold 1.0 \
  --recover-threshold 0.4 \
  --center-offset-threshold 0.30
```

Regras de validação da CLI:

- `--camera >= 0`
- `--no-face-threshold > 0`
- `--eyes-closed-threshold > 0`
- `--looking-away-threshold > 0`
- `--recover-threshold > 0`
- `--center-offset-threshold` entre `0.0` e `0.5`

Teclas:

- `q`: sair

## Como isso melhora a confiabilidade (Fase 2)

- Thresholds em **segundos** ao invés de frames (menos sensível a variação de FPS).
- Estado temporal com **histerese** para reduzir flicker de alertas.
- Backend de detecção desacoplado (`HaarSignalDetector`), abrindo caminho para trocar por MediaPipe sem reescrever a CLI/tracker.

## Como testar

### Testes automatizados (sem webcam)

```bash
python -m pytest
```

Cobertura atual inclui:

- Regras de decisão por tempo em `evaluate_attention`.
- Comportamento temporal do `AttentionTracker` (acúmulo por segundos, reset e histerese).
- Validação dos argumentos da CLI e erro amigável sem OpenCV.

### Teste manual (com webcam)

1. Rode `detector-distracao`.
2. Cenários rápidos:
   - Saia da frente da câmera por > `--no-face-threshold`.
   - Feche os olhos por > `--eyes-closed-threshold`.
   - Desloque-se para borda da imagem por > `--looking-away-threshold`.
3. Verifique que o status não volta imediatamente para "atento" ao primeiro frame bom (histerese).

## Troubleshooting

- **Erro `OpenCV não está instalado`**:
  - execute `pip install opencv-python`.
- **Ambiente sem acesso à internet/proxy**:
  - prefira um ambiente local com internet para instalar dependências;
  - ou use wheel local previamente baixado.

## Estrutura

```text
src/detector/
  cli.py      # execução e renderização
  logic.py    # regras de atenção/distração por tempo
  tracker.py  # estado temporal + histerese
  vision.py   # backend de sinais (Haar)
tests/
  test_cli.py
  test_logic.py
  test_tracker.py
```
