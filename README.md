# Detector de Distração (Python)

MVP de detector de distração em tempo real usando a webcam.

## O que detecta

- **Sem rosto visível** por um período contínuo.
- **Olhos fechados** por vários frames seguidos.
- **Rosto muito fora do centro** da tela (indicador de olhar para longe).

> Observação: este projeto é um ponto de partida. Para produção, o ideal é evoluir com modelos de landmarks faciais (ex.: MediaPipe).

## Requisitos

- Python 3.10+
- Webcam

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Execução

```bash
detector-distracao
```

Com configuração e logs detalhados:

```bash
detector-distracao --config detector.toml --log-level DEBUG --video-cooldown-seconds 0
```


O app abre por padrão o vídeo `https://www.youtube.com/shorts/3tSGAhyQAKA` quando há transição de **atento -> distraído**.
Você pode trocar com `--distraction-video-url` e usar `--video-cooldown-seconds` para controlar intervalo mínimo entre aberturas.
Para teste rápido, pressione `v` para forçar abertura manual do vídeo (respeita cooldown).

Se não abrir, rode com `--log-level DEBUG` e pressione `v`: o log vai mostrar o motivo (`motivo=...`), por exemplo `cooldown_active` ou falha do browser do sistema.


Teclas:

- `q`: sair
- `v`: testar abertura manual do vídeo
- `1`/`2`: diminuir/aumentar limiar de sem rosto
- `3`/`4`: diminuir/aumentar limiar de olhos fechados
- `5`/`6`: diminuir/aumentar tolerância de desvio do centro
- `7`/`8`: diminuir/aumentar janela de suavização temporal

## Configuração (`detector.toml`)

```toml
[detector]
no_face_frames_threshold = 30
eyes_closed_frames_threshold = 20
max_center_offset_ratio = 0.30
smoothing_window_size = 5

[runtime]
camera_index = 0
metrics_log_interval_frames = 30
```

O parâmetro `smoothing_window_size` aplica votação temporal para estabilizar mudanças rápidas de estado.

## Testes

```bash
pytest
```
