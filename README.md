# Detector de Distração (Python)

MVP de detector de distração em tempo real usando webcam ou vídeo.

## O que detecta

- **Sem rosto visível** por um período contínuo.
- **Olhos fechados** por vários frames seguidos.
- **Rosto muito fora do centro** da tela (indicador de olhar para longe).

> Observação: este projeto é um ponto de partida. Para produção, o ideal é evoluir com landmarks faciais (ex.: MediaPipe).

## Requisitos

- Python 3.10+
- Webcam (para modo ao vivo)

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Execução

### 1) Webcam padrão

```bash
detector-distracao
```

### 2) Outra câmera

```bash
detector-distracao --camera 1
```

### 3) Testar com arquivo de vídeo

```bash
detector-distracao --source caminho/para/video.mp4
```

### 4) Ajustar sensibilidade

```bash
detector-distracao \
  --no-face-threshold 40 \
  --eyes-closed-threshold 25 \
  --center-offset-threshold 0.25
```

Teclas:

- `q`: sair

## Como testar

### Testes automatizados (sem webcam)

```bash
python -m pytest
```

Cobertura atual:

- Regras de decisão da função `evaluate_attention`.
- Comportamento temporal do `AttentionTracker` (acúmulo e reset de contadores).

### Teste manual (com webcam)

1. Rode `detector-distracao`.
2. Cenários rápidos:
   - Saia da frente da câmera por alguns segundos (esperado: `distraido_sem_rosto`).
   - Feche os olhos por alguns frames (esperado: `distraido_olhos_fechados`).
   - Vá para o canto da imagem (esperado: `distraido_olhando_longe`).

## Como evoluir

Sugestão de roadmap prático:

1. **Melhorar precisão**
   - Trocar Haar Cascades por landmarks (MediaPipe Face Mesh).
   - Calcular EAR (Eye Aspect Ratio) para detectar sonolência com mais robustez.

2. **Reduzir falsos positivos**
   - Suavização temporal (média móvel / histerese).
   - Thresholds por usuário (fase de calibração inicial).

3. **Observabilidade**
   - Log de eventos em CSV/JSON com timestamp.
   - Dashboard simples com frequência de distrações por minuto.

4. **Produto/Deploy**
   - API local (FastAPI) para servir estado em tempo real.
   - Empacotar em Docker e adicionar CI para rodar testes automaticamente.

## Estrutura

```text
src/detector/
  cli.py      # captura de vídeo e renderização
  logic.py    # regras de atenção/distração
  tracker.py  # estado temporal (contadores)
tests/
  test_logic.py
  test_tracker.py
```
