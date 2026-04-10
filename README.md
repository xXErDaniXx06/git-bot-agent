# 🤖 Git Bot Agent

![Git Bot](https://img.shields.io/badge/Git-Bot_Agent-blue?style=for-the-badge&logo=github)

Git Bot Agent es un asistente inteligente impulsado por **Claude** que vive en tu entorno local. Su propósito principal es analizar los cambios en tu repositorio (`git status` y `git diff`) y generar **commits de forma automática** siguiendo el estándar de _Conventional Commits_.

> [!NOTE]
> Este agente está diseñado para trabajar localmente de forma autónoma. Revisa los cambios, formula el mensaje en inglés (como dicta la convención) y ejecuta automáticamente el commit y el registro por ti.

---

## 🛠️ Instalación y Configuración

Sigue estos pasos para instalar y ejecutar el agente en cualquier ordenador.

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd git-bot-agent
```

### 2. Entorno Virtual y Dependencias

> [!IMPORTANT]
> Es altamente recomendable usar un entorno virtual para no ensuciar las dependencias globales de tu sistema.

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows
.venv\Scripts\activate
# Activar en macOS / Linux
source .venv/bin/activate

# Instalar los paquetes necesarios
pip install anthropic python-dotenv
```

### 3. Configuración de API Key

El agente necesita acceso a la API de Anthropic (Claude) para razonar sobre tus cambios.

> [!WARNING]
> Nunca subas el archivo `.env` al repositorio. Asegúrate de que este archivo siempre esté en tu `.gitignore`.

1. Crea un archivo llamado `.env` en la raíz del proyecto.
2. Añade tu clave de API:

```env
ANTHROPIC_API_KEY=tu_clave_api_aqui
```

---

## 🚀 Cómo configurar el comando `git bot`

Para invocar a este agente desde **cualquier directorio o terminal** en tu ordenador simplemente escribiendo `git bot`, debes configurar un alias global en Git. 

Git permite nombrar scripts que empiecen por `git-` o utilizar alias. En este caso utilizaremos la configuración de alias nativa de Git pasando una ruta absoluta al script con un prefijo `!`, que indica que ejecutaremos comandos del sistema en lugar de comandos internos de Git.

> [!TIP]
> Antes de lanzar los comandos de configuración, copiate la **ruta absoluta** de la carpeta `git-bot-agent`.

### Opción 1: Si usas el entorno virtual (RECOMENDADA)

Debes apuntar al ejecutable de Python de tu entorno virtual, seguido de la ruta al script `main.py`. Abre tu terminal y reemplaza las rutas por la tuya.

**En terminales de Windows (usando C:/):**
```bash
git config --global alias.bot "!C:/ruta/absoluta/a/git-bot-agent/.venv/Scripts/python.exe C:/ruta/absoluta/a/git-bot-agent/main.py"
```

**En macOS / Linux:**
```bash
git config --global alias.bot "!/ruta/absoluta/a/git-bot-agent/.venv/bin/python /ruta/absoluta/a/git-bot-agent/main.py"
```

### Opción 2: Si instalaste las dependencias globalmente

Si decidiste no usar un entorno virtual y usar el `python` de tu sistema:

```bash
git config --global alias.bot "!python /ruta/absoluta/a/git-bot-agent/main.py"
```

> [!CAUTION]
> Si configuras esto en Windows, asegúrate de mantener las rutas con **barras normales (`/`)**, por ejemplo `C:/Users/danie/...`. Git interpreta las barras inversas (`\`) como caracteres de escape, lo cual hará que el alias falle en Git Bash u otras terminales si no las doblas.

---

## 💻 Uso Básico

Una vez configurado y con cambios pendientes pre-añadidos (o sin añadir) en cualquier proyecto de tu ordenador, abre la terminal en esa carpeta y ejecuta:

```bash
git bot
```

### ¿Qué sucederá en tu terminal?
1. El agente despertará en ese preciso directorio.
2. Inspeccionará el estado de tus archivos (`git status`).
3. Verificará con precisión de cirujano cada línea cambiada (`git diff HEAD`).
4. Si los cambios son válidos, construirá un `Conventional Commit` en inglés e insertará los archivos.
5. Ejecutará el commit final de manera autónoma.

> [!NOTE]
> Puedes alterar el comportamiento, tono y restricciones del asistente editando el archivo `agents.md` incluido en el directorio base del script (`git-bot-agent/agents.md`), ya que el script lee siempre dinámicamente este contexto desde su propia carpeta, no desde donde se ejecuta.
