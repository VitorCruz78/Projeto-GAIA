# Manual de Configuração do Ambiente de Desenvolvimento
## Projeto Gaia

**Versão:** 1.0  
**Data:** 2026-05-28  
**Engine:** Godot Engine 4.6 (Standard)

---

## 1. Sobre o Projeto

**Projeto Gaia** é um jogo sério de simulação ecológica 2D desenvolvido com **Godot Engine 4.6**
em GDScript. O jogador assume o papel de um Arquiteto de Ecossistemas com a missão de restaurar
biomas em colapso, aplicando conceitos de Biologia e Ecologia (cadeias alimentares, equilíbrio
de populações, biodiversidade). O jogo é alinhado à BNCC e voltado a estudantes de 11 a 14 anos.

Este manual descreve como configurar o ambiente de desenvolvimento local a partir do arquivo ZIP
do projeto.

---

## 2. Pré-requisitos

Antes de iniciar, verifique que seu computador atende aos seguintes requisitos:

| Requisito | Mínimo |
|---|---|
| Sistema operacional | Windows 10/11, macOS 12+, ou Linux (64-bit) |
| RAM | 4 GB |
| Armazenamento livre | 500 MB |
| Placa de vídeo | Suporte a Vulkan 1.0, Direct3D 12, ou OpenGL 3.3 |

> **Nota:** Godot 4.x exige suporte a Vulkan ou D3D12 por padrão. Hardware mais antigo pode usar
> o renderer `Compatibility` (OpenGL 3.3) — veja a Seção 7 para instruções.

**O que você precisará:**
- Arquivo ZIP do projeto fornecido (`projeto-gaia.zip`)
- Acesso à internet para baixar a Godot Engine

---

## 3. Instalação da Godot Engine 4.6

