# para empezar, importamos las librerias necesarias
from abc import ABC, abstractmethod
import datetime
import os 

#=========================================================================================================
#                              Modulo LOG: CONFIGURACIÓN Y LOGS - Por Manuel Chaux 
#=========================================================================================================
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
#con esto creamos el archivo log si no existe y escribimos el mapa de referencia de errores anterior.
def inicializar_archivo_log():
  """Configura y crea el archivo de registro de eventos con su mapa de referencia."""
  nombre_archivo = "registro_eventos.log"
  if not os.path.exists(nombre_archivo):
    try:
      with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(MAPA_CODIGOS_LOG.strip() + "\n\n")
    except Exception as e:
      print(f"[ERROR CRÍTICO]: No se pudo inicializar el archivo log: {e}")

#con esta funcion registramos los eventos en el archivo log, con fecha y hora, codigo de error y su tipo
def registrar_en_log(mensaje: str, tipo: str = "INFO"):
  """Registra los errores y sucesos con marca de tiempo en el archivo log

  de manera segura utilizando bloques try/except/finally.
  """
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
    # Bloque de estabilidad requerido para garantizar que el flujo no colapse
    pass

#=========================================================================================================
#                                     ESPACIO PARA EL MODULO 1 - Por Manuel Chaux x2
#=========================================================================================================

"""En esta sección daremos vida a las excepciones personalizadas y al sistema de gestión de clientes"""

# Clase padre de todas las excepciones personalizadas
class ErrorSistemaFJ(Exception):
  """Excepción base del sistema con formato y gravedad automática."""

  def __init__(self, mensaje: str, codigo: str = "ERR-000", nivel: str = "ERROR",):
      
    self.codigo = codigo
    self.nivel = nivel
    mensaje_completo = f"[{self.nivel}] ({self.codigo}): {mensaje}"
    super().__init__(mensaje_completo)


class ClienteNoValidoException(ErrorSistemaFJ):
  """Excepción para datos de cliente incorrectos o incompletos."""

  def __init__(
      self,
      mensaje: str = "Los datos del cliente no cumplen con el formato requerido.",
  ):
    super().__init__(mensaje, codigo="CLI-001", nivel="WARNING")


class ParametroFaltanteException(ErrorSistemaFJ):
  """Excepción para argumentos obligatorios ausentes en las funciones."""

  def __init__(
      self, mensaje: str = "Falta un argumento obligatorio en la operación."
  ):
    super().__init__(mensaje, codigo="SYS-002", nivel="ERROR")


class ServicioNoValidoException(ErrorSistemaFJ):
  """Excepción para servicios no disponibles o parámetros inválidos."""

  def __init__(
      self,
      mensaje: str = "El servicio solicitado no está disponible o es inválido.",
  ):
    super().__init__(mensaje, codigo="SRV-003", nivel="ERROR")

#Aun hay varias excepciones que se pueden crear, pero por ahora estas son las principales


# Creamos la clase cliente para gestionar los datos de los clientes y sus validaciones
class Cliente:
    
    def __init__(self, nombre: str, cedula: str, correo: str):
        
        #usamos el metodo de validacion para asegurarnos de que los datos son correctos.
        self.validar_datos_entrada(nombre, cedula, correo)
        
        self.__nombre = nombre.strip().title()
        self.__cedula = cedula.strip()
        self.__correo = correo.strip().lower()
        
        registrar_en_log(
            f"cliente creado exitosamente: {self.__correo}", "INFO"
        )
    
    def validar_datos_entrada(self, nombre:str, cedula:str, correo:str):
        #inspeccionamos y validamos los datos de entrada antes de instanciar
        if not nombre or not nombre.strip():
            
            registrar_en_log("Nombre de cliente inválido.", "WARNING")
            raise ClienteNoValidoException("El nombre del cliente no puede estar vacío.")         

        if not cedula or not cedula.isdigit() or len(cedula) < 6:
            
            registrar_en_log(f"cedula de cliente invalida: {cedula}.", "WARNING")
            raise ClienteNoValidoException("La cédula debe ser un número válido de al menos 6 dígitos.")
        
        if not correo or "@" not in correo or "." not in correo:
            
            registrar_en_log(f"correo de cliente invalido: {correo}.", "WARNING")
            raise ClienteNoValidoException("El correo electrónico no tiene un formato válido.")

    """usamos -> para indicar el tipo de retorno de la funcion, en este caso un float, esto facilita
    a la hora de documentar y entender el codigo, pero no es obligatorio
    tambien apoya a la comprension del copilot."""
    
    @property
    def nombre(self) -> str:
        
        #basicamente, esta es la unica forma de acceder a los atributos privados de la clase
        return self.__nombre

