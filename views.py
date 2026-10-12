from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =========================================================
# FUNCIONES GENÉRICAS
# =========================================================

def leer_objetos(gestor, modelo):
    datos = gestor.leer()
    return [modelo.desde_diccionario(registro) for registro in datos]


def obtener_por_id(objetos, id_registro):
    try:
        id_registro = int(id_registro)
    except (TypeError, ValueError):
        return None

    for objeto in objetos:
        if objeto.id == id_registro:
            return objeto

    return None


def buscar(objetos, termino, campos):
    termino = str(termino).strip().lower()

    return [
        objeto
        for objeto in objetos
        if any(
            termino in str(getattr(objeto, campo, "")).lower()
            for campo in campos
        )
    ]


def siguiente_id(objetos):
    ids = {objeto.id for objeto in objetos}
    return max(ids, default=0) + 1


def guardar_nuevo(objetos, objeto, gestor):
    objetos.append(objeto)

    if not gestor.guardar(
        [registro.a_diccionario() for registro in objetos]
    ):
        objetos.pop()
        return False

    return True


def reemplazar(objetos, objeto, gestor):
    for posicion, registro in enumerate(objetos):
        if registro.id == objeto.id:
            anterior = objetos[posicion]
            objetos[posicion] = objeto

            if not gestor.guardar(
                [registro.a_diccionario() for registro in objetos]
            ):
                objetos[posicion] = anterior
                return False

            return True

    return False


def eliminar(objetos, id_registro, gestor):
    objeto = obtener_por_id(objetos, id_registro)

    if objeto is None:
        return False

    posicion = objetos.index(objeto)
    objetos.pop(posicion)

    if not gestor.guardar(
        [registro.a_diccionario() for registro in objetos]
    ):
        objetos.insert(posicion, objeto)
        return False

    return True


def ids_registrados(objetos):
    return {objeto.id for objeto in objetos}


def indice_por_id(objetos):
    return {objeto.id: objeto for objeto in objetos}


# =========================================================
# CLASE BASE PARA LOS CONTROLADORES
# =========================================================

class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, termino):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, cambios):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =========================================================
# CONTROLADOR DE ESTUDIANTES
# =========================================================

