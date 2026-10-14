from flask import Flask, render_template, request, abort
import os
import re

app = Flask(__name__)

W = "https://pretecsi.com/wp-content/uploads/"

EMPRESA = {
    "horario": "Lunes a Viernes 7:30 a.m. – 5:30 p.m. | Sábados 8:00 a.m. – 12:00 m.",
    "telefono": "+57 123 4567 891",
    "direccion": "Valledupar, Cesar, Colombia",
    "email": "",
    # Pega aquí los links de tus redes. Las que dejes vacías ("") no se muestran.
    # WhatsApp puede ser solo el número con indicativo, ej: "573001234567"
    "redes": {
        "instagram": "instagram.com",
        "facebook": "facebook.com",
        "tiktok": "tiktok.com",
        "youtube": "youtube.com",
        "whatsapp": "whatsapp.com",
    },
}

LINEAS = [
    {"slug": "arborismo", "nombre": "Arborismo", "img": W + "2026/01/arborismo.webp"},
    {"slug": "proteccion-personal", "nombre": "Protección personal", "img": W + "2026/01/proteccion_personal.webp"},
    {"slug": "rescate-y-emergencias", "nombre": "Rescate y emergencias", "img": W + "2026/01/rescateyemergencias.webp"},
    {"slug": "sistemas-de-ingenieria", "nombre": "Sistemas de ingeniería", "img": W + "2026/01/sistemas_ingenieria.webp"},
    {"slug": "trabajo-en-altura", "nombre": "Trabajo en alturas", "img": W + "2026/01/trabajo_altura.webp"},
]

CATS = [
    {"slug": "accesorios", "nombre": "Accesorios"},
    {"slug": "arnes", "nombre": "Arneses"},
    {"slug": "ascendedores", "nombre": "Ascendedores"},
    {"slug": "autoretractiles", "nombre": "Dispositivos autorretráctiles"},
    {"slug": "bloqueadores-y-arrestadores", "nombre": "Bloqueadores y arrestadores"},
    {"slug": "cascos-e-iluminacion", "nombre": "Cascos e iluminación"},
    {"slug": "conectores", "nombre": "Conectores"},
    {"slug": "cuerdas-y-cordinos", "nombre": "Cuerdas y cordinos"},
    {"slug": "descensores", "nombre": "Descensores"},
    {"slug": "eslingas", "nombre": "Eslingas"},
    {"slug": "kits-de-rescate", "nombre": "Kits de rescate"},
    {"slug": "lineas-de-vida", "nombre": "Líneas de vida"},
    {"slug": "poleas", "nombre": "Poleas"},
    {"slug": "proteccion-auditiva", "nombre": "Protección auditiva"},
    {"slug": "proteccion-corporal", "nombre": "Protección corporal"},
    {"slug": "proteccion-facial", "nombre": "Protección facial"},
    {"slug": "proteccion-manual", "nombre": "Protección manual"},
    {"slug": "proteccion-respiratoria", "nombre": "Protección respiratoria"},
    {"slug": "proteccion-visual", "nombre": "Protección visual"},
]

SERVICIOS = [
    {"slug": "inspeccion-de-equipos", "nombre": "Inspección de equipos", "img": W + "2026/03/luz.webp", "resumen": "Revisión del estado visible de los equipos y orientación para consultar al fabricante o a personal competente.", "lista": ["Identificación del equipo", "Revisión visual de componentes", "Registro de observaciones", "Orientación sobre próximos pasos"]},
    {"slug": "puntos-de-anclaje", "nombre": "Puntos de anclaje", "img": W + "2026/03/casco.webp", "resumen": "Orientación inicial para identificar necesidades de anclaje y solicitar una evaluación técnica del lugar.", "lista": ["Revisión de necesidades del proyecto", "Información sobre soluciones posibles", "Recomendación de evaluación técnica", "Consulta de documentación disponible"]},
    {"slug": "lineas-de-vida", "nombre": "Líneas de vida", "img": "https://pretecsi.com/wp-content/uploads/2026/04/LINEA-DE-VIDA.avif", "resumen": "Información sobre sistemas de protección contra caídas para proyectos que requieren evaluación y diseño especializado.", "lista": ["Líneas de vida horizontales y verticales", "Consulta de condiciones de instalación", "Revisión de requisitos del proyecto", "Solicitud de asesoría técnica"]},
]

RECURSOS = [
    {"slug": "catalogos", "nombre": "Catálogos", "resumen": "Consulta información de productos y solicita el catálogo actualizado."},
    {"slug": "certificados", "nombre": "Certificados", "resumen": "Solicita fichas técnicas, certificados y documentación del fabricante para el modelo de tu interés."},
    {"slug": "videos", "nombre": "Videos", "resumen": "Material audiovisual sobre equipos, componentes y buenas prácticas de uso."},
    {"slug": "normativa", "nombre": "Normativa", "resumen": "Información general para identificar normas y requisitos aplicables. Confirma siempre la regulación vigente con una fuente oficial."},
    {"slug": "blog", "nombre": "Blog", "resumen": "Artículos informativos sobre trabajo en alturas, selección de equipos y cuidado del material."},
]

