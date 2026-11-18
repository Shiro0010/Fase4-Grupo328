# =========================================================================================================
# ARCHIVO MAESTRO UNIFICADO - SOFTWARE FJ (MÓDULOS 1, 2, 3 Y CLI GLOBAL)
# =========================================================================================================

from abc import ABC, abstractmethod
import datetime
import math
import os 

# =========================================================================================================
# Módulo LOG: CONFIGURACIÓN Y LOGS - Por Manuel Chaux 
# =========================================================================================================
MAPA_CODIGOS_LOG = """
====================== MAPA DE REFERENCIA DE ERRORES - SOFTWARE FJ ======================
||-[INFO]    : Evento operativo normal o registro exitoso.                             ||
||-[WARNING] : Advertencia de validación (datos incorrectos del usuario).              ||
||-[ERROR]   : Fallo crítico de operación (operación rechazada, excepción controlada). ||
||-------------------------------------------------------------------------------------||
||-[CLI-001] : Error en datos o formato de cliente.                                    ||
||-[SYS-002] : Falta un parámetro obligatorio en la función.                           ||
||-[SRV-003] : Servicio no disponible o parámetros de tarifa inválidos.                ||
=========================================================================================
"""

#Con esta funcion se inicializa el archivo log en caso de que no exista
# y se agrega el mapa de referencia al inicio del archivo.
def inicializar_archivo_log():
    """Configura y crea el archivo de registro de eventos con su mapa de referencia."""
    nombre_archivo = "registro_eventos.log"
    if not os.path.exists(nombre_archivo):
        try:
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(MAPA_CODIGOS_LOG.strip() + "\n\n")
        except Exception as e:
            print(f"[ERROR CRÍTICO]: No se pudo inicializar el archivo log: {e}")

#Esta funcion sera llamada cada vez que se quiera registrar un evento, error o advertencia en el log.
def registrar_en_log(mensaje: str, tipo: str = "INFO"):
    """Registra los errores y sucesos con marca de tiempo en el archivo log."""
    inicializar_archivo_log()
    nombre_archivo = "registro_eventos.log"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea_log = f"[{timestamp}] [{tipo}] {mensaje}\n"

    try:
        with open(nombre_archivo, "a", encoding="utf-8") as archivo:
            archivo.write(linea_log)
    except Exception as e:
        print(f"[ERROR DE LOGS]: Fallo al intentar escribir en el archivo: {e}")
    finally:
        pass


# =========================================================================================================
# EXCEPCIONES PERSONALIZADAS
# =========================================================================================================

#esta es la clase base de todas las demas excepciones del sistema, que permite un formato uniforme y un nivel de gravedad automático.
class ErrorSistemaFJ(Exception):
    """Excepción base del sistema con formato y gravedad automática."""
    def __init__(self, mensaje: str, codigo: str = "ERR-000", nivel: str = "ERROR"):
        self.codigo = codigo
        self.nivel = nivel
        mensaje_completo = f"[{self.nivel}] ({self.codigo}): {mensaje}"
        super().__init__(mensaje_completo)


'''Creamos 3 tipos de excepiones para el sistema, cada una con un codigo y nivel de gravedad diferente,'''

class ClienteNoValidoException(ErrorSistemaFJ):
    """Excepción para datos de cliente incorrectos o incompletos."""
    def __init__(self, mensaje: str = "Los datos del cliente no cumplen con el formato requerido."):
        super().__init__(mensaje, codigo="CLI-001", nivel="WARNING")


class ParametroFaltanteException(ErrorSistemaFJ):
    """Excepción para argumentos obligatorios ausentes en las funciones."""
    def __init__(self, mensaje: str = "Falta un argumento obligatorio en la operación."):
        super().__init__(mensaje, codigo="SYS-002", nivel="ERROR")


class ServicioNoValidoException(ErrorSistemaFJ):
    """Excepción para servicios no disponibles o parámetros inválidos."""
    def __init__(self, mensaje: str = "El servicio solicitado no está disponible o es inválido."):
        super().__init__(mensaje, codigo="SRV-003", nivel="ERROR")


# =========================================================================================================
# MÓDULO 1: GESTIÓN DE CLIENTES
# =========================================================================================================

#Esta clase representa a un cliente con sus datos básicos y validación de entrada.
class Cliente:
    def __init__(self, nombre: str, cedula: str, correo: str):
        self.validar_datos_entrada(nombre, cedula, correo)
        self.__nombre = nombre.strip().title()
        self.__cedula = cedula.strip()
        self.__correo = correo.strip().lower()
        registrar_en_log(f"cliente creado exitosamente: {self.__correo}", "INFO")
    
    # Esta función valida los datos de entrada del cliente y lanza excepciones si no cumplen con los criterios.
    def validar_datos_entrada(self, nombre: str, cedula: str, correo: str):
        if not nombre or not nombre.strip():
            registrar_en_log("Nombre de cliente inválido.", "WARNING")
            raise ClienteNoValidoException("El nombre del cliente no puede estar vacío.")         

        if not cedula or not cedula.isdigit() or len(cedula) < 6:
            registrar_en_log(f"cedula de cliente invalida: {cedula}.", "WARNING")
            raise ClienteNoValidoException("La cédula debe ser un número válido de al menos 6 dígitos.")
        
        if not correo or "@" not in correo or "." not in correo:
            registrar_en_log(f"correo de cliente invalido: {correo}.", "WARNING")
            raise ClienteNoValidoException("El correo electrónico no tiene un formato válido.")
    
    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def cedula(self) -> str:
        return self.__cedula

    @property
    def correo(self) -> str:
        return self.__correo