#viva la encapsulación, esto evita fugas de datos y controla el acceso a los atributos delicados
    @property
    def cedula(self) -> str:
        return self.__cedula

    @property
    def correo(self) -> str:
        return self.__correo

# ----------------------------------------------------------
# GESTOR MAESTRO DE CLIENTES EN MEMORIA
# ----------------------------------------------------------
"""lo llamamos maestro porque es el registro principal de clientes, y en memoria porque no usamos bases de datos
y al ser el almacen de los clientes pues, lo ocuparan todos los modulos seguramente."""

#En esta clase vamos a gestionar la lista de clientes, asegurando que no haya duplicados 
# y que se mantenga la integridad de los datos.
class GestorClientes:

  def __init__(self):
    # Lista privada para proteger los registros de modificaciones externas directas
    self.__lista_clientes = []

  def agregar_cliente(self, cliente: Cliente) -> None:
    """Inserta un cliente validado al registro maestro,

    verificando que no existan duplicados por cédula o correo.
    """
    for c in self.__lista_clientes:
      if c.cedula == cliente.cedula:
        registrar_en_log(
            f"Intento de duplicado bloqueado por cédula: {cliente.cedula}",
            "WARNING",
        )
        raise ClienteNoValidoException(
            "Ya existe un cliente registrado con esta cédula en el sistema."
        )

      if c.correo == cliente.correo:
        registrar_en_log(
            f"Intento de duplicado bloqueado por correo: {cliente.correo}",
            "WARNING",
        )
        raise ClienteNoValidoException(
            "Ya existe un cliente registrado con este correo en el sistema."
        )

    # Si pasa los filtros, se añade a la lista de clientes de forma segura y controlada
    self.__lista_clientes.append(cliente)
    
    registrar_en_log(
        f"Cliente con correo {cliente.correo} añadido con éxito al registro","INFO",)

  @property
  def clientes(self) -> list:
    """Permite consultar la lista de clientes de forma segura (solo lectura)."""
    return self.__lista_clientes



#=========================================================================================================
#                              MODULO 2 - SERVICIOS - Por Monica Ortega
#=========================================================================================================
"""Servicios de Software FJ: una clase abstracta (Servicio) y tres servicios que heredan de ella."""