# Los productos no tienen precios ni certificaciones inventadas. Solicita la ficha
# técnica y la disponibilidad del modelo antes de comprar o utilizar un equipo.
_PRODUCTOS_BASE = [
    ("ascendedor-de-pecho-yoke", "Ascendedor de pecho Yoke", "ascendedores", ["arborismo", "trabajo-en-altura"], "Ascendedor para sistemas compatibles de progresión por cuerda. Verifica el diámetro admitido y las instrucciones del fabricante.", W + "2026/08/ascendedor-pecho-para-cuerda-de-8-13-mm-n-5306-yoke.jpg", ["Uso según ficha técnica", "Compatibilidad por confirmar"]),
    ("ascendedor-cam-clean", "Ascendedor de pecho Cam Clean", "ascendedores", ["arborismo", "trabajo-en-altura"], "Dispositivo ascendedor para aplicaciones compatibles de acceso por cuerda.", "", ["Consulta compatibilidad", "Solicita ficha técnica"]),
    ("jag-rescue-60", "Kit de rescate JAG 60 m", "kits-de-rescate", ["rescate-y-emergencias", "trabajo-en-altura"], "Kit de rescate para configuraciones compatibles. Confirma componentes y longitud del modelo disponible.", "", ["Longitud indicada en el nombre", "Componentes por confirmar"]),
    ("jag-rescue-30", "Kit de rescate JAG 30 m", "kits-de-rescate", ["rescate-y-emergencias", "trabajo-en-altura"], "Kit de rescate para maniobras previstas por el fabricante y personal competente.", "", ["Longitud indicada en el nombre", "Solicita la documentación"]),
    ("kit-rescate-40", "Kit de rescate Dinamik 40 m", "kits-de-rescate", ["rescate-y-emergencias"], "Kit para escenarios de rescate específicos. Verifica el contenido exacto antes de cotizar.", "", ["Configuración por confirmar", "Ficha técnica bajo solicitud"]),
    ("kit-rescate-30", "Kit de rescate Dinamik 30 m", "kits-de-rescate", ["rescate-y-emergencias"], "Conjunto de rescate cuya selección debe corresponder al procedimiento previsto.", "", ["Configuración por confirmar", "Consulta disponibilidad"]),
    ("kit-rescate-20", "Kit de rescate Dinamik 20 m", "kits-de-rescate", ["rescate-y-emergencias"], "Kit de rescate para aplicaciones compatibles con sus especificaciones.", "", ["Longitud indicada en el nombre", "Consulta documentación"]),
    ("kit-rescate-10", "Kit de rescate Dinamik 10 m", "kits-de-rescate", ["rescate-y-emergencias"], "Kit de rescate para aplicaciones compatibles. La configuración debe ser revisada por personal competente.", "", ["Longitud indicada en el nombre", "Consulta disponibilidad"]),
    ("descensor-antipanico-sir", "Descensor con antipánico SIR", "descensores", ["trabajo-en-altura", "rescate-y-emergencias"], "Descensor con función antipánico para aplicaciones indicadas por el fabricante.", "", ["Consulta cuerda compatible", "Revisa instrucciones de uso"]),
    ("accesorio-cuerda", "Accesorios para cuerda", "accesorios", ["arborismo", "trabajo-en-altura"], "Complementos para organizar y utilizar sistemas de trabajo con cuerda. Consulta compatibilidad y disponibilidad.", "", ["Modelos por consultar", "Compatibilidad por confirmar"]),
    ("mochila-equipo", "Mochila para equipo vertical", "accesorios", ["arborismo", "trabajo-en-altura"], "Mochila para transportar y organizar equipos de trabajo vertical.", "", ["Capacidad por confirmar", "Consulta disponibilidad"]),
    ("bolsa-cuerda", "Bolsa para cuerda", "accesorios", ["arborismo", "trabajo-en-altura"], "Bolsa para facilitar el transporte y almacenamiento de cuerdas.", "", ["Tamaño por confirmar", "Consulta modelos disponibles"]),
    ("arnes-multiproposito", "Arnés multipropósito", "arnes", ["trabajo-en-altura"], "Arnés para labores en altura. Consulta tallas, puntos de conexión y documentación técnica del modelo disponible.", "", ["Tallas por confirmar", "Ficha técnica bajo solicitud"]),
    ("arnes-arborismo", "Arnés para arborismo", "arnes", ["arborismo"], "Arnés destinado a actividades de arborismo. Selecciona el modelo según la labor y las instrucciones del fabricante.", "", ["Modelos por consultar", "Consulta compatibilidad"]),
    ("ascendedor-mano", "Ascendedor de mano", "ascendedores", ["arborismo", "trabajo-en-altura"], "Dispositivo para progresión por cuerda en aplicaciones compatibles.", "", ["Mano izquierda o derecha según modelo", "Consulta diámetro compatible"]),
    ("retractil-anticaidas", "Dispositivo retráctil anticaídas", "autoretractiles", ["trabajo-en-altura"], "Dispositivo retráctil para protección contra caídas. Longitud, uso y compatibilidad dependen del modelo.", "", ["Longitud por confirmar", "Solicita ficha técnica"]),
    ("bloqueador-cuerda", "Bloqueador para cuerda", "bloqueadores-y-arrestadores", ["arborismo", "trabajo-en-altura"], "Dispositivo de bloqueo para aplicaciones específicas de cuerda. Verifica el diámetro admitido por el fabricante.", "", ["Modelo por consultar", "Uso según instrucciones"]),
    ("casco-altura", "Casco para trabajo en alturas", "cascos-e-iluminacion", ["trabajo-en-altura"], "Casco para trabajos verticales. Consulta sistema de ajuste, compatibilidad con accesorios y certificaciones.", "", ["Talla y color por confirmar", "Certificaciones según modelo"]),
    ("casco-arborismo", "Casco para arborismo", "cascos-e-iluminacion", ["arborismo"], "Protección de cabeza para actividades de arborismo. Verifica los requisitos de la tarea antes de elegir.", "", ["Modelos por consultar", "Accesorios por confirmar"]),
    ("conector-acero", "Conector de acero", "conectores", ["trabajo-en-altura"], "Conector para sistemas compatibles de protección contra caídas. La capacidad y el uso dependen del modelo.", "", ["Tipo de cierre por confirmar", "Consulta ficha técnica"]),
    ("mosqueton-seguridad", "Mosquetón de seguridad", "conectores", ["arborismo", "trabajo-en-altura"], "Mosquetón para aplicaciones compatibles de trabajo vertical. Consulta tipo de cierre, resistencia y ficha técnica.", "", ["Forma y cierre por confirmar", "Uso según fabricante"]),
    ("cuerda-semiestatica", "Cuerda semiestática", "cuerdas-y-cordinos", ["trabajo-en-altura", "rescate-y-emergencias"], "Cuerda para aplicaciones compatibles de acceso por cuerda y rescate. Diámetro y longitud por confirmar.", "", ["Diámetro por consultar", "Longitud por consultar"]),
    ("cuerda-arborismo", "Cuerda para arborismo", "cuerdas-y-cordinos", ["arborismo"], "Cuerda para actividades de arborismo. La compatibilidad debe verificarse con los equipos utilizados.", "", ["Modelos por consultar", "Solicita ficha técnica"]),
    ("cordino-auxiliar", "Cordino auxiliar", "cuerdas-y-cordinos", ["arborismo", "trabajo-en-altura"], "Cordino para aplicaciones específicas compatibles con sus características técnicas.", "", ["Diámetro por confirmar", "Longitud por consultar"]),
    ("descensor-ocho", "Descensor tipo ocho", "descensores", ["rescate-y-emergencias", "trabajo-en-altura"], "Dispositivo de descenso para aplicaciones compatibles. Consulta instrucciones, limitaciones y ficha del fabricante.", "", ["Material por confirmar", "Compatibilidad por verificar"]),
    ("descensor-acceso-cuerda", "Descensor para acceso por cuerda", "descensores", ["trabajo-en-altura"], "Dispositivo para maniobras de descenso con cuerda. El modelo y su uso deben seleccionarse según la tarea.", "", ["Modelo por consultar", "Consulta ficha técnica"]),
    ("eslinga-posicionamiento", "Eslinga de posicionamiento", "eslingas", ["trabajo-en-altura"], "Elemento para posicionamiento laboral cuando forma parte de un sistema compatible y correctamente seleccionado.", "", ["Longitud por confirmar", "Consulta indicaciones del fabricante"]),
    ("eslinga-absorbedor", "Eslinga con absorbedor de energía", "eslingas", ["trabajo-en-altura"], "Elemento de conexión con absorbedor para sistemas compatibles de detención de caídas.", "", ["Configuración por confirmar", "Solicita ficha técnica"]),
    ("linea-vida", "Sistema de línea de vida", "lineas-de-vida", ["trabajo-en-altura", "sistemas-de-ingenieria"], "Solución de protección contra caídas cuya selección, instalación y verificación requieren evaluación técnica.", "", ["Evaluación del lugar requerida", "Configuración según proyecto"]),
    ("polea-simple", "Polea simple", "poleas", ["arborismo", "rescate-y-emergencias"], "Polea para maniobras compatibles de cuerda y sistemas de rescate. Consulta carga de trabajo y ficha técnica.", "", ["Modelo por consultar", "Carga según ficha técnica"]),
    ("polea-doble", "Polea doble", "poleas", ["rescate-y-emergencias"], "Polea doble para sistemas compatibles de izado y rescate. La configuración debe seguir las indicaciones técnicas.", "", ["Modelo por consultar", "Uso según fabricante"]),
    ("guantes-proteccion", "Guantes de protección", "proteccion-manual", ["proteccion-personal"], "Guantes para tareas laborales. El material y nivel de protección deben corresponder al riesgo específico.", "", ["Tallas por confirmar", "Nivel de protección por modelo"]),
    ("proteccion-auditiva", "Protección auditiva", "proteccion-auditiva", ["proteccion-personal"], "Elemento de protección auditiva para ambientes con exposición al ruido. Selecciona según la evaluación del riesgo.", "", ["Tipo por consultar", "Características según modelo"]),
    ("proteccion-facial", "Protección facial", "proteccion-facial", ["proteccion-personal"], "Equipo de protección facial para riesgos compatibles con sus características y especificaciones.", "", ["Tipo por consultar", "Compatibilidad por confirmar"]),
    ("proteccion-respiratoria", "Protección respiratoria", "proteccion-respiratoria", ["proteccion-personal"], "Equipo de protección respiratoria. El filtro y el tipo de equipo deben seleccionarse según el contaminante y la evaluación del riesgo.", "", ["Tipo y filtro por consultar", "Consulta ficha técnica"]),
    ("proteccion-visual", "Protección visual", "proteccion-visual", ["proteccion-personal"], "Gafas u otros elementos de protección ocular según la tarea y los riesgos presentes.", "", ["Modelos por consultar", "Protección según ficha técnica"]),
    ("proteccion-corporal", "Protección corporal", "proteccion-corporal", ["proteccion-personal"], "Elementos de protección corporal para riesgos laborales específicos. Consulta materiales y características disponibles.", "", ["Tipo por consultar", "Tallas según modelo"]),
    ('accesorio-herramientas', 'Accesorios para herramientas', 'accesorios', ['arborismo', 'trabajo-en-altura'], 'Accesorios para organizar y asegurar herramientas durante labores verticales. Consulta los modelos compatibles.'),
    ('arnes-singing-rock-technic', 'Arnés Singing Rock Technic Standard', 'arnes', ['trabajo-en-altura', 'rescate-y-emergencias'], 'Arnés para acceso por cuerda, posicionamiento y detención de caídas. Solicita la ficha técnica del modelo.'),
    ('arnes-rescate', 'Arnés para rescate', 'arnes', ['rescate-y-emergencias', 'trabajo-en-altura'], 'Arnés para aplicaciones de rescate según el modelo disponible y el procedimiento previsto.'),
    ('arnes-confort', 'Arnés de cuerpo completo con acolchado', 'arnes', ['trabajo-en-altura'], 'Arnés de cuerpo completo. Consulta tallas, puntos de conexión y documentación del fabricante.'),
    ('ascendedor-pie', 'Ascendedor de pie', 'ascendedores', ['arborismo', 'trabajo-en-altura'], 'Dispositivo auxiliar de ascenso por cuerda; verifica compatibilidad y configuración autorizada.'),
    ('retractil-cable', 'Retráctil anticaídas con cable', 'autoretractiles', ['trabajo-en-altura', 'sistemas-de-ingenieria'], 'Equipo retráctil para aplicaciones compatibles. Longitud, uso y requisitos de anclaje dependen de la referencia.'),
    ('retractil-cinta', 'Retráctil anticaídas con cinta', 'autoretractiles', ['trabajo-en-altura'], 'Dispositivo retráctil con cinta. Consulta longitud, conectores, limitaciones y ficha técnica.'),
    ('retractil-rescate', 'Retráctil con función de rescate', 'autoretractiles', ['rescate-y-emergencias', 'trabajo-en-altura'], 'Equipo para aplicaciones específicas de detención de caídas y rescate según modelo.'),
    ('arrestador-cuerda', 'Arrestador para cuerda', 'bloqueadores-y-arrestadores', ['trabajo-en-altura', 'rescate-y-emergencias'], 'Dispositivo anticaídas para cuerda compatible. Revisa diámetro, dirección de uso y documentación.'),
    ('bloqueador-mecanico', 'Bloqueador mecánico de cuerda', 'bloqueadores-y-arrestadores', ['arborismo', 'trabajo-en-altura'], 'Bloqueador para progresión o maniobras específicas con cuerda, según instrucciones del fabricante.'),
    ('bloqueador-pecho', 'Bloqueador de pecho', 'bloqueadores-y-arrestadores', ['arborismo', 'trabajo-en-altura'], 'Bloqueador de pecho para configuraciones compatibles de ascenso por cuerda.'),
    ('casco-vertex', 'Casco tipo Vertex para altura', 'cascos-e-iluminacion', ['trabajo-en-altura', 'rescate-y-emergencias'], 'Casco para trabajo en alturas. Verifica referencia, ajuste, accesorios y documentación del fabricante.'),
    ('casco-ventilado', 'Casco ventilado para trabajo vertical', 'cascos-e-iluminacion', ['arborismo', 'trabajo-en-altura'], 'Casco ventilado para aplicaciones compatibles. La idoneidad depende del entorno y del modelo.'),
    ('lampara-casco', 'Iluminación para casco', 'cascos-e-iluminacion', ['rescate-y-emergencias', 'arborismo'], 'Accesorio de iluminación compatible con determinados cascos. Consulta montaje y características.'),
    ('conector-ovalado', 'Conector ovalado', 'conectores', ['rescate-y-emergencias', 'trabajo-en-altura'], 'Conector para equipos y sistemas compatibles. Consulta material, cierre y capacidad de la referencia.'),
    ('conector-triple-cierre', 'Conector con cierre de seguridad', 'conectores', ['trabajo-en-altura', 'arborismo'], 'Conector con mecanismo de cierre de seguridad. Selecciona el modelo según la conexión prevista.'),
    ('conector-anclaje', 'Conector para punto de anclaje', 'conectores', ['sistemas-de-ingenieria', 'trabajo-en-altura'], 'Conector para sistemas de anclaje compatibles. Revisa las instrucciones del sistema completo.'),
    ('cuerda-11mm', 'Cuerda semiestática de 11 mm', 'cuerdas-y-cordinos', ['trabajo-en-altura', 'rescate-y-emergencias'], 'Cuerda para usos compatibles según su ficha técnica. Longitudes, terminaciones y disponibilidad por confirmar.'),
    ('cuerda-dinamica', 'Cuerda dinámica', 'cuerdas-y-cordinos', ['arborismo'], 'Cuerda para aplicaciones compatibles con cuerdas dinámicas. Confirma uso previsto y ficha del fabricante.'),
    ('cordino-prusik', 'Cordino para nudos auxiliares', 'cuerdas-y-cordinos', ['arborismo', 'rescate-y-emergencias'], 'Cordino para maniobras auxiliares previstas por el fabricante y personal competente.'),
    ('descensor-id', 'Descensor autofrenante para cuerda', 'descensores', ['trabajo-en-altura', 'rescate-y-emergencias'], 'Descensor para aplicaciones compatibles de acceso por cuerda. Verifica el modelo y la cuerda admitida.'),
    ('descensor-rescate', 'Descensor para rescate', 'descensores', ['rescate-y-emergencias'], 'Dispositivo para descenso en operaciones de rescate de acuerdo con la documentación del fabricante.'),
    ('eslinga-doble', 'Eslinga doble de conexión', 'eslingas', ['trabajo-en-altura'], 'Elemento de conexión doble para sistemas compatibles. Consulta conectores, longitud y ficha técnica.'),
    ('eslinga-anclaje', 'Eslinga de anclaje', 'eslingas', ['sistemas-de-ingenieria', 'trabajo-en-altura'], 'Elemento de anclaje para configuraciones autorizadas. Verifica material, capacidad y uso permitido.'),
    ('eslinga-posicionamiento-ajustable', 'Eslinga ajustable de posicionamiento', 'eslingas', ['trabajo-en-altura', 'arborismo'], 'Elemento ajustable para posicionamiento en aplicaciones compatibles según las instrucciones del fabricante.'),
    ('linea-vida-horizontal', 'Línea de vida horizontal', 'lineas-de-vida', ['sistemas-de-ingenieria', 'trabajo-en-altura'], 'Sistema horizontal que requiere diseño, instalación y revisión por personal competente según el proyecto.'),
    ('linea-vida-vertical', 'Sistema de línea de vida vertical', 'lineas-de-vida', ['sistemas-de-ingenieria', 'trabajo-en-altura'], 'Sistema vertical de protección contra caídas. La compatibilidad depende de la estructura y componentes.'),
    ('anclaje-estructural', 'Punto de anclaje estructural', 'lineas-de-vida', ['sistemas-de-ingenieria', 'trabajo-en-altura'], 'Solución de anclaje que requiere evaluación técnica de la estructura y de las condiciones del proyecto.'),
    ('polea-rescate', 'Polea para sistemas de rescate', 'poleas', ['rescate-y-emergencias', 'sistemas-de-ingenieria'], 'Polea para configuraciones compatibles de izado y rescate. Consulta carga y diámetro de cuerda permitidos.'),
    ('polea-arborismo', 'Polea para arborismo', 'poleas', ['arborismo'], 'Polea para aplicaciones compatibles de arborismo. Verifica uso, cuerda y ficha del modelo.'),
    ('guantes-cordex', 'Guantes para trabajo con cuerda', 'proteccion-manual', ['arborismo', 'trabajo-en-altura'], 'Guantes para tareas con cuerda. Consulta material, tallas y nivel de protección del modelo.'),
    ('guantes-industriales', 'Guantes de protección industrial', 'proteccion-manual', ['proteccion-personal'], 'Guantes para riesgos laborales específicos. Selecciona según evaluación del riesgo y ficha técnica.'),
    ('guantes-agarre', 'Guantes con palma reforzada', 'proteccion-manual', ['proteccion-personal', 'trabajo-en-altura'], 'Guantes con refuerzo para tareas compatibles. Consulta disponibilidad y características del modelo.'),
    ('tapones-auditivos', 'Tapones de protección auditiva', 'proteccion-auditiva', ['proteccion-personal'], 'Protección auditiva para ambientes con ruido. Verifica atenuación y adecuación al riesgo.'),
    ('orejeras-auditivas', 'Orejeras de protección auditiva', 'proteccion-auditiva', ['proteccion-personal'], 'Protección auditiva tipo orejera. Consulta nivel de atenuación y compatibilidad con otros EPP.'),
    ('proteccion-facial-visera', 'Visera de protección facial', 'proteccion-facial', ['proteccion-personal'], 'Visera para riesgos compatibles. Verifica el tipo de impacto o exposición que puede soportar.'),
    ('careta-proteccion', 'Careta de protección industrial', 'proteccion-facial', ['proteccion-personal'], 'Careta de protección para tareas específicas. Consulta la ficha del fabricante antes de seleccionar.'),
    ('respirador-media-cara', 'Respirador de media cara', 'proteccion-respiratoria', ['proteccion-personal'], 'Respirador reutilizable para filtros compatibles. El filtro depende del contaminante y de la evaluación del riesgo.'),
    ('mascarilla-desechable', 'Mascarilla de protección respiratoria', 'proteccion-respiratoria', ['proteccion-personal'], 'Elemento respiratorio para aplicaciones compatibles. Confirma tipo, ajuste y certificación del producto.'),
    ('gafas-seguridad', 'Gafas de seguridad', 'proteccion-visual', ['proteccion-personal'], 'Protección ocular para riesgos compatibles con la especificación del modelo.'),
    ('gafas-antimpacto', 'Gafas de protección contra impactos', 'proteccion-visual', ['proteccion-personal'], 'Gafas de seguridad para aplicaciones indicadas por el fabricante. Consulta características y ajuste.'),
    ('ropa-alta-visibilidad', 'Prenda de alta visibilidad', 'proteccion-corporal', ['proteccion-personal', 'trabajo-en-altura'], 'Prenda para mejorar la visibilidad del trabajador. Consulta talla y características disponibles.'),
    ('overol-proteccion', 'Ropa de protección laboral', 'proteccion-corporal', ['proteccion-personal'], 'Prenda de protección para riesgos específicos. La selección depende del entorno y la ficha técnica.'),
    ('tripo-rescate', 'Trípode para espacios confinados', 'accesorios', ['rescate-y-emergencias', 'sistemas-de-ingenieria'], 'Equipo de acceso y rescate que requiere selección, montaje y uso según la documentación del fabricante.'),
    ('anclaje-temporal', 'Sistema de anclaje temporal', 'accesorios', ['sistemas-de-ingenieria', 'trabajo-en-altura'], 'Sistema temporal de anclaje para configuraciones compatibles. Verifica requisitos del lugar y del fabricante.'),
    ('kit-rescate-confined', 'Kit de rescate para espacios confinados', 'kits-de-rescate', ['rescate-y-emergencias', 'sistemas-de-ingenieria'], 'Kit configurable para escenarios de rescate. Componentes y compatibilidad se confirman con la ficha del conjunto.'),

]