#Con esta clase se gestiona la lista de clientes, permitiendo agregar y buscar clientes
# asegurando que no haya duplicados por cédula o correo.
class GestorClientes:
    def __init__(self):
        self.__lista_clientes = []

    """esta funcion agrega un cliente a la lista,
    no sin antes validar sus datos y verificar la inexistencia de duplicados por cédula o correo"""
    
    #Funcion para agregar un cliente a la lista de clientes
    def agregar_cliente(self, cliente: Cliente) -> None:
        for c in self.__lista_clientes:
            if c.cedula == cliente.cedula:
                registrar_en_log(f"Intento de duplicado bloqueado por cédula: {cliente.cedula}", "WARNING")
                raise ClienteNoValidoException("Ya existe un cliente registrado con esta cédula en el sistema.")

            if c.correo == cliente.correo:
                registrar_en_log(f"Intento de duplicado bloqueado por correo: {cliente.correo}", "WARNING")
                raise ClienteNoValidoException("Ya existe un cliente registrado con este correo en el sistema.")

        self.__lista_clientes.append(cliente)
        registrar_en_log(f"Cliente con correo {cliente.correo} añadido con éxito al registro", "INFO")

    #Funcion para buscar un cliente por su cédula, si no lo encuentra lanza una excepción
    def buscar_cliente_por_cedula(self, cedula: str) -> Cliente:
        cedula_limpia = str(cedula).strip()
        for c in self.__lista_clientes:
            if c.cedula == cedula_limpia:
                return c
        raise ClienteNoValidoException(f"No se encontró ningún cliente registrado con la cédula {cedula_limpia}.")

    @property
    def clientes(self) -> list:
        return self.__lista_clientes


# =========================================================================================================
# MÓDULO 2: SERVICIOS - Por Mónica Ortega
# =========================================================================================================

#clase abstracta que representa un servicio genérico, con atributos y métodos comunes a todos los tipos de servicios.
class Servicio(ABC):
    IVA = 0.19

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float):
        if id_servicio is None or str(id_servicio).strip() == "":
            registrar_en_log("Se intentó crear un servicio sin código.", "ERROR")
            raise ParametroFaltanteException("El servicio necesita un código.")

        if nombre is None or str(nombre).strip() == "":
            registrar_en_log(f"El servicio {id_servicio} no tiene nombre.", "ERROR")
            raise ParametroFaltanteException("El servicio necesita un nombre.")

        try:
            tarifa_base = float(tarifa_base)
        except (TypeError, ValueError, OverflowError) as error:
            registrar_en_log(f"La tarifa del servicio {id_servicio} no es un número.", "ERROR")
            raise ServicioNoValidoException("La tarifa base debe ser un número.") from error

        if not math.isfinite(tarifa_base) or tarifa_base <= 0:
            registrar_en_log(f"La tarifa del servicio {id_servicio} no es un número finito mayor que cero.", "ERROR")
            raise ServicioNoValidoException("La tarifa base debe ser un número finito mayor que cero.")

        self._id_servicio = str(id_servicio).strip().upper()
        self._nombre = str(nombre).strip()
        self._tarifa_base = tarifa_base
        self._disponible = True 

    @property
    def id_servicio(self) -> str:
        return self._id_servicio

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    #Esta función permite cambiar el estado de disponibilidad del servicio y registra el cambio en el log.
    def cambiar_disponibilidad(self, estado: bool) -> None:
        self._disponible = estado
        if estado:
            registrar_en_log(f"El servicio {self._id_servicio} quedó disponible.", "INFO")
        else:
            registrar_en_log(f"El servicio {self._id_servicio} quedó NO disponible.", "INFO")

    #Esta función valida los parámetros de cantidad y descuento, asegurando que sean correctos y que el servicio esté disponible.
    def validar_parametros(self, cantidad=None, descuento=0) -> None:
        if cantidad is None:
            registrar_en_log(f"Falta la cantidad en el servicio {self._id_servicio}.", "ERROR")
            raise ParametroFaltanteException("Falta indicar la cantidad (horas o días).")

        if not isinstance(cantidad, int) or cantidad <= 0:
            registrar_en_log(f"Cantidad inválida en {self._id_servicio}: {cantidad}", "ERROR")
            raise ServicioNoValidoException("La cantidad debe ser un número entero mayor que cero.")
        
        if not self._disponible:
            registrar_en_log(f"Se intentó usar el servicio {self._id_servicio}, que no está disponible.", "ERROR")
            raise ServicioNoValidoException(f"El servicio '{self._nombre}' no está disponible.")

        if (not isinstance(descuento, (int, float)) or descuento < 0 or descuento > 100
                or not math.isfinite(descuento)):
            registrar_en_log(f"Descuento inválido en {self._id_servicio}: {descuento}", "ERROR")
            raise ServicioNoValidoException("El descuento debe ser un número finito entre 0 y 100.")

    def _aplicar_descuento_e_iva(self, subtotal: float, descuento: float, con_iva: bool) -> float:
        valor = subtotal - (subtotal * descuento / 100)
        if con_iva:
            valor = valor * (1 + self.IVA)
        return round(valor, 2)

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        pass

    @abstractmethod
    def obtener_descripcion(self) -> str:
        pass