class Servicio(ABC):
    """Clase abstracta: es el molde de todos los servicios.
    No se pueden crear objetos directamente de ella, solo de sus hijas."""

    IVA = 0.19  # impuesto, se usa cuando el cliente pide el costo con IVA

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float):
        # El código del servicio no puede estar vacío
        if id_servicio is None or str(id_servicio).strip() == "":
            registrar_en_log("Se intentó crear un servicio sin código.", "ERROR")
            raise ParametroFaltanteException("El servicio necesita un código.")

        # El nombre del servicio no puede estar vacío
        if nombre is None or str(nombre).strip() == "":
            registrar_en_log(f"El servicio {id_servicio} no tiene nombre.", "ERROR")
            raise ParametroFaltanteException("El servicio necesita un nombre.")

        # La tarifa debe poder convertirse en número
        try:
            tarifa_base = float(tarifa_base)
        except (TypeError, ValueError) as error:
            registrar_en_log(f"La tarifa del servicio {id_servicio} no es un número.", "ERROR")
        
            raise ServicioNoValidoException("La tarifa base debe ser un número.") from error

        # esta tarifa debe ser mayor a cero
        if tarifa_base <= 0:
            registrar_en_log(f"La tarifa del servicio {id_servicio} no es mayor que cero.", "ERROR")
            raise ServicioNoValidoException("La tarifa base debe ser mayor que cero.")

        self._id_servicio = str(id_servicio).strip().upper()
        self._nombre = str(nombre).strip()
        self._tarifa_base = tarifa_base
        self._disponible = True 

    # Propiedades: para leer los datos
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
        # El módulo de reservas usa esto para saber si el servicio se puede reservar
        return self._disponible

    def cambiar_disponibilidad(self, estado: bool) -> None:
        """Activa (True) o desactiva (False) el servicio y lo anota en el log."""
        self._disponible = estado
        if estado:
            registrar_en_log(f"El servicio {self._id_servicio} quedó disponible.", "INFO")
        else:
            registrar_en_log(f"El servicio {self._id_servicio} quedó NO disponible.", "INFO")

    def validar_parametros(self, cantidad=None, descuento=0) -> None:
        """Revisa lo que tienen en común todos los servicios.
        Las clases hijas la sobrescriben para agregar sus propios límites."""
        # La cantidad es obligatoria
        if cantidad is None:
            registrar_en_log(f"Falta la cantidad en el servicio {self._id_servicio}.", "ERROR")
            raise ParametroFaltanteException("Falta indicar la cantidad (horas o días).")

        # La cantidad debe ser un número entero mayor que cero
        if not isinstance(cantidad, int) or cantidad <= 0:
            registrar_en_log(f"Cantidad inválida en {self._id_servicio}: {cantidad}", "ERROR")
            raise ServicioNoValidoException("La cantidad debe ser un número entero mayor que cero.")

        
        if not self._disponible:
            registrar_en_log(f"Se intentó usar el servicio {self._id_servicio}, que no está disponible.", "ERROR")
            raise ServicioNoValidoException(f"El servicio '{self._nombre}' no está disponible.")

        # El descuento es un porcentaje: entre 0 y 100
        if descuento < 0 or descuento > 100:
            registrar_en_log(f"Descuento inválido en {self._id_servicio}: {descuento}", "ERROR")
            raise ServicioNoValidoException("El descuento debe estar entre 0 y 100.")

    def _aplicar_descuento_e_iva(self, subtotal: float, descuento: float, con_iva: bool) -> float:
        """Aplica al subtotal las dos variantes de cobro opcionales: descuento e IVA."""
        valor = subtotal - (subtotal * descuento / 100)  # primero se resta el descuento
        if con_iva:
            valor = valor * (1 + self.IVA)               # después se suma el IVA
        return round(valor, 2)                           # dejamos dos decimales

    """Usamos *args y **kwargs en los métodos abstractos para dejar libres los parámetros;
    cada servicio hijo define los suyos."""

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        pass

    @abstractmethod
    def obtener_descripcion(self) -> str:
        pass