IMG_CATEGORIA = {
    "accesorios": W + "2026/01/arborismo.webp",
    "arnes": W + "2026/03/casco.webp",
    "ascendedores": W + "2026/01/arborismo.webp",
    "autoretractiles": W + "2026/01/trabajo_altura.webp",
    "bloqueadores-y-arrestadores": W + "2026/01/trabajo_altura.webp",
    "cascos-e-iluminacion": W + "2026/03/casco.webp",
    "conectores": W + "2026/01/trabajo_altura.webp",
    "cuerdas-y-cordinos": W + "2026/01/arborismo.webp",
    "descensores": W + "2026/01/rescateyemergencias.webp",
    "eslingas": W + "2026/01/trabajo_altura.webp",
    "kits-de-rescate": W + "2026/01/rescateyemergencias.webp",
    "lineas-de-vida": W + "2026/03/buid.webp",
    "poleas": W + "2026/01/rescateyemergencias.webp",
    "proteccion-auditiva": W + "2026/01/proteccion_personal.webp",
    "proteccion-corporal": W + "2026/01/proteccion_personal.webp",
    "proteccion-facial": W + "2026/01/proteccion_personal.webp",
    "proteccion-manual": W + "2026/01/proteccion_personal.webp",
    "proteccion-respiratoria": W + "2026/01/proteccion_personal.webp",
    "proteccion-visual": W + "2026/01/proteccion_personal.webp",
}

