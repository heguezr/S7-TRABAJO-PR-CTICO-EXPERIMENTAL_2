from shared.herramientas import (
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    imprimir_info,
    confirmar,
)
from views import EstudianteController, MateriaController, MatriculaController


# =========================================================
# INICIALIZACIÓN
# =========================================================

estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)


# =========================================================
# FUNCIONES GENERALES
# =========================================================

def mostrar_lista(objetos, titulo):
    imprimir_titulo(titulo)

    if not objetos:
        imprimir_info("No hay registros para mostrar.")
        return

    for objeto in objetos:
        print(objeto)


def mostrar_detalle(objeto, titulo):
    imprimir_titulo(titulo)

    if objeto is None:
        imprimir_error("No se encontró el registro.")
        return

    print(objeto)

    for campo, valor in objeto.a_diccionario().items():
        print(f"{campo.capitalize():15}: {valor}")


def leer_id(mensaje="Ingrese el ID: "):
    try:
        return int(input(mensaje).strip())
    except ValueError:
        imprimir_error("El ID debe ser un número entero.")
        return None


def leer_texto(mensaje):
    return input(mensaje).strip()


def mostrar_resultado(resultado):
    exito, mensaje = resultado

    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


# =========================================================
# ESTUDIANTES
# =========================================================

def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")

    datos = {
        "nombre": leer_texto("Nombre: "),
        "apellido": leer_texto("Apellido: "),
        "email": leer_texto("Email: "),
        "carnet": leer_texto("Carnet: "),
        "carrera": leer_texto("Carrera: "),
    }

    mostrar_resultado(estudiantes.crear_estudiante(datos))


def ver_estudiantes():
    mostrar_lista(
        estudiantes.obtener_estudiantes(),
        "ESTUDIANTES",
    )


def buscar_estudiante():
    termino = leer_texto("Texto que desea buscar: ")

    mostrar_lista(
        estudiantes.buscar_estudiantes(termino),
        "RESULTADOS DE BÚSQUEDA",
    )


def ver_estudiante():
    id_estudiante = leer_id()

    if id_estudiante is not None:
        mostrar_detalle(
            estudiantes.obtener_estudiante(id_estudiante),
            "DETALLE DEL ESTUDIANTE",
        )


def actualizar_estudiante():
    id_estudiante = leer_id()

    if id_estudiante is None:
        return

    estudiante = estudiantes.obtener_estudiante(id_estudiante)

    if estudiante is None:
        imprimir_error("No se encontró el estudiante.")
        return

    print("Deje vacío un campo si no desea modificarlo.")

    cambios = {}

    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        valor = leer_texto(
            f"{campo.capitalize()} ({getattr(estudiante, campo)}): "
        )

        if valor:
            cambios[campo] = valor

    if not cambios:
        imprimir_info("No se realizaron cambios.")
        return

    mostrar_resultado(
        estudiantes.actualizar_estudiante(id_estudiante, cambios)
    )


def eliminar_estudiante():
    id_estudiante = leer_id()

    if id_estudiante is None:
        return

    estudiante = estudiantes.obtener_estudiante(id_estudiante)

    if estudiante is None:
        imprimir_error("No se encontró el estudiante.")
        return

    if confirmar(f"¿Eliminar a {estudiante.nombre_completo()}?"):
        mostrar_resultado(
            estudiantes.eliminar_estudiante(id_estudiante)
        )


def menu_estudiantes():
    opciones = {
        "1": ("Crear estudiante", crear_estudiante),
        "2": ("Ver todos", ver_estudiantes),
        "3": ("Buscar", buscar_estudiante),
        "4": ("Ver por ID", ver_estudiante),
        "5": ("Actualizar", actualizar_estudiante),
        "6": ("Eliminar", eliminar_estudiante),
    }

    ejecutar_menu("ESTUDIANTES", opciones)


# =========================================================
# MATERIAS
# =========================================================

def crear_materia():
    imprimir_titulo("CREAR MATERIA")

    datos = {
        "nombre": leer_texto("Nombre: "),
        "codigo": leer_texto("Código: "),
        "creditos": leer_texto("Créditos: "),
        "cupos": leer_texto("Cupos disponibles: "),
    }

    mostrar_resultado(materias.crear_materia(datos))


def ver_materias():
    mostrar_lista(materias.obtener_materias(), "MATERIAS")


def buscar_materia():
    termino = leer_texto("Texto que desea buscar: ")

    mostrar_lista(
        materias.buscar_materias(termino),
        "RESULTADOS DE BÚSQUEDA",
    )


def ver_materia():
    id_materia = leer_id()

    if id_materia is not None:
        mostrar_detalle(
            materias.obtener_materia(id_materia),
            "DETALLE DE LA MATERIA",
        )


def actualizar_materia():
    id_materia = leer_id()

    if id_materia is None:
        return

    materia = materias.obtener_materia(id_materia)

    if materia is None:
        imprimir_error("No se encontró la materia.")
        return

    print("Deje vacío un campo si no desea modificarlo.")

    cambios = {}

    for campo in ("nombre", "codigo", "creditos", "cupos"):
        valor = leer_texto(
            f"{campo.capitalize()} ({getattr(materia, campo)}): "
        )

        if valor:
            cambios[campo] = valor

    if not cambios:
        imprimir_info("No se realizaron cambios.")
        return

    mostrar_resultado(
        materias.actualizar_materia(id_materia, cambios)
    )