#con esta clase se implementa el servicio de sala de reuniones
#con validaciones específicas para horas máximas y descuentos por jornada completa.
class SalaReunionServicio(Servicio):
    HORAS_MAXIMAS = 12
    HORAS_PARA_DESCUENTO = 4
    DESCUENTO_JORNADA = 10

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, capacidad: int):
        super().__init__(id_servicio, nombre, tarifa_base)
        if not isinstance(capacidad, int) or capacidad <= 0:
            registrar_en_log(f"Capacidad inválida en la sala {id_servicio}: {capacidad}", "ERROR")
            raise ServicioNoValidoException("La capacidad de la sala debe ser un entero mayor que cero.")
        self._capacidad = capacidad

    def validar_parametros(self, cantidad=None, descuento=0) -> None:
        super().validar_parametros(cantidad, descuento)
        if cantidad > self.HORAS_MAXIMAS:
            registrar_en_log(f"Sala {self._id_servicio}: {cantidad} horas es demasiado.", "ERROR")
            raise ServicioNoValidoException(f"Una sala se reserva máximo {self.HORAS_MAXIMAS} horas.")

    def calcular_costo(self, cantidad=None, descuento=0, con_iva=False) -> float:
        self.validar_parametros(cantidad, descuento)
        subtotal = self._tarifa_base * cantidad
        if cantidad >= self.HORAS_PARA_DESCUENTO:
            subtotal = subtotal - (subtotal * self.DESCUENTO_JORNADA / 100)
        return self._aplicar_descuento_e_iva(subtotal, descuento, con_iva)

    def obtener_descripcion(self) -> str:
        return (f"Sala '{self._nombre}' ({self._id_servicio}) - capacidad: {self._capacidad} personas - "
                f"${self._tarifa_base:,.0f} por hora")

#con esta clase se implementa el servicio de alquiler de equipos
class AlquilerEquipoServicio(Servicio):
    TIPOS_VALIDOS = ("informatico", "oficina")
    DIAS_MAXIMOS = 30
    SEGURO = 5

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, tipo_equipo: str):
        super().__init__(id_servicio, nombre, tarifa_base)
        tipo = str(tipo_equipo).strip().lower()
        if tipo not in self.TIPOS_VALIDOS:
            registrar_en_log(f"Tipo de equipo inválido en {id_servicio}: {tipo_equipo}", "ERROR")
            raise ServicioNoValidoException("El tipo de equipo debe ser 'informatico' u 'oficina'.")
        self._tipo_equipo = tipo

    def validar_parametros(self, cantidad=None, descuento=0) -> None:
        super().validar_parametros(cantidad, descuento)
        if cantidad > self.DIAS_MAXIMOS:
            registrar_en_log(f"Alquiler {self._id_servicio}: {cantidad} días es demasiado.", "ERROR")
            raise ServicioNoValidoException(f"Un equipo se alquila máximo {self.DIAS_MAXIMOS} días.")

    def calcular_costo(self, cantidad=None, descuento=0, con_iva=False) -> float:
        self.validar_parametros(cantidad, descuento)
        subtotal = self._tarifa_base * cantidad
        subtotal = subtotal + (subtotal * self.SEGURO / 100)
        return self._aplicar_descuento_e_iva(subtotal, descuento, con_iva)

    def obtener_descripcion(self) -> str:
        return (f"Equipo {self._tipo_equipo} '{self._nombre}' ({self._id_servicio}) - "
                f"${self._tarifa_base:,.0f} por día más {self.SEGURO} % de seguro")