CAT = {c["slug"]: c for c in CATS}
LIN = {l["slug"]: l for l in LINEAS}
SRV = {s["slug"]: s for s in SERVICIOS}
REC = {r["slug"]: r for r in RECURSOS}


# Grupos principales del menú y del catálogo (según el brief).
GRUPOS = [
    {"slug": "arneses", "nombre": "Arneses", "cats": ["arnes"]},
    {"slug": "cuerdas", "nombre": "Cuerdas", "cats": ["cuerdas-y-cordinos"]},
    {"slug": "cascos", "nombre": "Cascos", "cats": ["cascos-e-iluminacion"]},
    {"slug": "equipos-verticales", "nombre": "Equipos verticales", "cats": [
        "ascendedores", "autoretractiles", "bloqueadores-y-arrestadores", "conectores",
        "descensores", "eslingas", "kits-de-rescate", "lineas-de-vida", "poleas"]},
    {"slug": "accesorios", "nombre": "Accesorios", "cats": ["accesorios"]},
    {"slug": "proteccion-personal", "nombre": "Protección personal", "cats": [
        "proteccion-auditiva", "proteccion-corporal", "proteccion-facial",
        "proteccion-manual", "proteccion-respiratoria", "proteccion-visual"]},
]
GRP = {g["slug"]: g for g in GRUPOS}
GRUPO_DE = {c: g["slug"] for g in GRUPOS for c in g["cats"]}


