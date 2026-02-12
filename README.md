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

Teclas:

- `q`: sair

## Testes

```bash
pytest
```

## Planejamento de modernização

### Objetivos de evolução

- Aumentar **precisão e robustez** da detecção em cenários reais (variação de luz, ângulo e distância).
- Reduzir **falsos positivos** com lógica temporal e calibração por usuário.
- Evoluir o MVP para uma base pronta para **piloto em ambiente de trabalho/estudo**.

### Fase 1 — Estabilização técnica (curto prazo, 1 a 2 semanas)

- Modularizar pipeline em componentes explícitos: captura, inferência, pós-processamento e UI.
- Incluir configuração por arquivo (`.toml`/`.yaml`) para limiares e parâmetros de câmera.
- Melhorar observabilidade local com logs estruturados (nível `INFO`/`DEBUG`) e métricas simples (FPS, taxa de detecção).
- Ampliar testes unitários cobrindo casos de borda (limiar exato, ausência intermitente de rosto, jitter no centro).

### Fase 2 — Modernização do motor de visão (médio prazo, 2 a 4 semanas)

- Migrar de Haar Cascades para **landmarks faciais** (MediaPipe Face Mesh ou modelo equivalente).
- Substituir heurística de olhos abertos/fechados por métrica mais confiável (ex.: EAR — Eye Aspect Ratio).
- Introduzir suavização temporal (janela móvel/exponencial) para reduzir variações frame a frame.
- Criar modo de calibração inicial de 20–30 segundos para personalizar limiares por usuário.

### Fase 3 — Produto e operação (médio/longo prazo, 4 a 8 semanas)

- Adicionar interface com eventos e timeline (estado atual, histórico de distrações, duração por estado).
- Exportar sessões em JSON/CSV para análise posterior.
- Implementar modo headless para execução em background e integração com outros sistemas.
- Definir política de privacidade local (processamento local por padrão, sem gravação automática de vídeo).

### Fase 4 — Qualidade para produção (contínuo)

- Pipeline de CI com lint + testes + checagens de tipo.
- Benchmarks mínimos por plataforma (latência, uso de CPU, estabilidade por tempo de execução).
- Testes com dataset controlado para medir precisão por cenário.
- Versionamento semântico e changelog automatizado.

### Backlog priorizado (top 10)

1. Extrair pipeline de vídeo para serviços separados.
2. Adicionar arquivo de configuração externo.
3. Criar camada de métricas (FPS/tempo de inferência).
4. Implementar EAR com landmarks faciais.
5. Introduzir suavização temporal.
6. Adicionar calibração por usuário.
7. Exibir dashboard simples de estados e alertas.
8. Exportar relatório de sessão.
9. Preparar execução headless.
10. Criar workflow de CI completo.

### Indicadores de sucesso

- Redução de falsos alertas em pelo menos **30%** versus baseline atual.
- FPS estável acima de **20** em máquina de referência.
- Cobertura de testes unitários acima de **85%** na camada de lógica.
- Tempo de setup para novo ambiente abaixo de **10 minutos**.