#con esta clase se implementa el servicio de asesoría especializada
class AsesoriaEspecializadaServicio(Servicio):
    NIVELES = {"junior": 1.0, "senior": 1.5}
    HORAS_MAXIMAS = 8

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, especialidad: str, nivel: str = "junior"):
        super().__init__(id_servicio, nombre, tarifa_base)
        if especialidad is None or str(especialidad).strip() == "":
            registrar_en_log(f"La asesoría {id_servicio} no tiene especialidad.", "ERROR")
            raise ParametroFaltanteException("La asesoría necesita una especialidad.")

        nivel_limpio = str(nivel).strip().lower()
        if nivel_limpio not in self.NIVELES:
            registrar_en_log(f"Nivel inválido en la asesoría {id_servicio}: {nivel}", "ERROR")
            raise ServicioNoValidoException("El nivel del asesor debe ser 'junior' o 'senior'.")

        self._especialidad = str(especialidad).strip()
        self._nivel = nivel_limpio

    """con este metodo se validan los parámetros de la asesoría"""
    def validar_parametros(self, cantidad=None, descuento=0) -> None:
        super().validar_parametros(cantidad, descuento)
        if cantidad > self.HORAS_MAXIMAS:
            registrar_en_log(f"Asesoría {self._id_servicio}: {cantidad} horas es demasiado.", "ERROR")
            raise ServicioNoValidoException(f"Una asesoría dura máximo {self.HORAS_MAXIMAS} horas.")

    #este metodo calcula el costo de la asesoria considerando los parametros de cantidad, descuento y si se aplica IVA o no.
    def calcular_costo(self, cantidad=None, descuento=0, con_iva=False) -> float:
        self.validar_parametros(cantidad, descuento)
        multiplicador = self.NIVELES[self._nivel]
        subtotal = self._tarifa_base * cantidad * multiplicador   
        return self._aplicar_descuento_e_iva(subtotal, descuento, con_iva)

    #este metodo devuelve una descripción completa del servicio de asesoría incluyendo especialidad, nombre, código, nivel del asesor y tarifa base.
    def obtener_descripcion(self) -> str:
        return (f"Asesoría en {self._especialidad} '{self._nombre}' ({self._id_servicio}) - "
                f"asesor {self._nivel} - ${self._tarifa_base:,.0f} por hora base")


# Funciones de apoyo y Gestor del Módulo 2
def calcular_costo_seguro(servicio, cantidad=None, descuento=0, con_iva=False) -> float:
    try:
        costo = servicio.calcular_costo(cantidad, descuento, con_iva)
    except ErrorSistemaFJ:
        raise
    except (TypeError, ValueError, AttributeError) as error:
        registrar_en_log(f"Fallo inesperado al calcular el costo: {error}", "ERROR")
        raise ServicioNoValidoException("No se pudo calcular el costo del servicio.") from error
    else:
        registrar_en_log(f"Costo calculado para {servicio.id_servicio}: ${costo:,.2f}", "INFO")
        return costo
    finally:
        registrar_en_log("Fin del intento de cálculo de costo.", "INFO")

#esta funcion crea un catálogo inicial de servicios para el sistema
#incluyendo salas de reuniones, alquiler de equipos y asesorías especializadas.
def crear_catalogo_servicios() -> list:
    return [
        SalaReunionServicio("SAL-01", "Sala Ejecutiva", 50000, 10),
        AlquilerEquipoServicio("EQU-01", "Portatil Profesional", 40000, "informatico"),
        AsesoriaEspecializadaServicio("ASE-01", "Ciberseguridad", 120000, "Ciberseguridad", "senior"),
    ]

#Este es el gestor de servicios que mantiene una lista de servicios disponibles
#permite agregar nuevos servicios y buscar servicios por su código.
class GestorServicios:
    def __init__(self):
        self._lista_servicios = []

    def agregar_servicio(self, servicio: Servicio) -> None:
        for s in self._lista_servicios:
            if s.id_servicio == servicio.id_servicio:
                registrar_en_log(f"Intento de duplicado bloqueado: servicio {servicio.id_servicio}", "WARNING")
                raise ServicioNoValidoException(f"Ya existe un servicio con el código {servicio.id_servicio}.")
        self._lista_servicios.append(servicio)
        registrar_en_log(f"Servicio {servicio.id_servicio} agregado al catálogo.", "INFO")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        codigo = str(id_servicio).strip().upper()  
        for s in self._lista_servicios:
            if s.id_servicio == codigo:
                return s
        registrar_en_log(f"Se buscó el servicio {codigo} y no existe.", "WARNING")
        raise ServicioNoValidoException(f"No existe ningún servicio con el código {codigo}.")

    @property
    def servicios(self) -> list:
        return list(self._lista_servicios)

#Este bloque inicializa el gestor de servicios y carga un catálogo predeterminado al iniciar el sistema.
gestor_servicios = GestorServicios()
for _servicio in crear_catalogo_servicios():
    gestor_servicios.agregar_servicio(_servicio)

"""esta funcion permite leer un número entero desde la entrada del usuario
validando que sea correcto y registrando advertencias en el log si no lo es."""
def leer_entero(pregunta: str):
    texto = input(pregunta).strip()
    if texto == "":
        return None
    try:
        return int(texto)
    except ValueError as error:
        registrar_en_log(f"Se escribió '{texto}' donde se esperaba un número entero.", "WARNING")
        raise ServicioNoValidoException(f"'{texto}' no es un número entero válido.") from error

