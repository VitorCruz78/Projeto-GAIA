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
