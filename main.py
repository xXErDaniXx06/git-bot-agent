import os
import subprocess
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

def leer_contexto():
    try:
        with open("agents.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Eres un asistente."

def obtener_git_status():
    resultado = subprocess.run(['git', 'status'], capture_output=True, text=True)
    return resultado.stdout

# NUEVA FUNCIÓN: La herramienta real que ejecutará el script
def obtener_git_diff():
    resultado = subprocess.run(['git', 'diff'], capture_output=True, text=True)
    return resultado.stdout

def probar_agente():
    print("Iniciando Agente de Desarrollo...\n")
    reglas = leer_contexto()
    estado_git = obtener_git_status()
    
    # 1. Definimos la herramienta (Tool) para que Claude sepa que existe
    mis_herramientas = [
        {
            "name": "obtener_git_diff",
            "description": "Obtiene las diferencias exactas del código (git diff) para ver qué líneas se han modificado. Úsala siempre antes de hacer un commit.",
            "input_schema": {
                "type": "object",
                "properties": {} # No necesita parámetros, solo ejecutarla
            }
        }
    ]

    print("🧠 Agente analizando el status...\n")
    
    # 2. Primera llamada: Le pasamos el status y las herramientas
    respuesta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=reglas,
        tools=mis_herramientas, # AQUÍ LE DAMOS LA CAJA DE HERRAMIENTAS
        messages=[
            {"role": "user", "content": f"Este es mi 'git status':\n{estado_git}\n\nRedacta el comando de git commit."}
        ]
    )
    
    # 3. Comprobamos si Claude ha decidido usar la herramienta
    if respuesta.stop_reason == "tool_use":
        tool_call = next(block for block in respuesta.content if block.type == "tool_use")
        print(f"🛠️  Claude ha decidido usar la herramienta: {tool_call.name}")
        
        # Ejecutamos la función en Python
        if tool_call.name == "obtener_git_diff":
            resultado_diff = obtener_git_diff()
            print("📄 Leyendo tus cambios...\n")
            
            # 4. Segunda llamada: Le devolvemos el resultado del diff a Claude
            respuesta_final = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                system=reglas,
                messages=[
                    {"role": "user", "content": f"Este es mi 'git status':\n{estado_git}\n\nRedacta el comando de git commit."},
                    {"role": "assistant", "content": respuesta.content}, # Le recordamos que él pidió la herramienta
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_call.id,
                                "content": resultado_diff # Aquí le pasamos el código que has modificado
                            }
                        ]
                    }
                ]
            )
            print("=== RESPUESTA FINAL DEL AGENTE ===")
            print(respuesta_final.content[0].text)
    else:
        print(respuesta.content[0].text)

if __name__ == "__main__":
    probar_agente()