"""esta funcion permite leer un número decimal desde la entrada del usuario
validando que sea correcto y registrando advertencias en el log si no lo es."""
def leer_decimal(pregunta: str):
    texto = input(pregunta).strip()
    if texto == "":
        return None
    try:
        numero = float(texto)
    except ValueError as error:
        registrar_en_log(f"Se escribió '{texto}' donde se esperaba un número.", "WARNING")
        raise ServicioNoValidoException(f"'{texto}' no es un número válido.") from error
    if not math.isfinite(numero):
        registrar_en_log(f"Se escribió '{texto}' donde se esperaba un número finito.", "WARNING")
        raise ServicioNoValidoException("El número debe ser finito.")
    return numero

"""esta funcion permite ver el catálogo de servicios disponibles."""
def ver_catalogo() -> None:
    print("\n--- CATÁLOGO DE SERVICIOS ---")
    servicios = gestor_servicios.servicios
    if not servicios:
        print("No hay servicios registrados todavía.")
        return
    for i, servicio in enumerate(servicios, 1):
        estado = "disponible" if servicio.disponible else "NO disponible"
        print(f"{i}. {servicio.obtener_descripcion()} [{estado}]")

"""Este método interactivo permite al usuario crear un nuevo servicio
solicitando los datos necesarios según el tipo de servicio elegido."""
def crear_servicio_interactivo() -> None:
    print("\n--- CREAR SERVICIO NUEVO ---")
    print("1. Sala de reuniones")
    print("2. Alquiler de equipo")
    print("3. Asesoría especializada")
    tipo = input("Tipo de servicio (1-3): ").strip()

    if tipo not in ("1", "2", "3"):
        registrar_en_log(f"Tipo de servicio inválido: {tipo}", "WARNING")
        raise ServicioNoValidoException("Tipo de servicio inválido. Elige 1, 2 o 3.")

    id_servicio = input("Código del servicio (ejemplo SAL-02): ")
    nombre = input("Nombre del servicio: ")
    tarifa = leer_decimal("Tarifa base (por hora, o por día en equipos): ")

    if tipo == "1":
        capacidad = leer_entero("Capacidad de la sala (personas): ")
        servicio = SalaReunionServicio(id_servicio, nombre, tarifa, capacidad)
    elif tipo == "2":
        tipo_equipo = input("Tipo de equipo (informatico u oficina): ")
        servicio = AlquilerEquipoServicio(id_servicio, nombre, tarifa, tipo_equipo)
    else:
        especialidad = input("Especialidad de la asesoría: ")
        nivel = input("Nivel del asesor (junior o senior): ")
        servicio = AsesoriaEspecializadaServicio(id_servicio, nombre, tarifa, especialidad, nivel)

    gestor_servicios.agregar_servicio(servicio)
    print("Servicio creado con éxito:")
    print(f"  {servicio.obtener_descripcion()}")

"""esta funcion permite calcular el costo de un servicio según sus parámetros."""
def calcular_costo_interactivo() -> None:
    print("\n--- CALCULAR COSTO DE UN SERVICIO ---")
    ver_catalogo()
    codigo = input("\nCódigo del servicio: ")
    servicio = gestor_servicios.buscar_servicio(codigo)

    cantidad = leer_entero("Cantidad (horas o días): ")
    descuento = leer_decimal("Descuento en % (deja vacío si no hay): ")
    if descuento is None:
        descuento = 0
    respuesta = input("¿Aplicar IVA del 19 %? (s/n): ").strip().lower()
    con_iva = respuesta == "s"

    costo = calcular_costo_seguro(servicio, cantidad, descuento, con_iva)
    print(f"\n{servicio.obtener_descripcion()}")
    print(f"Costo total: ${costo:,.2f}")

"""esta funcion permite cambiar la disponibilidad de un servicio."""
def cambiar_disponibilidad_interactivo() -> None:
    print("\n--- ACTIVAR O DESACTIVAR UN SERVICIO ---")
    ver_catalogo()
    codigo = input("\nCódigo del servicio: ")
    servicio = gestor_servicios.buscar_servicio(codigo)

    servicio.cambiar_disponibilidad(not servicio.disponible) 
    if servicio.disponible:
        print(f"El servicio {servicio.id_servicio} ahora está DISPONIBLE.")
    else:
        print(f"El servicio {servicio.id_servicio} ahora está NO DISPONIBLE.")

"""esta funcion imprime el menú relacionado al modulo de servicios en consola"""
def mostrar_menu_servicios() -> None:
    print("\n==============================================")
    print("            MÓDULO DE SERVICIOS               ")
    print("==============================================")
    print("1. Ver catálogo de servicios")
    print("2. Crear un servicio nuevo")
    print("3. Calcular el costo de un servicio")
    print("4. Activar o desactivar un servicio")
    print("5. Volver al menú principal")
    print("==============================================")