Baixe sempre a versão **4.6 Standard** (não a versão .NET/C#).  
URL oficial: [https://godotengine.org/download](https://godotengine.org/download)

### 3.1 Windows

1. Acesse [https://godotengine.org/download/windows/](https://godotengine.org/download/windows/)
2. Baixe o arquivo **"Godot Engine - Windows (64-bit)"** (ex.: `Godot_v4.6-stable_win64.exe.zip`)
3. Extraia o ZIP em uma pasta de sua escolha (ex.: `C:\Ferramentas\Godot\`)
4. O executável extraído (`Godot_v4.6-stable_win64.exe`) **não requer instalação** — é portátil
5. Execute o arquivo diretamente; o Project Manager abrirá

> **Permissão do Windows Defender:** Se o SmartScreen bloquear a execução, clique em
> **"Mais informações" → "Executar assim mesmo"**.

**Verificação:** A janela "Project Manager" da Godot abre sem mensagens de erro.

---

### 3.2 macOS

1. Acesse [https://godotengine.org/download/macos/](https://godotengine.org/download/macos/)
2. Baixe o arquivo **"Godot Engine - macOS (Universal)"** (ex.: `Godot_v4.6-stable_macos.universal.zip`)
   - A build Universal funciona em Macs com processador Intel **e** Apple Silicon (M1/M2/M3)
3. Extraia o ZIP — o resultado é `Godot.app`
4. Arraste `Godot.app` para a pasta `/Applications`
5. Na primeira execução, o Gatekeeper bloqueará o app. Para liberar:
   - Abra **System Settings → Privacy & Security**
   - Role até a mensagem `"Godot" was blocked from use...`
   - Clique em **Open Anyway**
   - Confirme no diálogo seguinte

> **Alternativa via terminal:**
> ```bash
> xattr -dr com.apple.quarantine /Applications/Godot.app
> ```

**Verificação:** A janela "Project Manager" da Godot abre sem mensagens de erro.

---

### 3.3 Linux

1. Acesse [https://godotengine.org/download/linux/](https://godotengine.org/download/linux/)
2. Baixe o arquivo **"Godot Engine - Linux (64-bit)"**  
   (ex.: `Godot_v4.6-stable_linux.x86_64.zip`)
3. Extraia o ZIP e torne o executável executável:

```bash
unzip Godot_v4.6-stable_linux.x86_64.zip
chmod +x Godot_v4.6-stable_linux.x86_64
```

4. Execute diretamente:

```bash
./Godot_v4.6-stable_linux.x86_64
```

> **Opcional — adicionar ao PATH:**
> ```bash
> sudo mv Godot_v4.6-stable_linux.x86_64 /usr/local/bin/godot4
> # A partir disso, basta digitar: godot4
> ```

> **Dependências (Ubuntu/Debian):** Se o app não abrir, instale as dependências de Vulkan:
> ```bash
> sudo apt update && sudo apt install libvulkan1 mesa-vulkan-drivers
> ```

**Verificação:** A janela "Project Manager" da Godot abre sem mensagens de erro.

---

## 4. Configuração do Projeto

### 4.1 Extraindo o arquivo ZIP

1. Crie uma pasta dedicada para o projeto, por exemplo:
   - Windows: `C:\Projetos\ProjetoGaia\`
   - macOS/Linux: `~/Documentos/ProjetoGaia/`
2. Extraia **todo o conteúdo** do arquivo `projeto-gaia.zip` dentro dessa pasta
3. Confirme que o arquivo `project.godot` está na **raiz** da pasta extraída:

```
ProjetoGaia/
├── project.godot      ← deve estar aqui
├── autoloads/
├── scenes/
├── scripts/
├── assets/
└── ...
```

> **Atenção:** Alguns descompactadores criam uma subpasta extra ao extrair.  
> Se o `project.godot` estiver em `ProjetoGaia/projeto-gaia/project.godot`, mova os arquivos  
> um nível acima.

### 4.2 Importando o projeto na Godot

1. Abra a Godot Engine — o **Project Manager** será exibido
2. Clique em **Import**
3. Navegue até a pasta onde o projeto foi extraído e selecione o arquivo `project.godot`
4. Clique em **Import & Edit**
5. Aguarde a importação dos assets — na primeira vez, esse processo pode levar **1 a 2 minutos**
6. O editor da Godot abrirá com o projeto carregado

---

## 5. Executando o Jogo

Com o projeto aberto no editor da Godot:

1. Pressione **F5** (ou clique no botão ▶ **Run Project** na barra superior direita)
2. A cena principal `scenes/menu_principal.tscn` será carregada automaticamente
3. Uma janela separada abrirá exibindo o **Menu Principal** do jogo

> A cena de entrada está configurada em `project.godot`:
> `run/main_scene = "res://scenes/menu_principal.tscn"`

**Resultado esperado:** Menu principal do Projeto Gaia é exibido na janela de jogo.

---

## 6. Estrutura de Pastas do Projeto

```
projeto-gaia/
├── project.godot              # Configuração do projeto — ponto de entrada para a Godot
├── autoloads/
│   └── game_manager.gd        # Singleton global (pontuação, estado de jogo)
├── scenes/                    # Todas as cenas do jogo (.tscn)
│   ├── menu_principal.tscn    # Cena inicial (main_scene)
│   ├── mapa_mundo.tscn        # Seleção de bioma/fase
│   ├── fase_1_floresta.tscn   # Fase 1 — Floresta Temperada
│   ├── fase_2_tropical.tscn   # Fase 2 — Floresta Tropical
│   ├── fase_3_deserto.tscn    # Fase 3 — Deserto
│   ├── cutscene_intro.tscn    # Cutscene de introdução narrativa
│   └── codice_gaia.tscn       # Enciclopédia educacional in-game
├── scripts/                   # Scripts GDScript reutilizáveis e desacoplados
├── assets/
│   ├── sprites/               # Sprites dos personagens, organismos e UI
│   └── tilesets/              # Tilesets dos biomas
├── systems/                   # Sistemas globais (ex.: controle de tempo, balanceamento)
└── organismos/                # Entidades dos ecossistemas (plantas, herbívoros, etc.)
```

> **Arquivos de script:** Cada cena `.tscn` tem um script `.gd` correspondente de mesmo nome
> (ex.: `fase_1_floresta.tscn` ↔ `scenes/fase_1_floresta.gd`).

---

## 7. Solução de Problemas Comuns

### 7.1 Tabela de Erros

| Problema | Causa provável | Solução |
|---|---|---|
| "project.godot não encontrado" ao importar | ZIP extraído de forma incorreta ou incompleta | Re-extrair o ZIP; confirmar que `project.godot` está na raiz da pasta |
| Tela completamente preta ao rodar o jogo | Driver de vídeo não suporta Vulkan ou D3D12 | Ver seção 7.2 (Trocar Renderer) |
| Godot não abre no macOS ("app danificado" ou "não pode ser aberto") | Gatekeeper bloqueou o executável | System Settings → Privacy & Security → **Open Anyway** |
| Erro de permissão ao executar no Linux | Arquivo sem flag de execução | `chmod +x Godot_v4.6-stable_linux.x86_64` |
| Assets com ícone de erro no FileSystem | Reimportação incompleta ou interrompida | No editor: **Project → Reimport All** |
| Jogo roda mas está muito lento | Renderer Vulkan/D3D12 sobrecarrega o hardware | Ver seção 7.2 (Trocar Renderer) |
| Janela do jogo não abre, sem mensagem de erro | Resolução ou display problem | **Project → Project Settings → Display → Window** e reduzir a resolução |

### 7.2 Trocar para o Renderer Compatibility (hardware antigo)

O Godot 4.x usa Vulkan ou D3D12 por padrão. Para hardware sem suporte, use o renderer
`Compatibility` (baseado em OpenGL 3.3):

1. No editor, vá em **Project → Project Settings**
2. Na barra de busca, digite `renderer`
3. Em **Rendering → Renderer → Rendering Method**, selecione **`mobile`** ou **`gl_compatibility`**
4. Reinicie o editor quando solicitado

> Alternativamente, inicie a Godot pela linha de comando com a flag:
> ```bash
> ./Godot_v4.6-stable_linux.x86_64 --rendering-driver opengl3
> ```

---

*Manual gerado para o Projeto Gaia — Versão 1.0*