class EstudianteController(CrudBase):

    CAMPOS_BUSCABLES = (
        "nombre",
        "apellido",
        "email",
        "carnet",
    )

    CAMPOS_EDITABLES = (
        "nombre",
        "apellido",
        "email",
        "carnet",
        "carrera",
    )

    def __init__(self, ruta="data/estudiantes.json"):
        self.gestor = GestorJSON(ruta)
        self.estudiantes = leer_objetos(self.gestor, Estudiante)

    def guardar(self):
        datos = [
            estudiante.a_diccionario()
            for estudiante in self.estudiantes
        ]
        return self.gestor.guardar(datos)

    def carnets_registrados(self, excepto_id=None):
        return {
            estudiante.carnet.strip().upper()
            for estudiante in self.estudiantes
            if estudiante.id != excepto_id and estudiante.carnet.strip()
        }

    def emails_registrados(self, excepto_id=None):
        return {
            estudiante.email.strip().lower()
            for estudiante in self.estudiantes
            if estudiante.id != excepto_id
        }

    def validar(self, datos, id_actual=None, crear=False):
        obligatorios = ("nombre", "apellido", "email", "carnet")

        if crear:
            for campo in obligatorios:
                if not str(datos.get(campo, "")).strip():
                    return False, f"El campo {campo} es obligatorio."

        email = datos.get("email")

        if email is not None:
            email = str(email).strip().lower()

            if not es_email_valido(email):
                return False, "El correo electrónico no es válido."

            if email in self.emails_registrados(id_actual):
                return False, "Ese correo electrónico ya está registrado."

        carnet = datos.get("carnet")

        if carnet is not None:
            carnet = str(carnet).strip().upper()

            if not carnet:
                return False, "El carnet es obligatorio."

            if carnet in self.carnets_registrados(id_actual):
                return False, "Ese carnet ya está registrado."

        return True, "Datos válidos."

    def leer(self):
        return self.estudiantes

    def obtener(self, id_registro):
        return obtener_por_id(self.estudiantes, id_registro)

    def buscar(self, termino):
        return buscar(
            self.estudiantes,
            termino,
            self.CAMPOS_BUSCABLES,
        )

    def siguiente(self):
        return siguiente_id(self.estudiantes)

    def crear(self, datos):
        datos = dict(datos)

        for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
            datos[campo] = str(datos.get(campo, "")).strip()

        datos["email"] = datos["email"].lower()
        datos["carnet"] = datos["carnet"].upper()

        valido, mensaje = self.validar(datos, crear=True)

        if not valido:
            return False, mensaje

        estudiante = Estudiante(
            self.siguiente(),
            datos["nombre"],
            datos["apellido"],
            datos["email"],
            datos["carnet"],
            datos["carrera"],
        )

        if not guardar_nuevo(self.estudiantes, estudiante, self.gestor):
            return False, "No se pudo guardar el estudiante."

        return True, "Estudiante creado correctamente."

    def actualizar(self, id_registro, cambios):
        estudiante = self.obtener(id_registro)

        if estudiante is None:
            return False, "No se encontró el estudiante."

        cambios = dict(cambios)

        if any(campo not in self.CAMPOS_EDITABLES for campo in cambios):
            return False, "Se intentó modificar un campo no permitido."

        datos = {
            campo: getattr(estudiante, campo)
            for campo in self.CAMPOS_EDITABLES
        }

        for campo, valor in cambios.items():
            datos[campo] = str(valor).strip()

        datos["email"] = datos["email"].lower()
        datos["carnet"] = datos["carnet"].upper()

        valido, mensaje = self.validar(datos, estudiante.id)

        if not valido:
            return False, mensaje

        actualizado = Estudiante(
            estudiante.id,
            datos["nombre"],
            datos["apellido"],
            datos["email"],
            datos["carnet"],
            datos["carrera"],
        )

        if not reemplazar(self.estudiantes, actualizado, self.gestor):
            return False, "No se pudo guardar la actualización."

        return True, "Estudiante actualizado correctamente."

    def eliminar(self, id_registro):
        if self.obtener(id_registro) is None:
            return False, "No se encontró el estudiante."

        if not eliminar(self.estudiantes, id_registro, self.gestor):
            return False, "No se pudo eliminar el estudiante."

        return True, "Estudiante eliminado correctamente."

    # Nombres solicitados en la guía

    def crear_estudiante(self, datos):
        return self.crear(datos)

    def obtener_estudiantes(self):
        return self.leer()

    def obtener_estudiante(self, id_registro):
        return self.obtener(id_registro)

    def buscar_estudiantes(self, termino):
        return self.buscar(termino)

    def actualizar_estudiante(self, id_registro, cambios):
        return self.actualizar(id_registro, cambios)

    def eliminar_estudiante(self, id_registro):
        return self.eliminar(id_registro)


# =========================================================
# CONTROLADOR DE MATERIAS
# =========================================================

