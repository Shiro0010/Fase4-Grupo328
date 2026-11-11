# para empezar, importamos las liberias necesarias
from abc import ABC, abstractmethod
import datetime
import os 


#=========================================================================================================
#                              Modulo LOG: CONFIGURACIÓN Y LOGS - Por Manuel Chaux 
#=========================================================================================================

def inicializar_archivo_log():
    """pendiente: esta funcion configurará y creará el archivo de registro de eventos."""
    pass

def registrar_en_log(mensaje: str, tipo: str = "INFO"):
    """pendiente: registrará los errores y sucesos con marca de tiempo en el archivo log"""
    pass


#=========================================================================================================
#                                     ESPACIO PARA EL MODULO 1 - Por Manuel Chaux x2
#=========================================================================================================
"""En esta sección daremos vida a las excepciones personalizadas y al sistema de gestión de clientes"""

# Clase padre de todas las excepciones personalizadas
class ErrorSistemaFJ(Exception):
    pass

class ClienteNoValidoException(ErrorSistemaFJ):
    pass
    
class ParametroFaltanteException(ErrorSistemaFJ):
    pass

class ServicioNoValidoException(ErrorSistemaFJ):
    pass

#Aun hay varias excepciones que se pueden crear, pero por ahora estas son las principales


# Esqueleto base para el Cliente (Atributos privados y encapsulación)
class Cliente:
    def __init__(self, nombre: str, cedula: str, correo: str):
        # TODO: Inicializar atributos privados
        pass

    """usamos -> para indicar el tipo de retorno de la funcion, en este caso un float, esto facilita
    a la hora de documentar y entender el codigo, pero no es obligatorio
    tambien apoya a la comprension del copilot."""
    
    @property
    def nombre(self) -> str:
        pass

    @property
    def cedula(self) -> str:
        pass

    @property
    def correo(self) -> str:
        pass

    def validar_cliente(self) -> bool:
        """Método pendiente para implementar validaciones y raise."""
        pass


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