class SalaReunionServicio(Servicio):
    """Servicio 1: reserva de salas. Se cobra por hora."""

    HORAS_MAXIMAS = 12         # máximo 12 horas por reserva
    HORAS_PARA_DESCUENTO = 4   # desde estas horas hay descuento por jornada
    DESCUENTO_JORNADA = 10     # porcentaje de ese descuento

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, capacidad: int):
        # La clase madre guarda y valida el código, el nombre y la tarifa
        super().__init__(id_servicio, nombre, tarifa_base)

        # La capacidad tiene que ser un entero mayor que cero
        if not isinstance(capacidad, int) or capacidad <= 0:
            registrar_en_log(f"Capacidad inválida en la sala {id_servicio}: {capacidad}", "ERROR")
            raise ServicioNoValidoException("La capacidad de la sala debe ser un entero mayor que cero.")
        self._capacidad = capacidad

    def validar_parametros(self, cantidad=None, descuento=0) -> None:
        # Primero las reglas comunes de la clase madre
        super().validar_parametros(cantidad, descuento)
        # Después la regla propia de las salas
        if cantidad > self.HORAS_MAXIMAS:
            registrar_en_log(f"Sala {self._id_servicio}: {cantidad} horas es demasiado.", "ERROR")
            raise ServicioNoValidoException(f"Una sala se reserva máximo {self.HORAS_MAXIMAS} horas.")

    def calcular_costo(self, cantidad=None, descuento=0, con_iva=False) -> float:
        """Costo de la sala (cantidad = horas). Se puede llamar de tres formas:
            calcular_costo(4)            -> solo las horas
            calcular_costo(4, 10)        -> horas con 10 % de descuento
            calcular_costo(4, 10, True)  -> horas, descuento e IVA"""
        self.validar_parametros(cantidad, descuento)
        subtotal = self._tarifa_base * cantidad  # tarifa por hora
        # Regla propia de las salas: descuento por jornada larga
        if cantidad >= self.HORAS_PARA_DESCUENTO:
            subtotal = subtotal - (subtotal * self.DESCUENTO_JORNADA / 100)
        return self._aplicar_descuento_e_iva(subtotal, descuento, con_iva)

    def obtener_descripcion(self) -> str:
        return (f"Sala '{self._nombre}' ({self._id_servicio}) - capacidad: {self._capacidad} personas - "
                f"${self._tarifa_base:,.0f} por hora")


class AlquilerEquipoServicio(Servicio):
    """Servicio 2: alquiler de equipos informáticos o de oficina. Se cobra por día."""

    TIPOS_VALIDOS = ("informatico", "oficina")  # tipos de equipo permitidos
    DIAS_MAXIMOS = 30                         
    SEGURO = 5                                  # porcentaje de seguro que se suma

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, tipo_equipo: str):
        super().__init__(id_servicio, nombre, tarifa_base)

        # El tipo de equipo tiene que ser uno de los permitidos
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
        """Costo del alquiler (cantidad = días). El descuento y el IVA son opcionales."""
        self.validar_parametros(cantidad, descuento)
        subtotal = self._tarifa_base * cantidad                 # tarifa por día x días
        subtotal = subtotal + (subtotal * self.SEGURO / 100)    # regla propia: se suma el seguro
        return self._aplicar_descuento_e_iva(subtotal, descuento, con_iva)

    def obtener_descripcion(self) -> str:
        return (f"Equipo {self._tipo_equipo} '{self._nombre}' ({self._id_servicio}) - "
                f"${self._tarifa_base:,.0f} por día más {self.SEGURO} % de seguro")


class AsesoriaEspecializadaServicio(Servicio):
    """Servicio 3: asesorías técnicas. Los honorarios se cobran por hora según el nivel del asesor."""

    NIVELES = {"junior": 1.0, "senior": 1.5}  
    HORAS_MAXIMAS = 8                        

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, especialidad: str, nivel: str = "junior"):
        super().__init__(id_servicio, nombre, tarifa_base)

        # La especialidad no puede estar vacía
        if especialidad is None or str(especialidad).strip() == "":
            registrar_en_log(f"La asesoría {id_servicio} no tiene especialidad.", "ERROR")
            raise ParametroFaltanteException("La asesoría necesita una especialidad.")

        # El nivel tiene que ser junior o senior
        nivel_limpio = str(nivel).strip().lower()
        if nivel_limpio not in self.NIVELES:
            registrar_en_log(f"Nivel inválido en la asesoría {id_servicio}: {nivel}", "ERROR")
            raise ServicioNoValidoException("El nivel del asesor debe ser 'junior' o 'senior'.")

        self._especialidad = str(especialidad).strip()
        self._nivel = nivel_limpio

    def validar_parametros(self, cantidad=None, descuento=0) -> None:
        super().validar_parametros(cantidad, descuento)
        if cantidad > self.HORAS_MAXIMAS:
            registrar_en_log(f"Asesoría {self._id_servicio}: {cantidad} horas es demasiado.", "ERROR")
            raise ServicioNoValidoException(f"Una asesoría dura máximo {self.HORAS_MAXIMAS} horas.")

    def calcular_costo(self, cantidad=None, descuento=0, con_iva=False) -> float:
        """Honorarios de la asesoría (cantidad = horas). El descuento y el IVA son opcionales."""
        self.validar_parametros(cantidad, descuento)
        multiplicador = self.NIVELES[self._nivel]                  # junior = 1.0, senior = 1.5
        subtotal = self._tarifa_base * cantidad * multiplicador   
        return self._aplicar_descuento_e_iva(subtotal, descuento, con_iva)

    def obtener_descripcion(self) -> str:
        return (f"Asesoría en {self._especialidad} '{self._nombre}' ({self._id_servicio}) - "
                f"asesor {self._nivel} - ${self._tarifa_base:,.0f} por hora base")