class MateriaController(CrudBase):

    CAMPOS_BUSCABLES = ("nombre", "codigo")

    CAMPOS_EDITABLES = (
        "nombre",
        "codigo",
        "creditos",
        "cupos",
    )

    def __init__(self, ruta="data/materias.json"):
        self.gestor = GestorJSON(ruta)
        self.materias = leer_objetos(self.gestor, Materia)

    def guardar(self):
        datos = [
            materia.a_diccionario()
            for materia in self.materias
        ]
        return self.gestor.guardar(datos)

    def codigos_registrados(self, excepto_id=None):
        return {
            materia.codigo.strip().upper()
            for materia in self.materias
            if materia.id != excepto_id
        }

    def validar(self, datos, id_actual=None, crear=False):
        if crear:
            for campo in ("nombre", "codigo"):
                if not str(datos.get(campo, "")).strip():
                    return False, f"El campo {campo} es obligatorio."

        codigo = datos.get("codigo")

        if codigo is not None:
            codigo = str(codigo).strip().upper()

            if not codigo:
                return False, "El código es obligatorio."

            if codigo in self.codigos_registrados(id_actual):
                return False, "Ese código ya está registrado."

        try:
            creditos = int(datos.get("creditos", 0))
            cupos = int(datos.get("cupos", 0))
        except (TypeError, ValueError):
            return False, "Los créditos y los cupos deben ser números enteros."

        if crear or "creditos" in datos:
            if not 1 <= creditos <= 10:
                return False, "Los créditos deben estar entre 1 y 10."

        if crear or "cupos" in datos:
            if not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
                return False, (
                    f"Los cupos deben estar entre 0 y "
                    f"{Materia.CUPOS_MAXIMOS}."
                )

        return True, "Datos válidos."

    def leer(self):
        return self.materias

    def obtener(self, id_registro):
        return obtener_por_id(self.materias, id_registro)

    def buscar(self, termino):
        return buscar(
            self.materias,
            termino,
            self.CAMPOS_BUSCABLES,
        )

    def siguiente(self):
        return siguiente_id(self.materias)

    def crear(self, datos):
        datos = dict(datos)
        datos["nombre"] = str(datos.get("nombre", "")).strip()
        datos["codigo"] = str(datos.get("codigo", "")).strip().upper()

        valido, mensaje = self.validar(datos, crear=True)

        if not valido:
            return False, mensaje

        materia = Materia(
            self.siguiente(),
            datos["nombre"],
            datos["codigo"],
            int(datos["creditos"]),
            int(datos["cupos"]),
        )

        if not guardar_nuevo(self.materias, materia, self.gestor):
            return False, "No se pudo guardar la materia."

        return True, "Materia creada correctamente."

    def actualizar(self, id_registro, cambios):
        materia = self.obtener(id_registro)

        if materia is None:
            return False, "No se encontró la materia."

        cambios = dict(cambios)

        if any(campo not in self.CAMPOS_EDITABLES for campo in cambios):
            return False, "Se intentó modificar un campo no permitido."

        datos = {
            campo: getattr(materia, campo)
            for campo in self.CAMPOS_EDITABLES
        }
        datos.update(cambios)

        datos["nombre"] = str(datos["nombre"]).strip()
        datos["codigo"] = str(datos["codigo"]).strip().upper()

        valido, mensaje = self.validar(datos, materia.id)

        if not valido:
            return False, mensaje

        actualizada = Materia(
            materia.id,
            datos["nombre"],
            datos["codigo"],
            int(datos["creditos"]),
            int(datos["cupos"]),
        )

        if not reemplazar(self.materias, actualizada, self.gestor):
            return False, "No se pudo guardar la actualización."

        return True, "Materia actualizada correctamente."

    def eliminar(self, id_registro):
        if self.obtener(id_registro) is None:
            return False, "No se encontró la materia."

        if not eliminar(self.materias, id_registro, self.gestor):
            return False, "No se pudo eliminar la materia."

        return True, "Materia eliminada correctamente."

    def materias_sin_cupo(self):
        return [
            materia
            for materia in self.materias
            if not materia.hay_cupo()
        ]

    # Nombres solicitados en la guía

    def crear_materia(self, datos):
        return self.crear(datos)

    def obtener_materias(self):
        return self.leer()

    def obtener_materia(self, id_registro):
        return self.obtener(id_registro)

    def buscar_materias(self, termino):
        return self.buscar(termino)

    def actualizar_materia(self, id_registro, cambios):
        return self.actualizar(id_registro, cambios)

    def eliminar_materia(self, id_registro):
        return self.eliminar(id_registro)


# =========================================================
# CONTROLADOR DE MATRÍCULAS
# =========================================================