"""Esta funcion convoca los métodos relacionados al menú de servicios según la opcion digitada a traves de
cada input"""
def menu_servicios() -> None:
    while True:
        mostrar_menu_servicios()
        opcion = input("Selecciona una opción (1-5): ").strip()
        try:
            if opcion == "1":
                ver_catalogo()
            elif opcion == "2":
                crear_servicio_interactivo()
            elif opcion == "3":
                calcular_costo_interactivo()
            elif opcion == "4":
                cambiar_disponibilidad_interactivo()
            elif opcion == "5":
                print("\nVolviendo al menú principal...")
                break
            else:
                print("Opción inválida. Por favor, elige un número del 1 al 5.")
        except ErrorSistemaFJ as error:
            print(f"\n[AVISO DEL SISTEMA]: {error}")
        except EOFError:
            print("\nEntrada finalizada. Volviendo al menú principal...")
            break
        except Exception as error:
            registrar_en_log(f"Fallo imprevisto en el menú de servicios: {error}", "ERROR")
            print(f"\n[ERROR INESPERADO]: Ocurrió un fallo imprevisto: {error}")


# =========================================================================================================
# MÓDULO 3: GESTIÓN DE RESERVAS
# =========================================================================================================

"""esta clase representa una reserva de un servicio por parte de un cliente"""
class Reserva:
    def __init__(self, id_reserva: str, cliente, codigo_servicio: str, cantidad: int, fecha: str):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.codigo_servicio = codigo_servicio
        self.cantidad = cantidad
        fecha_texto = str(fecha).strip()
        try:
            fecha_validada = datetime.date.fromisoformat(fecha_texto)
        except ValueError as error:
            raise ErrorSistemaFJ("La fecha debe tener el formato YYYY-MM-DD.") from error
        if fecha_validada.isoformat() != fecha_texto:
            raise ErrorSistemaFJ("La fecha debe tener el formato YYYY-MM-DD.")
        self.fecha = fecha_validada.isoformat()
        self.estado = "Pendiente"
        self.costo_calculado = 0.0
        self.servicio_asociado = None

    @property
    def id_reserva(self):
        return self._id_reserva

    @id_reserva.setter
    def id_reserva(self, valor):
        if not valor or not str(valor).strip():
            raise ErrorSistemaFJ("El ID de la reserva no puede estar vacío.")
        self._id_reserva = str(valor).strip().upper()

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            registrar_en_log(f"Cantidad de reserva inválida intentada: {valor}", "WARNING")
            raise ErrorSistemaFJ("La cantidad (horas o días) debe ser un número entero mayor a cero.")
        self._cantidad = valor

    #este metodo valida que el servicio asociado a la reserva esté disponible y calcula el costo de la reserva
    def validar_y_preparar(self) -> None:
        self.servicio_asociado = gestor_servicios.buscar_servicio(self.codigo_servicio)
        
        if not self.servicio_asociado.disponible:
            registrar_en_log(f"Intento de reservar servicio no disponible: {self.codigo_servicio}", "WARNING")
            raise ErrorSistemaFJ(f"El servicio '{self.servicio_asociado.nombre}' no se encuentra disponible.")
        
        try:
            self.costo_calculado = calcular_costo_seguro(self.servicio_asociado, self.cantidad)
            registrar_en_log(f"Costo calculado con éxito para la reserva {self.id_reserva}: ${self.costo_calculado}", "INFO")
        except Exception as error:
            registrar_en_log(f"Fallo al calcular costo en reserva {self.id_reserva}: {error}", "ERROR")
            raise ErrorSistemaFJ(f"No fue posible calcular el costo del servicio: {error}") from error

    #este metodo confirma la reserva, cambiando su estado a "Confirmada" y registrando el evento en el log
    def confirmar(self) -> None:
        if self.estado != "Pendiente":
            raise ErrorSistemaFJ(f"No se puede confirmar una reserva en estado '{self.estado}'.")
        
        self.validar_y_preparar()
        self.estado = "Confirmada"
        registrar_en_log(f"Reserva {self.id_reserva} confirmada para el cliente {self.cliente.nombre}.", "INFO")

    #este metodo procesa la reserva, cambiando su estado a "Procesada" y registrando el evento en el log
    def procesar(self) -> None:
        if self.estado != "Confirmada":
            registrar_en_log(f"Intento de procesar reserva {self.id_reserva} en estado inválido: {self.estado}", "WARNING")
            raise ErrorSistemaFJ(f"No se puede procesar la reserva. Su estado actual es '{self.estado}' y debe estar 'Confirmada'.")
        
        self.estado = "Procesada"
        registrar_en_log(f"Reserva {self.id_reserva} procesada exitosamente.", "INFO")

    #este metodo cancela la reserva, cambiando su estado a "Cancelada" y registrando el evento en el log
    def cancelar(self) -> None:
        if self.estado == "Procesada":
            raise ErrorSistemaFJ("No se puede cancelar una reserva que ya fue procesada.")
        
        self.estado = "Cancelada"
        registrar_en_log(f"Reserva {self.id_reserva} cancelada.", "INFO")

    #este metodo devuelve una descripción completa de la reserva incluyendo cliente, servicio, fecha, cantidad, estado y costo total
    def obtener_descripcion(self) -> str:
        nombre_serv = self.servicio_asociado.nombre if self.servicio_asociado else self.codigo_servicio
        return (
            f"Reserva [{self.id_reserva}] | Cliente: {self.cliente.nombre} | "
            f"Servicio: {nombre_serv} | Fecha: {self.fecha} | "
            f"Cantidad: {self.cantidad} | Estado: {self.estado} | Total: ${self.costo_calculado:,.2f}"
        )