def eliminar_materia():
    id_materia = leer_id()

    if id_materia is None:
        return

    materia = materias.obtener_materia(id_materia)

    if materia is None:
        imprimir_error("No se encontró la materia.")
        return

    if confirmar(f"¿Eliminar la materia {materia.nombre}?"):
        mostrar_resultado(
            materias.eliminar_materia(id_materia)
        )


def menu_materias():
    opciones = {
        "1": ("Crear materia", crear_materia),
        "2": ("Ver todas", ver_materias),
        "3": ("Buscar", buscar_materia),
        "4": ("Ver por ID", ver_materia),
        "5": ("Actualizar", actualizar_materia),
        "6": ("Eliminar", eliminar_materia),
    }

    ejecutar_menu("MATERIAS", opciones)


# =========================================================
# MATRÍCULAS
# =========================================================

def crear_matricula():
    imprimir_titulo("REGISTRAR MATRÍCULA")

    print("Estudiantes disponibles:")
    mostrar_lista(estudiantes.obtener_estudiantes(), "ESTUDIANTES")

    print("Materias disponibles:")
    mostrar_lista(materias.obtener_materias(), "MATERIAS")

    id_estudiante = leer_id("ID del estudiante: ")

    if id_estudiante is None:
        return

    id_materia = leer_id("ID de la materia: ")

    if id_materia is None:
        return

    periodo = leer_texto("Período (ej. 2026-1): ")
    nota = leer_texto("Nota inicial (0 a 20): ")

    datos = {
        "estudiante_id": id_estudiante,
        "materia_id": id_materia,
        "periodo": periodo,
        "nota": nota,
    }

    mostrar_resultado(matriculas.crear_matricula(datos))


def ver_matriculas():
    mostrar_lista(
        matriculas.obtener_matriculas(),
        "MATRÍCULAS",
    )


def registrar_nota():
    id_matricula = leer_id("ID de la matrícula: ")

    if id_matricula is None:
        return

    nota = leer_texto("Nueva nota (0 a 20): ")

    mostrar_resultado(
        matriculas.registrar_nota(id_matricula, nota)
    )


def ver_certificado():
    id_matricula = leer_id("ID de la matrícula: ")

    if id_matricula is None:
        return

    certificado = matriculas.certificado(id_matricula)

    if certificado is None:
        imprimir_error("No se pudo generar el certificado.")
    else:
        imprimir_titulo("CERTIFICADO ACADÉMICO")
        print(certificado)


def retirar_matricula():
    id_matricula = leer_id("ID de la matrícula: ")

    if id_matricula is None:
        return

    matricula = matriculas.obtener_matricula(id_matricula)

    if matricula is None:
        imprimir_error("No se encontró la matrícula.")
        return

    if confirmar("¿Desea retirar esta matrícula?"):
        mostrar_resultado(
            matriculas.retirar_matricula(id_matricula)
        )


def menu_matriculas():
    opciones = {
        "1": ("Matricular", crear_matricula),
        "2": ("Ver todas", ver_matriculas),
        "3": ("Registrar nota", registrar_nota),
        "4": ("Ver certificado", ver_certificado),
        "5": ("Retirar matrícula", retirar_matricula),
    }

    ejecutar_menu("MATRÍCULAS", opciones)


# =========================================================
# RESUMEN ACADÉMICO
# =========================================================

def mostrar_resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")

    total_estudiantes = len(estudiantes.obtener_estudiantes())

    carreras = {
        estudiante.carrera
        for estudiante in estudiantes.obtener_estudiantes()
        if estudiante.carrera
    }

    materias_agotadas = materias.materias_sin_cupo()

    matriculas_aprobadas = [
        matricula
        for matricula in matriculas.obtener_matriculas()
        if matricula.esta_aprobada()
    ]

    print(f"Total de estudiantes       : {total_estudiantes}")
    print(f"Carreras distintas         : {len(carreras)}")

    for carrera in sorted(carreras):
        print(f"  - {carrera}")

    print(f"Materias sin cupo          : {len(materias_agotadas)}")
    print(f"Matrículas aprobadas       : {len(matriculas_aprobadas)}")


# =========================================================
# MENÚS
# =========================================================

def ejecutar_menu(titulo, opciones, texto_salida="Volver"):
    while True:
        imprimir_titulo(titulo)

        for clave, (texto, _) in opciones.items():
            print(f"{clave}. {texto}")

        print(f"0. {texto_salida}")

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "0":
            break

        if opcion in opciones:
            opciones[opcion][1]()
        else:
            imprimir_error("Opción no válida.")

        input("\nPresione Enter para continuar...")


def main():
    opciones = {
        "1": ("Estudiantes", menu_estudiantes),
        "2": ("Materias", menu_materias),
        "3": ("Matrículas", menu_matriculas),
        "4": ("Resumen", mostrar_resumen),
    }

    ejecutar_menu("SISTEMA ACADÉMICO", opciones, "Salir")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma finalizado.")