# ---------------------------------------------------------------------------
# Imágenes de producto (propias, sin depender de otras webs)
# Cada producto tiene hasta 3 vistas en static/img/productos/:
#     <id>.svg  <id>-2.svg  <id>-3.svg
# Para usar FOTOS REALES: copia tus archivos con el mismo nombre y extensión
# .jpg, .jpeg, .png o .webp (ej. casco-altura.jpg, casco-altura-2.jpg ...).
# Si existe la foto, se usa en lugar de la ilustración.
# ---------------------------------------------------------------------------
_DIR_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img", "productos")


# Imágenes cargadas desde el servidor de Pretecsi (hotlink).
# Pega aquí las URLs de cada producto: clic derecho sobre la foto > "Copiar dirección de la imagen".
#   "id-del-producto": ["https://pretecsi.com/.../foto1.jpg", "https://pretecsi.com/.../foto2.jpg"],
# Si una URL falla o la web la bloquea, se muestra automáticamente la ilustración propia.
USAR_IMAGENES_PRETECSI = True
IMAGENES_PRETECSI = {
    "linea-vida": ["https://pretecsi.com/wp-content/uploads/2026/04/LINEA-DE-VIDA.avif"],
    "ascendedor-de-pecho-yoke": ["https://pretecsi.com/wp-content/uploads/2026/08/ascendedor-pecho-para-cuerda-de-8-13-mm-n-5306-yoke-630x630.jpg"],
    "ascendedor-cam-clean": ["https://pretecsi.com/wp-content/uploads/2026/08/RK805BX00.jpg"],
    "jag-rescue-60": ["https://pretecsi.com/wp-content/uploads/2026/07/K090AA00-JAG-RESCUE-KIT-30M-view-2-22_LowRes-602x630.jpeg"],
    "jag-rescue-30": ["https://pretecsi.com/wp-content/uploads/2026/07/K090AA00-JAG-RESCUE-KIT-30M-view-2-22_LowRes-602x630.jpeg"],
    "kit-rescate-40": ["https://pretecsi.com/wp-content/uploads/2026/07/0d4d8f19-eec5-4d28-90b7-7ddc623d2b84-630x630.jpg"],
    "kit-rescate-30": ["https://pretecsi.com/wp-content/uploads/2026/07/0d4d8f19-eec5-4d28-90b7-7ddc623d2b84-630x630.jpg"],
    "kit-rescate-20": ["https://pretecsi.com/wp-content/uploads/2026/07/0d4d8f19-eec5-4d28-90b7-7ddc623d2b84-630x630.jpg"],
    "kit-rescate-10": ["https://pretecsi.com/wp-content/uploads/2026/07/0d4d8f19-eec5-4d28-90b7-7ddc623d2b84-630x630.jpg"],
    "descensor-antipanico-sir": ["https://pretecsi.com/wp-content/uploads/2026/07/K032SIR00-2.jpg"],
    "descensor-ocho": ["https://pretecsi.com/wp-content/uploads/2026/04/Ocho-de-Rescate-EQgrip-ALU8-web-1-tiny-630x630.jpg"],
    "descensor-id": ["https://pretecsi.com/wp-content/uploads/2026/07/Captura-de-pantalla-2026-07-15-124846.jpg"],
    "descensor-acceso-cuerda": ["https://pretecsi.com/wp-content/uploads/2026/07/Captura-de-pantalla-2026-07-15-132852.jpg"],
    "descensor-rescate": ["https://pretecsi.com/wp-content/uploads/2026/07/Captura-de-pantalla-2026-07-15-125449.jpg"],
    "polea-simple": ["https://pretecsi.com/wp-content/uploads/2026/01/2128-630x630.jpg"],
    "polea-doble": ["https://pretecsi.com/wp-content/uploads/2026/01/2127-630x630.jpg"],
    "polea-arborismo": ["https://pretecsi.com/wp-content/uploads/2026/02/RK806BB00.jpg"],
    "polea-rescate": ["https://pretecsi.com/wp-content/uploads/2025/10/POLEA-RESCUE-630x630.png"],
    "arnes-arborismo": ["https://pretecsi.com/wp-content/uploads/2026/02/W0105BR.jpg"],
    "arnes-multiproposito": ["https://pretecsi.com/wp-content/uploads/2026/04/arnes-de-seguridad-linktech-LT4c-630x630.webp"],
    "arnes-rescate": ["https://pretecsi.com/wp-content/uploads/2026/04/5-ARGOL.avif"],
}


