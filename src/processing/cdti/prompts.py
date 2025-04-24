EXTRACTION_SYSTEM_MESSAGE = "Eres un asistente que extrae información de fichas administrativas en español."

EXTRACTION_HUMAN_MESSAGE = """
A continuación tienes el contenido de una ficha técnica de una subvención en formato Markdown.

Devuelve un objeto JSON con las siguientes claves extraídas del texto:
- "organismo": Entidad que da la subvención. Algunos ejemplos son CDTI, SODERCAN, SPRI, etc.
- "nombre": Título de la ayuda o subvención. Suele ser la primera línea del texto
- "linea": Modalidades de la subvención. Solo la ayuda llamada "proyectos de I+D" tiene 5 lineas de ayudas llamadas modalidades. Devolver una lista de python esas 5 modalidades. Esl resto devolver una lista vacía ("[]").
- "fecha_inicio": Fecha de inicio del plazo para presentar la solicitud, en formato dd/mm/yyyy si es posible. Si es todo el año, devolver el string "Todo el año" en fecha inicio y fecha fin.
- "fecha_fin": Fecha de fin del plazo para presentar la solicitud, en formato dd/mm/yyyy si es posible. Si es todo el año, devolver el string "Todo el año" en fecha inicio y fecha fin.
- "objetivo: Objetivo general de la ayuda o actuación. Si existe el parrafo "Objetivo General de la actuación", devolver ese texto. En caso contrario, se construye un breve párrafo de objetivo de la ayuda a partir del texto Usa verbos en formato sustantivo (Creación en vez de crear, apoyo en vez de apoyar, etc).
- "beneficiarios": Beneficiarios de la ayuda o actuación. Si existe el parrafo "Beneficiarios", devolver ese texto. En caso contrario, se construye una frase breve de beneficiarios a partir del texto.
No expliques nada. Solo responde con un JSON válido.
- "anio": Año de la convocatoria. Si no hace referencia al año, devolver el año actual (2025).
- "area": Clasifica la convocatoria en una de las siguientes areas: [I+D, Innovación, Inversión, Internacional]
- "presupuesto_minimo": Extrae el valor del presupuesto mínimo. Si no existe, devolver "".
- "presupuesto_maximo": Extrae el valor del presupuesto máximo. Si no existe, devolver "".
- "duración_mínima": Extrae la duración mínima de la ayuda en formato string ("<duracion> meses"). Si no existe, devolver "".
- "duración_máxima": Extrae la duración máxima de la ayuda en formato string ("<duracion> meses"). Si aparece una fecha, calcula la duración máxima en meses desde la fecha de inicio de la convocatoria. Si no existe, devolver "".
- "intensidad_del_prestamo": Extrae la información sobre la intensidad del préstamo. Suele ser un porcentaje, y se suele encontrar en el apartado "características de la ayuda". Devuelve el texto asociado, no solo el valor.
- "tipo_financiacion": Extrae el tipo de la ayuda. Suele ser un apartado propio. Si no lo encuentras, devuelve un string vacío.
- "link_ficha_tecnica": Extrae la url del apartado "aid url". Si no existe, devolver un string vacío.
- "link_convocatoria": Extrae la url del apartado "doc url". Si no existe, devolver un string vacío.
Contenido:
--------------------
{document}
--------------------
"""

DYNAMIC_RAG_PROMPT_TEMPLATE = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, say that you don't know.
Always answer in spanish.
Context: {context}
Question: {question}
"""

AID_INTENSITY_PROMPT = "Busca información sobre la intensidad de subvención y devuelve el resultado de forma esquemática. Responde directamente, sin añadir texto introductorio o de finalización explicativos."
PAYMENT_METHOD_PROMPT = "Busca información sobre las formas y plazos de cobro de la subvención y devuelve el resultado de forma esquemática. Responde directamente, sin añadir texto introductorio o de finalización explicativos."
MINIMIS_PROMPT = "Busca si la subvención aparece información sobre disponibilidad de minimis. Responde únicamente 'Si' o 'No'."
APPLICATION_REGION_PROMPT = "Busca si la convocatoria tiene restricciones por zona geográfica. si no las tiene, devuelve únicamente 'No'"
# APPLICATION_REGION_PROMPT = "Busca información sobre la región de aplicación de la subvención, donde tiene que estar localizada geográficamente la empresa candidata, y devuelve el resultado de forma esquemática. Responde directamente, sin añadir texto introductorio o de finalización explicativos."
# APPLICATION_REGION_PROMPT = "Busca información sobre requisitos geofráficos de las empresas candidatas para optar a la subvención y devuelve el resultado de forma esquemática. Responde directamente, sin añadir texto introductorio o de finalización explicativos."
CONSORTIUM_TYPE_PROMPT = "Busca información sobre el tipo de consorcio de la subvención (numero de empresas aceptables o colaboradoras) y devuelve el resultado de forma concisa. Responde directamente, sin añadir texto introductorio o de finalización explicativos."
ELIGIBLE_COSTS_PROMPT = "Busca información sobre los costes elegibles de la subvención y devuelve el resultado de forma esquemática y resumida. Responde directamente, sin añadir texto introductorio o de finalización explicativos."

RAG_PROMPTS = {
    "intensidad_de_subvencion": AID_INTENSITY_PROMPT,
    "forma_y_plazo_de_cobro": PAYMENT_METHOD_PROMPT,
    "minimis": MINIMIS_PROMPT,
    "region_de_aplicacion": APPLICATION_REGION_PROMPT,
    "tipo_de_consorcio": CONSORTIUM_TYPE_PROMPT,
    "costes_elegibles": ELIGIBLE_COSTS_PROMPT
}