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
detector-distracao --config detector.toml --log-level DEBUG
```

Teclas:

- `q`: sair

## Configuração (`detector.toml`)

```toml
[detector]
no_face_frames_threshold = 30
eyes_closed_frames_threshold = 20
max_center_offset_ratio = 0.30

[runtime]
camera_index = 0
metrics_log_interval_frames = 30
```

## Testes

```bash
pytest
```
