# 🌍 Projeto Gaia

Projeto Gaia é um jogo sério de simulação e estratégia educacional em 2D, desenvolvido para PC utilizando a Godot Engine. O jogador assume o papel de um Arquiteto de Ecossistemas, com a missão de restaurar biomas em colapso por meio da introdução e equilíbrio de espécies.

---

## 🚀 Como rodar o protótipo

### Pré-requisitos
- [Godot Engine 4.x](https://godotengine.org/download) instalado

### Passos
1. Abra o Godot Engine e selecione **Import Project**
2. Navegue até a pasta `Projeto-GAIA/` e selecione o arquivo `project.godot`
3. Clique em **Import & Edit**
4. Pressione **F5** (ou o botão ▶ Play) para rodar

### Estrutura de pastas
```
Projeto-GAIA/
├── fase_1.tscn          # Cena principal (Bioma Floresta)
├── fase_1.gd            # Controlador da fase (spawn, UI, tempo)
├── herbivoro_coelho.tscn/.gd  # Entidade: Herbívoro (coelho)
├── planta_carvalho.tscn/.gd   # Entidade: Planta (carvalho)
├── organismo_base.tscn  # Base reutilizável (Area2D + colisão)
├── scenes/              # Futuras cenas reutilizáveis
├── scripts/             # Scripts futuros desacoplados
├── assets/              # Arte, sons, etc.
└── systems/             # Sistemas globais (ex: sistema de tempo)
```

---

## 🎮 Como jogar o protótipo

### Ao iniciar
- A tela exibe um bioma de floresta (fundo verde) com um painel de controle no canto superior esquerdo.
- O jogador começa com **100 Pontos de Biodiversidade**.

### Adicionando espécies
| Ação | Tecla | Botão |
|------|-------|-------|
| Selecionar Planta | `1` | Botão "Planta [1]" |
| Selecionar Herbívoro | `2` | Botão "Herbivoro [2]" |
| Colocar no terreno | Clique esquerdo | — |

- **Planta** custa 10 pontos — estática, serve de alimento
- **Herbívoro** custa 25 pontos — se move, busca plantas, morre de fome sem comer

### Controle de tempo
| Ação | Tecla | Botão |
|------|-------|-------|
| Pausar / Despausar | `P` | Botão "Pausar [P]" |
| Velocidade normal | `N` | Botão "Normal [N]" |
| Velocidade 3× | `R` | Botão "Rapido [R]" |

### Loop de simulação
1. Herbívoros buscam a planta mais próxima automaticamente
2. Ao alcançar uma planta, consomem ela (remove do mapa)
3. Sem plantas, os herbívoros vagam aleatoriamente
4. Herbívoros morrem de fome após **20 segundos** sem comer
5. Os contadores de entidades no painel se atualizam em tempo real

---

## ✅ Cobertura do GDD (~30%)

- [x] Cena principal (Main/Forest) com bioma visual básico
- [x] Entidade Planta (produtor, grupo `comida`)
- [x] Entidade Herbívoro (movimento, busca por planta, vagação, fome/morte)
- [x] Inserção de espécies via clique no terreno
- [x] Sistema de Pontos de Biodiversidade (custo por espécie)
- [x] Painel de UI: botões, contadores de entidades, modo atual
- [x] Sistema de tempo: pausar, velocidade normal, acelerado (3×)
- [x] Uso de grupos Godot (`comida`, `herbivoros`) para comunicação entre entidades
- [x] `_unhandled_input` para evitar conflito entre cliques de UI e spawn
- [x] Estrutura de pastas do projeto (`scenes/`, `scripts/`, `assets/`, `systems/`)

## 🔜 Próximos Passos

### Técnicos
- [ ] Implementar Carnívoro (lobo) com busca por herbívoros
- [ ] Sistema de reprodução simples (herbívoro gera filhote após N refeições)
- [ ] Sistema de câmera livre (arrastar/zoom) para o PlayerController
- [ ] Separar sistema de tempo em autoload (`systems/SistemaTempo.gd`)
- [ ] Usar sinais para atualização de UI em vez de polling por `_process`
- [ ] Barra de fome visual no herbívoro (ProgressBar)

### Gameplay
- [ ] Bioma com tiles/terreno real (TileMapLayer)
- [ ] Pontos de biodiversidade regenerados com o tempo
- [ ] Eventos ecológicos (ex: seca reduz plantas)
- [ ] Sistema de análise de equilíbrio (alertas de desequilíbrio)
- [ ] Missões/objetivos por fase (ex: "mantenha 5 herbívoros por 60s")

---

# 🎯 Objetivo

Criar e manter ecossistemas saudáveis, aplicando conceitos de Biologia e Ecologia na prática. O jogo estimula o pensamento científico por meio do ciclo:

Diagnóstico → Intervenção → Observação

# 👥 Público-Alvo

Estudantes de 11 a 14 anos (Ensino Fundamental II)

Professores e mediadores educacionais

Entusiastas de jogos de simulação ecológica

Alinhado à BNCC, especialmente às habilidades relacionadas à biodiversidade, cadeias alimentares e equilíbrio ambiental.

# 🕹️ Principais Mecânicas

🌱 Introdução de espécies com Pontos de Biodiversidade

⏱️ Simulação em tempo real, com controle de velocidade

📊 Análise de dados ecológicos (população, biomassa, biodiversidade)

🧬 Evolução e adaptação genética de espécies

🧩 Desafios educativos, como reorganização de cadeias alimentares

🌎 Biomas Disponíveis

🌳 Floresta Temperada (tutorial)

🌴 Floresta Tropical

🏜️ Deserto

(Planejados: Taiga, Savana, Recife de Corais, Manguezal)

Cada bioma apresenta desafios específicos, como espécies invasoras, eventos climáticos extremos e desequilíbrios populacionais.

# 📖 Narrativa

Em um futuro marcado pelo colapso ecológico, a entidade Gaia escolhe um jovem ecologista para restaurar os biomas do planeta. Com o auxílio do Códice de Gaia, o jogador enfrenta desafios ambientais e descobre os impactos de uma corporação que explora os recursos naturais de forma predatória.

O objetivo final é restaurar o equilíbrio global e despertar uma nova consciência ecológica.

# 🎨 Estilo Visual

Pixel Art em alta resolução

Identidade visual inspirada em livros ilustrados

Paletas de cores adaptadas a cada bioma

Trilha sonora imersiva e efeitos ambientais dinâmicos

# 🛠️ Tecnologia

Desenvolvido com Godot Engine

Arquitetura baseada em nós (Nodes)

Uso de sinais (Signals) para eventos

Sistema de controle de tempo (pausa/aceleração)

# 🏆 Progressão e Recompensas

Desbloqueio de novos biomas

Novas espécies e mutações

Expansão do Códice com conteúdos educativos

Itens cosméticos para o personagem