def imagenes_producto(pid, remota=""):
    locales = []
    for sufijo in ("", "-2", "-3"):
        for ext in ("jpg", "jpeg", "png", "webp", "svg"):
            archivo = f"{pid}{sufijo}.{ext}"
            if os.path.exists(os.path.join(_DIR_IMG, archivo)):
                locales.append("/static/img/productos/" + archivo)
                break
    locales = locales or [W + "2026/01/trabajo_altura.webp"]
    remotas = []
    if USAR_IMAGENES_PRETECSI:
        remotas = list(IMAGENES_PRETECSI.get(pid, []))
        if remota and remota.startswith("http") and remota not in remotas:
            remotas.insert(0, remota)
    return remotas + locales, locales[0]


PRODUCTOS = []
_IDS_PRODUCTOS = set()

for i, producto in enumerate(_PRODUCTOS_BASE, start=1):
    if len(producto) == 7:
        pid, nombre, cat, lin, desc, img, lista = producto
    elif len(producto) == 5:
        pid, nombre, cat, lin, desc = producto
        img = ""
        lista = [
            "Consulta las características del modelo disponible.",
            "Solicita la ficha técnica y confirma la disponibilidad.",
        ]
    else:
        raise ValueError(
            f"El producto número {i} contiene {len(producto)} campos; "
            "se esperaban 5 o 7."
        )

    if pid in _IDS_PRODUCTOS:
        raise ValueError(f"El identificador de producto está repetido: {pid}")
    _IDS_PRODUCTOS.add(pid)

    if cat not in CAT:
        raise ValueError(f"El producto '{pid}' usa una categoría inexistente: {cat}")

    if not isinstance(lin, list):
        lin = list(lin) if lin else []

    imgs, respaldo = imagenes_producto(pid, img)
    imagen = imgs[0]

    PRODUCTOS.append({
        "id": pid,
        "nombre": nombre,
        "cat": cat,
        "grupo": GRUPO_DE.get(cat, ""),
        "lin": lin,
        "desc": desc,
        "img": imagen,
        "imgs": imgs,
        "fb": respaldo,
        "lista": lista or [],
        "ficha": None,
        "precio": None,
        "ok": True,
        "dest": False,
    })