#esta clase gestiona todas las reservas, permitiendo agregar nuevas reservas y buscar reservas existentes por su código
class GestorReservas:
    def __init__(self):
        self._lista_reservas = []

    #con este metodo se agrega una nueva reserva al gestor, asegurando que no haya duplicados por código de reserva
    def agregar_reserva(self, reserva: Reserva) -> None:
        for r in self._lista_reservas:
            if r.id_reserva == reserva.id_reserva:
                raise ErrorSistemaFJ(f"Ya existe una reserva con el código {reserva.id_reserva}.")
        self._lista_reservas.append(reserva)
        registrar_en_log(f"Reserva {reserva.id_reserva} agregada al gestor.", "INFO")

    #con este metodo se busca una reserva por su código, devolviendo la reserva si se encuentra o lanzando una excepción si no
    def buscar_reserva(self, id_reserva: str) -> Reserva:
        codigo = str(id_reserva).strip().upper()
        for r in self._lista_reservas:
            if r.id_reserva == codigo:
                return r
        raise ErrorSistemaFJ(f"No se encontró ninguna reserva con el código {codigo}.")

    @property
    def reservas(self) -> list:
        return list(self._lista_reservas)

#este bloque inicializa el gestor de reservas para el sistema
gestor_reservas = GestorReservas()

#este metodo interactivo permite al usuario crear una nueva reserva solicitando los datos necesarios
def crear_reserva_interactiva(cliente_actual, codigo_serv: str) -> None:
    print("\n--- CREAR NUEVA RESERVA ---")
    id_res = input("Ingrese un código único para la reserva (ej. RES-01): ")
    fecha = input("Ingrese la fecha de la reserva (YYYY-MM-DD): ")
    cantidad = leer_entero("Ingrese la cantidad (horas o días según el servicio): ")

    if cantidad is None:
        raise ErrorSistemaFJ("La cantidad es obligatoria para la reserva.")

    nueva_reserva = Reserva(id_res, cliente_actual, codigo_serv, cantidad, fecha)
    nueva_reserva.confirmar()
    gestor_reservas.agregar_reserva(nueva_reserva)
    print("\n¡Reserva creada y confirmada con éxito!")
    print(f"  {nueva_reserva.obtener_descripcion()}")

#este metodo permite ver todas las reservas registradas en el sistema, mostrando su descripción completa
def ver_lista_reservas() -> None:
    print("\n--- LISTA DE RESERVAS REGISTRADAS ---")
    todas = gestor_reservas.reservas
    if not todas:
        print("No hay reservas registradas todavía.")
        return
    for i, res in enumerate(todas, 1):
        print(f"{i}. {res.obtener_descripcion()}")

#este metodo interactivo permite al usuario cambiar el estado de una reserva existente, ya sea procesándola o cancelándola
def cambiar_estado_reserva_interactivo() -> None:
    print("\n--- GESTIONAR ESTADO DE RESERVA ---")
    ver_lista_reservas()
    if not gestor_reservas.reservas:
        return

    codigo = input("\nIngrese el código de la reserva a gestionar: ")
    reserva = gestor_reservas.buscar_reserva(codigo)

    print(f"Estado actual: {reserva.estado}")
    print("1. Procesar reserva")
    print("2. Cancelar reserva")
    op = input("Seleccione una opción (1-2): ").strip()

    if op == "1":
        reserva.procesar()
        print(f"La reserva {reserva.id_reserva} ha sido PROCESADA.")
    elif op == "2":
        reserva.cancelar()
        print(f"La reserva {reserva.id_reserva} ha sido CANCELADA.")
    else:
        print("Opción inválida.")

#este metodo imprime el menú relacionado al modulo de reservas en consola
def menu_reservas(cliente_ejemplo) -> None:
    while True:
        print("\n==============================================")
        print("            MÓDULO DE RESERVAS                ")
        print("==============================================")
        print("1. Ver catálogo de servicios disponibles")
        print("2. Crear y confirmar una reserva")
        print("3. Ver listado de reservas")
        print("4. Procesar o cancelar una reserva")
        print("5. Volver al menú principal")
        print("==============================================")
        
        opcion = input("Selecciona una opción (1-5): ").strip()
        
        try:
            if opcion == "1":
                ver_catalogo()
            elif opcion == "2":
                ver_catalogo()
                codigo_s = input("\nIngrese el código exacto del servicio que desea reservar: ")
                crear_reserva_interactiva(cliente_ejemplo, codigo_s)
            elif opcion == "3":
                ver_lista_reservas()
            elif opcion == "4":
                cambiar_estado_reserva_interactivo()
            elif opcion == "5":
                print("\nVolviendo al menú principal...")
                break
            else:
                print("Opción inválida. Elija entre 1 y 5.")
                
        except ErrorSistemaFJ as error:
            print(f"\n[AVISO DE RESERVA]: {error}")
        except EOFError:
            print("\nEntrada finalizada. Volviendo al menú principal...")
            break
        except Exception as error:
            registrar_en_log(f"Fallo imprevisto en menú de reservas: {error}", "ERROR")
            print(f"\n[ERROR INESPERADO]: {error}")