# ----------------------------------------------------------
# FUNCIONES DE APOYO DEL MODULO 2
# ----------------------------------------------------------

def calcular_costo_seguro(servicio, cantidad=None, descuento=0, con_iva=False) -> float:
    """Calcula el costo de un servicio sin que el programa se caiga.
    El módulo de reservas puede usarla así: calcular_costo_seguro(servicio, duracion)"""
    try:
        # poliformismo
        costo = servicio.calcular_costo(cantidad, descuento, con_iva)
    except ErrorSistemaFJ:
    
        raise
    except (TypeError, ValueError, AttributeError) as error:
        # Error inesperado de Python: lo anotamos y lo convertimos en un error del sistema
        registrar_en_log(f"Fallo inesperado al calcular el costo: {error}", "ERROR")
        raise ServicioNoValidoException("No se pudo calcular el costo del servicio.") from error
    else:
        # Esto solo corre si no hubo errores
        registrar_en_log(f"Costo calculado para {servicio.id_servicio}: ${costo:,.2f}", "INFO")
        return costo
    finally:
    
        registrar_en_log("Fin del intento de cálculo de costo.", "INFO")


def crear_catalogo_servicios() -> list:
    """Crea una lista con un ejemplo de cada servicio."""
    return [
        SalaReunionServicio("SAL-01", "Sala Ejecutiva", 50000, 10),
        AlquilerEquipoServicio("EQU-01", "Portatil Profesional", 40000, "informatico"),
        AsesoriaEspecializadaServicio("ASE-01", "Ciberseguridad", 120000, "Ciberseguridad", "senior"),
    ]


def probar_costo(titulo, servicio, cantidad=None, descuento=0, con_iva=False) -> None:
    """Prueba un cálculo de costo. Si falla, muestra el error y el programa sigue."""
    try:
        costo = calcular_costo_seguro(servicio, cantidad, descuento, con_iva)
        print(f"  [OK] {titulo}: ${costo:,.2f}")
    except ErrorSistemaFJ as error:
        print(f"  [ERROR CONTROLADO] {titulo}: {error}")


def simular_servicios() -> None:
    """Demostración del Módulo 2 con casos correctos e incorrectos."""
    print("\n--- SIMULACIÓN DE SERVICIOS ---")
    sala, equipo, asesoria = crear_catalogo_servicios()

    print("\nDescripciones (la misma llamada, cada servicio responde distinto):")
    for servicio in [sala, equipo, asesoria]:
        print(f"  - {servicio.obtener_descripcion()}")

    print("\nCasos correctos:")
    probar_costo("Sala por 5 horas", sala, 5)
    probar_costo("Equipo por 3 días", equipo, 3)
    probar_costo("Asesoría 2 horas con 15 % de descuento e IVA", asesoria, 2, 15, True)

    print("\nCasos con error (el sistema los atrapa y sigue funcionando):")
    try:
        SalaReunionServicio("SAL-02", "Sala Pequena", -100, 4)
    except ErrorSistemaFJ as error:
        print(f"  [ERROR CONTROLADO] Crear sala con tarifa negativa: {error}")

    try:
        AlquilerEquipoServicio("EQU-02", "Cafetera", 5000, "cafetera")
    except ErrorSistemaFJ as error:
        print(f"  [ERROR CONTROLADO] Crear equipo de tipo cafetera: {error}")

    probar_costo("Sala por 15 horas", sala, 15)
    probar_costo("Sala sin indicar las horas", sala)
    probar_costo("Equipo con descuento de 150 %", equipo, 2, 150)
    probar_costo("Calcular sobre algo que no es un servicio", None, 2)

    print("\nServicio no disponible:")
    asesoria.cambiar_disponibilidad(False)
    probar_costo("Asesoría desactivada", asesoria, 2)
    asesoria.cambiar_disponibilidad(True)
    probar_costo("Asesoría activada otra vez", asesoria, 2)

    print("\nRevisa el archivo registro_eventos.log: ahí quedó el detalle de cada caso.")