# Destacados del inicio: un producto de cada categoría principal (más variedad)
_ORDEN_DEST = ["arnes", "cascos-e-iluminacion", "cuerdas-y-cordinos", "descensores",
               "conectores", "poleas", "ascendedores", "eslingas"]
for _slug in _ORDEN_DEST:
    _p = next((p for p in PRODUCTOS if p["cat"] == _slug), None)
    if _p:
        _p["dest"] = True

for _c in CATS:
    _ps = [p for p in PRODUCTOS if p["cat"] == _c["slug"]]
    # Prefiere un producto con foto real (jpg/png/webp); si no hay, usa el primero.
    _p = next((p for p in _ps if not p["img"].lower().split("?")[0].endswith(".svg")), None) or (_ps[0] if _ps else None)
    _c["img"] = _p["img"] if _p else ""

HERO = [
    {"tag": "SEGURIDAD Y CONFIANZA", "t": "Protegemos tu trabajo en altura", "p": "Equipos y soluciones para trabajo vertical, arborismo y protección personal.", "cta": "Explorar productos", "href": "productos", "img": W + "2026/01/trabajo_altura.webp"},
    {"tag": "EQUIPOS PARA CADA RETO", "t": "El equipo adecuado empieza con una buena elección", "p": "Consulta las características técnicas y solicita orientación para tu proyecto.", "cta": "Contáctanos", "href": "contacto", "img": W + "2026/01/rescateyemergencias.webp"},
]

TESTIMONIOS = []

@app.context_processor
def contexto_global():
    return {
        "CATALOGO": [{"id": p["id"], "n": p["nombre"], "img": p["img"], "u": "/producto/" + p["id"]} for p in PRODUCTOS],
        "CATS": CATS, "CAT": CAT, "GRUPOS": GRUPOS, "GRUPO_DE": GRUPO_DE, "LINEAS": LINEAS, "LIN": LIN,
        "SERVICIOS": SERVICIOS, "RECURSOS": RECURSOS, "EMPRESA": EMPRESA,
    }

@app.route("/")
def index():
    return render_template("index.html", hero=HERO, destacados=[p for p in PRODUCTOS if p["dest"]], testimonios=TESTIMONIOS)