# =========================================================================================================
# INTERFAZ DE CONSOLA (CLI) - MENÚ PRINCIPAL GLOBAL
# =========================================================================================================

#esta funcion imprime el menú principal del sistema en consola
def mostrar_menu_principal():
    print("\n==============================================")
    print("       SISTEMA DE GESTIÓN - SOFTWARE FJ       ")
    print("==============================================")
    print("1. Registrar nuevo cliente")
    print("2. Ver lista de clientes registrados")
    print("3. Gestionar servicios (Módulo 2)")
    print("4. Gestionar reservas (Módulo 3)")
    print("5. Salir del sistema")
    print("==============================================")

#esta funcion ejecuta la consola principal del sistema
#permitiendo al usuario interactuar con los módulos de clientes, servicios y reservas
def ejecutar_consola():
    gestor = GestorClientes()

    while True:
        mostrar_menu_principal()
        opcion = input("Selecciona una opción (1-5): ").strip()

        try:
            if opcion == "1":
                print("\n--- REGISTRO DE NUEVO CLIENTE ---")
                
                while True:
                    nombre = input("Nombre completo (o escribe 'salir'): ").strip()
                    if nombre.lower() == "salir":
                        print("Registro cancelado por el usuario.")
                        break
                    if not nombre:
                        print("[DATO INVÁLIDO]: El nombre no puede estar vacío. Intenta de nuevo.")
                        registrar_en_log("Intento de registro con nombre vacío.", "WARNING")
                        continue
                    break
                
                if nombre.lower() == "salir":
                    continue

                while True:
                    cedula = input("Cédula (mínimo 6 dígitos): ").strip()
                    if not cedula.isdigit() or len(cedula) < 6:
                        print("[DATO INVÁLIDO]: La cédula debe ser numérica de al menos 6 dígitos. Intenta de nuevo.")
                        registrar_en_log("Intento de registro con cédula inválida.", "WARNING")
                        continue
                    break

                while True:
                    correo = input("Correo electrónico: ").strip()
                    if not correo or "@" not in correo or "." not in correo:
                        print("[DATO INVÁLIDO]: El correo electrónico no tiene un formato válido. Intenta de nuevo.")
                        registrar_en_log("Intento de registro con correo inválido.", "WARNING")
                        continue
                    break

                try:
                    nuevo_cliente = Cliente(nombre, cedula, correo)
                    gestor.agregar_cliente(nuevo_cliente)
                    print("Cliente registrado con éxito en el sistema.")
                except ErrorSistemaFJ as e:
                    print(f"\n[AVISO DEL SISTEMA]: {e}")

            elif opcion == "2":
                print("\n--- CLIENTES REGISTRADOS EN MEMORIA ---")
                clientes = gestor.clientes
                if not clientes:
                    print("No hay clientes registrados todavía.")
                else:
                    for i, c in enumerate(clientes, 1):
                        print(f"{i}. Nombre: {c.nombre} | Cédula: {c.cedula} | Correo: {c.correo}")

            elif opcion == "3":
                # Abrimos el submenú interactivo del Módulo 2 de Mónica
                menu_servicios()

            elif opcion == "4":
                print("\n--- ACCESO AL MÓDULO DE RESERVAS ---")
                if not gestor.clientes:
                    print("[AVISO]: Debe registrar al menos un cliente antes de hacer una reserva.")
                    continue
                
                cedula_ingresada = input("Ingrese la cédula del cliente que va a reservar: ").strip()
                try:
                    cliente_encontrado = gestor.buscar_cliente_por_cedula(cedula_ingresada)
                    menu_reservas(cliente_encontrado)
                except ErrorSistemaFJ as e:
                    print(f"\n[AVISO]: {e}")

            elif opcion == "5":
                print("\n¡Gracias por usar Software FJ! Saliendo del sistema...")
                break
            else:
                print("Opción inválida. Por favor, elige un número del 1 al 5.")

        except ErrorSistemaFJ as e:
            print(f"\n[AVISO DEL SISTEMA]: {e}")
        except EOFError:
            print("\nEntrada finalizada. Saliendo del sistema...")
            break
        except Exception as e:
            print(f"\n[ERROR INESPERADO]: Ocurrió un fallo imprevisto: {e}")

#con este bloque se inicia la ejecución del sistema si el archivo es ejecutado directamente
if __name__ == "__main__":
    print("Iniciando entorno de ejecución para Software FJ...")
    try:
        ejecutar_consola()
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada finalizada. Saliendo del sistema...")
        