class MatriculaController(CrudBase):

    CAMPOS_BUSCABLES = (
        "periodo",
        "fecha",
        "estudiante_id",
        "materia_id",
    )

    def __init__(
        self,
        estudiantes,
        materias,
        ruta="data/matriculas.json",
    ):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(ruta)
        self.matriculas = leer_objetos(self.gestor, Matricula)

    def guardar(self):
        datos = [
            matricula.a_diccionario()
            for matricula in self.matriculas
        ]
        return self.gestor.guardar(datos)

    def leer(self):
        return self.matriculas

    def obtener(self, id_registro):
        return obtener_por_id(self.matriculas, id_registro)

    def buscar(self, termino):
        return buscar(
            self.matriculas,
            termino,
            self.CAMPOS_BUSCABLES,
        )

    def siguiente(self):
        return siguiente_id(self.matriculas)

    def crear(self, datos):
        datos = dict(datos)

        try:
            estudiante_id = int(datos["estudiante_id"])
            materia_id = int(datos["materia_id"])
            nota = float(datos.get("nota", 0))
        except (KeyError, TypeError, ValueError):
            return False, "Los IDs y la nota deben ser válidos."

        periodo = str(datos.get("periodo", "")).strip()

        if not periodo:
            return False, "El período es obligatorio."

        estudiante = self.estudiantes.obtener(estudiante_id)

        if estudiante is None:
            return False, "El estudiante no existe."

        materia = self.materias.obtener(materia_id)

        if materia is None:
            return False, "La materia no existe."

        if not materia.hay_cupo():
            return False, "La materia no tiene cupos disponibles."

        for matricula in self.matriculas:
            if (
                matricula.estudiante_id == estudiante_id
                and matricula.materia_id == materia_id
                and matricula.periodo.lower() == periodo.lower()
            ):
                return False, (
                    "El estudiante ya está matriculado en esa materia "
                    "durante ese período."
                )

        if not Materia.es_nota_valida(nota):
            return False, "La nota debe estar entre 0 y 20."

        matricula = Matricula(
            self.siguiente(),
            estudiante_id,
            materia_id,
            periodo,
            nota,
        )

        # Ocupar y guardar el cupo primero.
        materia.ocupar_cupo()

        if not self.materias.guardar():
            materia.liberar_cupo()
            return False, "No se pudo actualizar el cupo de la materia."

        if not guardar_nuevo(
            self.matriculas,
            matricula,
            self.gestor,
        ):
            materia.liberar_cupo()
            self.materias.guardar()
            return False, "No se pudo guardar la matrícula."

        return True, "Matrícula creada correctamente."

    def actualizar(self, id_registro, cambios):
        return False, "Utiliza registrar_nota() para modificar la nota."

    def eliminar(self, id_registro):
        return self.retirar_matricula(id_registro)

    def registrar_nota(self, id_registro, nota):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return False, "No se encontró la matrícula."

        if not Materia.es_nota_valida(nota):
            return False, "La nota debe estar entre 0 y 20."

        nota_anterior = matricula.nota
        matricula.nota = float(nota)

        if not self.guardar():
            matricula.nota = nota_anterior
            return False, "No se pudo guardar la nota."

        return True, "Nota registrada correctamente."

    def retirar_matricula(self, id_registro):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return False, "No se encontró la matrícula."

        materia = self.materias.obtener(matricula.materia_id)

        if materia is None:
            return False, "No se encontró la materia asociada."

        posicion = self.matriculas.index(matricula)

        # Liberar el cupo y persistirlo.
        materia.liberar_cupo()

        if not self.materias.guardar():
            materia.cupos -= 1
            return False, "No se pudo actualizar el cupo."

        self.matriculas.pop(posicion)

        if not self.guardar():
            self.matriculas.insert(posicion, matricula)
            materia.ocupar_cupo()
            self.materias.guardar()
            return False, "No se pudo retirar la matrícula."

        return True, "Matrícula retirada correctamente."

    def certificado(self, id_registro):
        matricula = self.obtener(id_registro)

        if matricula is None:
            return None

        estudiantes = indice_por_id(self.estudiantes.leer())
        materias = indice_por_id(self.materias.leer())

        estudiante = estudiantes.get(matricula.estudiante_id)
        materia = materias.get(matricula.materia_id)

        if estudiante is None or materia is None:
            return None

        return (
            f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
            f"Estudiante: {estudiante.nombre_completo()}   "
            f"({estudiante.carnet})\n"
            f"Materia   : {materia.nombre}   ({materia.codigo}) · "
            f"{materia.creditos} créditos\n"
            f"{'-' * 42}\n"
            f"Nota      : {matricula.nota}\n"
            f"Estado    : {matricula.estado()}"
        )

    def matriculas_por_estudiante(self):
        agrupadas = {}

        for matricula in self.matriculas:
            agrupadas.setdefault(
                matricula.estudiante_id, []
            ).append(matricula)

        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        if self.estudiantes.obtener(id_estudiante) is None:
            return None

        notas = [
            matricula.nota
            for matricula in self.matriculas
            if matricula.estudiante_id == int(id_estudiante)
        ]

        if not notas:
            return 0

        return round(sum(notas) / len(notas), 2)

    # Nombres solicitados en la guía

    def crear_matricula(self, datos):
        return self.crear(datos)

    def obtener_matriculas(self):
        return self.leer()

    def obtener_matricula(self, id_registro):
        return self.obtener(id_registro)