#=========================================================================================================
#                                     ESPACIO PARA EL MODULO 3
#=========================================================================================================
"""Espacio destinado para la gestión de reservas y control de estados."""

"""en este espacio puedes empezar a redactar el codigo de este modulo, cree clases abstractas
y otras mas como base, puedes usarlas o corregirlas a tu gusto."""

class Reserva:
    def __init__(self, cliente, servicio, duracion: int):
        pass

    def confirmar_reserva(self):
        pass

    def cancelar_reserva(self):
        pass



# ==========================================================
# INTERFAZ DE CONSOLA (CLI) - SOFTWARE FJ
# ==========================================================

def mostrar_menu_principal():
    print("\n==============================================")
    print("       SISTEMA DE GESTIÓN - SOFTWARE FJ       ")
    print("==============================================")
    print("1. Registrar nuevo cliente")
    print("2. Ver lista de clientes registrados")
    print("3. Simular servicios (Módulo 2)")
    print("4. Gestionar reservas (Módulo 3)")
    print("5. Salir del sistema")
    print("==============================================")


# ==========================================================
# INTERFAZ DE CONSOLA (CLI) - CAMPO POR CAMPO
# ==========================================================

def ejecutar_consola():
    gestor = GestorClientes()

    while True:
        mostrar_menu_principal()
        opcion = input("Selecciona una opción (1-5): ").strip()

        try:
            if opcion == "1":
                print("\n--- REGISTRO DE NUEVO CLIENTE ---")
                
                # Validación individual para el nombre
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

                # Validación individual para la cédula con reintento estricto
                while True:
                    cedula = input("Cédula (mínimo 6 dígitos): ").strip()
                    if not cedula.isdigit() or len(cedula) < 6:
                        print("[DATO INVÁLIDO]: La cédula debe ser numérica de al menos 6 dígitos. Intenta de nuevo.")
                        registrar_en_log("Intento de registro con cédula inválida.", "WARNING")
                        continue
                    break

                # Validación individual para el correo con reintento estricto
                while True:
                    correo = input("Correo electrónico: ").strip()
                    if not correo or "@" not in correo or "." not in correo:
                        print("[DATO INVÁLIDO]: El correo electrónico no tiene un formato válido. Intenta de nuevo.")
                        registrar_en_log("Intento de registro con correo inválido.", "WARNING")
                        continue
                    break

                # Una vez que cada campo pasó su propio filtro, instanciamos y guardamos de forma segura
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
                simular_servicios()

            elif opcion == "4":
                print("\n[Módulo 3] Espacio reservado para reservas.")

            elif opcion == "5":
                print("\n¡Gracias por usar Software FJ! Saliendo del sistema...")
                break
            else:
                print("Opción inválida. Por favor, elige un número del 1 al 5.")

        except ErrorSistemaFJ as e:
            print(f"\n[AVISO DEL SISTEMA]: {e}")
        except Exception as e:
            print(f"\n[ERROR INESPERADO]: Ocurrió un fallo imprevisto: {e}")
            
if __name__ == "__main__":
    print("Iniciando entorno de ejecución para Software FJ...")
    ejecutar_consola()