@app.route("/productos")
def productos():
    q = request.args.get("q", "").strip()
    cat = request.args.get("cat", "").strip()
    grupo = request.args.get("grupo", "").strip()
    if grupo not in GRP:
        grupo = ""
    resultado = PRODUCTOS[:]
    if q:
        ql = q.casefold()
        resultado = [
            p for p in resultado
            if ql in (
                p["nombre"] + " " + p["desc"] + " " + CAT[p["cat"]]["nombre"]
            ).casefold()
        ]
    if cat in CAT:
        resultado = [p for p in resultado if p["cat"] == cat]
    elif cat:
        cat = ""
    if grupo:
        resultado = [p for p in resultado if p["grupo"] == grupo]
    cats_con = [c for c in CATS if any(p["cat"] == c["slug"] for p in PRODUCTOS)]
    return render_template("productos.html", productos=resultado, cats_con=cats_con, q=q, cat=cat, grupo=grupo)

@app.route("/linea/<slug>")
def linea(slug):
    l = LIN.get(slug)
    if not l:
        abort(404)
    ps = [p for p in PRODUCTOS if slug in p["lin"]]
    return render_template("categoria.html", c=l, productos=ps, tipo="línea")

@app.route("/grupo/<slug>")
def grupo(slug):
    g = GRP.get(slug)
    if not g:
        abort(404)
    ps = [p for p in PRODUCTOS if p["grupo"] == slug]
    return render_template("categoria.html", c=g, productos=ps, tipo="grupo")

@app.route("/categoria/<slug>")
def categoria(slug):
    c = CAT.get(slug)
    if not c:
        abort(404)
    ps = [p for p in PRODUCTOS if p["cat"] == slug]
    return render_template("categoria.html", c=c, productos=ps, tipo="categoría")

@app.route("/producto/<pid>")
def detalle(pid):
    p = next((p for p in PRODUCTOS if p["id"] == pid), None)
    if not p:
        abort(404)
    relacionados = [x for x in PRODUCTOS if x["cat"] == p["cat"] and x["id"] != p["id"]][:4]
    return render_template("detalle_producto.html", p=p, relacionados=relacionados)

@app.route("/servicios/<slug>")
def servicio(slug):
    s = SRV.get(slug)
    if not s:
        abort(404)
    return render_template("pagina.html", t=s["nombre"], resumen=s["resumen"], lista=s["lista"], tipo="servicio", slug=slug)

@app.route("/recursos/<slug>")
def recurso(slug):
    r = REC.get(slug)
    if not r:
        abort(404)
    extras = {
        "catalogos": ["Solicita el catálogo actualizado", "Indica las categorías que te interesan", "Confirma disponibilidad y referencias"],
        "certificados": ["Identifica la marca y referencia exacta", "Solicita la ficha técnica correspondiente", "Confirma vigencia y alcance de los documentos"],
        "videos": ["Consulta siempre las instrucciones oficiales del fabricante", "Verifica que el video corresponda al modelo exacto", "La formación audiovisual no sustituye capacitación práctica"],
        "normativa": ["Identifica el tipo de trabajo y los riesgos", "Consulta fuentes oficiales y requisitos vigentes", "Solicita evaluación de una persona competente"],
        "blog": ["Selección responsable de equipos", "Inspección y cuidado del material", "Planificación del trabajo seguro en alturas"],
    }
    return render_template("pagina.html", t=r["nombre"], resumen=r["resumen"], lista=extras.get(slug, []), tipo="recurso", slug=slug)

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

def validar(form):
    errores = {}
    nombre = form.get("nombre", "").strip()
    correo = form.get("correo", "").strip()
    telefono = form.get("telefono", "").strip()
    asunto = form.get("asunto", "").strip()
    mensaje = form.get("mensaje", "").strip()
    if len(nombre) < 2:
        errores["nombre"] = "Escribe tu nombre."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]{2,}", correo):
        errores["correo"] = "Escribe un correo válido."
    if telefono and not re.fullmatch(r"[0-9+()\s-]{7,20}", telefono):
        errores["telefono"] = "Revisa el número de teléfono."
    if len(asunto) < 3:
        errores["asunto"] = "Escribe un asunto."
    if len(mensaje) < 10:
        errores["mensaje"] = "El mensaje debe tener al menos 10 caracteres."
    return errores

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    f = {
        "nombre": request.values.get("nombre", ""),
        "correo": request.values.get("correo", ""),
        "telefono": request.values.get("telefono", ""),
        "asunto": request.values.get("asunto", ""),
        "mensaje": request.values.get("mensaje", ""),
    }
    if request.args.get("cart") == "1" and not f["mensaje"]:
        f["mensaje"] = "Quiero solicitar una cotización de los productos de mi carrito. Por favor, confirmen disponibilidad y precios."
    errores = validar(f) if request.method == "POST" else {}
    valido = request.method == "POST" and not errores
    # ------------------------------------------------------------------
    # ENVÍO DE CORREO (pendiente). Aquí es donde se conectaría un servicio real:
    #   * Flask-Mail:  pip install Flask-Mail  (configurar MAIL_SERVER, MAIL_PORT,
    #                  MAIL_USERNAME, MAIL_PASSWORD y usar mail.send(Message(...)))
    #   * o smtplib + email.message.EmailMessage con tus credenciales SMTP.
    # Solo cuando el envío tenga éxito se debe mostrar un mensaje de "enviado".
    # Nunca guardes las credenciales en el código: usa variables de entorno.
    # ------------------------------------------------------------------
    return render_template("contacto.html", f=f, errores=errores, valido=valido)

@app.errorhandler(404)
def no_encontrado(error):
    return render_template("pagina.html", t="Página no encontrada", resumen="La dirección que buscas no existe o el contenido fue movido.", lista=["Vuelve al inicio", "Explora el catálogo", "Contáctanos si necesitas ayuda"], tipo="error", slug=""), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
