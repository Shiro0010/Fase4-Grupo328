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
#                                     ESPACIO PARA EL MODULO 2
#=========================================================================================================
"""Espacio destinado para la jerarquía de servicios y polimorfismo."""

"""en este espacio puedes empezar a redactar el codigo de este modulo, cree clases abstractas
y otras mas como base, puedes usarlas o corregirlas a tu gusto."""

class Servicio(ABC):
    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float):
        pass
    
    """Ocupamos Args y Kwargs para permitir flexibilidad en los parametros de entrada, esto es util
    cuando se tienen diferentes tipos de servicios con diferentes atributos, asi podemos pasar los
    parametros necesarios"""
    
    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        pass

    @abstractmethod
    def obtener_descripcion(self) -> str:
        pass


class SalaReunionServicio(Servicio):
    pass


class AlquilerEquipoServicio(Servicio):
    pass


class AsesoriaEspecializadaServicio(Servicio):
    pass


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
                print("\n[Módulo 2] Espacio reservado para servicios.")

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
