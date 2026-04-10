import os
import subprocess
from dotenv import load_dotenv
from anthropic import Anthropic

# 1. Fijamos la "casa" del agente (su ruta absoluta)
DIRECTORIO_AGENTE = os.path.dirname(os.path.abspath(__file__))

# 2. Cargamos el .env obligándole a mirar en su casa
load_dotenv(os.path.join(DIRECTORIO_AGENTE, ".env"))
client = Anthropic()

def leer_contexto():
    # 3. Obligamos a que lea el agents.md de su casa
    ruta_agents = os.path.join(DIRECTORIO_AGENTE, "agents.md")
    try:
        with open(ruta_agents, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Eres un asistente de desarrollo."

# --- LAS HERRAMIENTAS REALES (Manos del agente) ---
def ejecutar_git_status():
    return subprocess.run(['git', 'status'], capture_output=True, text=True).stdout

def ejecutar_git_diff():
    # Añadimos HEAD para leer todo, preparado o no
    return subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, encoding='utf-8').stdout

def ejecutar_commit_real(mensaje):
    # 1. Prepara todos los archivos
    subprocess.run(['git', 'add', '.'])
    # 2. Ejecuta el commit con el mensaje que ha pensado la IA
    resultado = subprocess.run(['git', 'commit', '-m', mensaje], capture_output=True, text=True)
    return resultado.stdout

# --- DEFINICIÓN DE HERRAMIENTAS PARA CLAUDE ---
mis_herramientas = [
    {
        "name": "ver_estado",
        "description": "Usa esto primero para ver qué archivos han cambiado.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "ver_codigo",
        "description": "Usa esto para leer las líneas exactas de código que el usuario ha modificado.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "hacer_commit",
        "description": "Usa esto para ejecutar el commit final. Automáticamente hace 'git add .' antes del commit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mensaje": {
                    "type": "string",
                    "description": "El mensaje exacto del commit siguiendo las reglas de Conventional Commits en inglés."
                }
            },
            "required": ["mensaje"]
        }
    }
]

def iniciar_agente_git():
    print("🚀 Iniciando tu Asistente Git Personal...\n")
    reglas = leer_contexto()
    
    # Empezamos dándole la orden inicial
    mensajes = [
        {"role": "user", "content": "Analiza mi repositorio local y haz un commit con los cambios pendientes. Si no hay cambios, dímelo."}
    ]

    pasos = 1
    # EL BUCLE DEL AGENTE
    while True:
        respuesta = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=reglas,
            tools=mis_herramientas,
            messages=mensajes
        )

        if respuesta.stop_reason == "tool_use":
            # 1. Guardamos la petición de Claude (que puede contener varias herramientas)
            mensajes.append({"role": "assistant", "content": respuesta.content})
            
            # 2. Preparamos una lista para meter todos los resultados
            resultados_herramientas = []

            # 3. Procesamos TODAS las herramientas que haya pedido a la vez
            for block in respuesta.content:
                if block.type == "tool_use":
                    print(f"🔄 Paso {pasos} - El agente ejecuta: {block.name}")
                    
                    resultado_texto = ""
                    if block.name == "ver_estado":
                        resultado_texto = ejecutar_git_status()
                    elif block.name == "ver_codigo":
                        resultado_texto = ejecutar_git_diff()
                    elif block.name == "hacer_commit":
                        mensaje_generado = block.input["mensaje"]
                        print(f"✍️  Escribiendo commit: {mensaje_generado}")
                        resultado_texto = ejecutar_commit_real(mensaje_generado)

                    # Metemos el resultado en la lista emparejado con su ID
                    resultados_herramientas.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": resultado_texto
                    })
            
            # 4. Le mandamos de vuelta el paquete con todos los resultados juntos
            mensajes.append({
                "role": "user",
                "content": resultados_herramientas
            })
            pasos += 1
            
        else:
            print("\n=== TRABAJO TERMINADO ===")
            print(respuesta.content[0].text)
            break

if __name__ == "__main__":
    iniciar_agente_git()