
class Reserva:
    """Clase que conecta un Cliente con un Servicio utilizando los gestores 
    del Módulo 2 de manera segura."""

    def __init__(self, id_reserva: str, cliente, codigo_servicio: str, cantidad: int, fecha: str):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.codigo_servicio = codigo_servicio
        self.cantidad = cantidad
        self.fecha = fecha
        self.estado = "Pendiente"  # Estados: Pendiente, Confirmada, Procesada, Cancelada
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

    def validar_y_preparar(self) -> None:
        """Busca el servicio en el gestor de la compañera, valida su disponibilidad 
        y calcula el costo de forma segura."""
        
        # 1. Buscar el servicio usando el gestor del Módulo 2
        # (Se asume que 'gestor_servicios' está importado desde el módulo de servicios)
        self.servicio_asociado = gestor_servicios.buscar_servicio(self.codigo_servicio)
        
        # 2. Validar obligatoriamente si el servicio está disponible
        if not self.servicio_asociado.disponible:
            registrar_en_log(f"Intento de reservar servicio no disponible: {self.codigo_servicio}", "WARNING")
            raise ErrorSistemaFJ(f"El servicio '{self.servicio_asociado.nombre}' no se encuentra disponible para reservas.")
        
        # 3. Calcular el costo usando la función segura provista por el Módulo 2
        try:
            # Llamamos a calcular_costo_seguro provista en el módulo 2
            self.costo_calculado = calcular_costo_seguro(self.servicio_asociado, self.cantidad)
            registrar_en_log(f"Costo calculado con éxito para la reserva {self.id_reserva}: ${self.costo_calculado}", "INFO")
        except Exception as error:
            registrar_en_log(f"Fallo al calcular costo en reserva {self.id_reserva}: {error}", "ERROR")
            raise ErrorSistemaFJ(f"No fue posible calcular el costo del servicio: {error}") from error

    def confirmar(self) -> None:
        """Confirma la reserva ejecutando previamente las validaciones del servicio."""
        if self.estado == "Cancelada":
            raise ErrorSistemaFJ("No se puede confirmar una reserva que ya ha sido cancelada.")
        if self.estado == "Confirmada":
            raise ErrorSistemaFJ("La reserva ya se encuentra confirmada.")
        
        # Ejecuta validación y cálculo de costo al momento de confirmar
        self.validar_y_preparar()
        self.estado = "Confirmada"
        registrar_en_log(f"Reserva {self.id_reserva} confirmada para el cliente {self.cliente.nombre}.", "INFO")

    def procesar(self) -> None:
        """Procesa una reserva que obligatoriamente esté confirmada."""
        if self.estado != "Confirmada":
            registrar_en_log(f"Intento de procesar reserva {self.id_reserva} en estado inválido: {self.estado}", "WARNING")
            raise ErrorSistemaFJ(f"No se puede procesar la reserva. Su estado actual es '{self.estado}' y debe estar 'Confirmada'.")
        
        self.estado = "Procesada"
        registrar_en_log(f"Reserva {self.id_reserva} procesada exitosamente.", "INFO")

    def cancelar(self) -> None:
        """Cancela la reserva si no ha sido procesada."""
        if self.estado == "Procesada":
            raise ErrorSistemaFJ("No se puede cancelar una reserva que ya fue procesada.")
        
        self.estado = "Cancelada"
        registrar_en_log(f"Reserva {self.id_reserva} cancelada.", "INFO")

    def obtener_descripcion(self) -> str:
        nombre_serv = self.servicio_asociado.nombre if self.servicio_asociado else self.codigo_servicio
        return (
            f"Reserva [{self.id_reserva}] | Cliente: {self.cliente.nombre} | "
            f"Servicio: {nombre_serv} | Fecha: {self.fecha} | "
            f"Cantidad: {self.cantidad} | Estado: {self.estado} | Total: ${self.costo_calculado:,.2f}"
        )


class GestorReservas:
    """Administra la lista de reservas en memoria para el módulo 3."""

    def __init__(self):
        self._lista_reservas = []

    def agregar_reserva(self, reserva: Reserva) -> None:
        for r in self._lista_reservas:
            if r.id_reserva == reserva.id_reserva:
                raise ErrorSistemaFJ(f"Ya existe una reserva con el código {reserva.id_reserva}.")
        self._lista_reservas.append(reserva)
        registrar_en_log(f"Reserva {reserva.id_reserva} agregada al gestor.", "INFO")

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        codigo = str(id_reserva).strip().upper()
        for r in self._lista_reservas:
            if r.id_reserva == codigo:
                return r
        raise ErrorSistemaFJ(f"No se encontró ninguna reserva con el código {codigo}.")

    @property
    def reservas(self) -> list:
        return list(self._lista_reservas)


# Instancia global del gestor de reservas
gestor_reservas = GestorReservas()


# ==========================================================
# OPCIONES INTERACTIVAS DEL MÓDULO DE RESERVAS
# ==========================================================

def crear_reserva_interactiva(cliente_actual, codigo_serv: str) -> None:
    """Crea una reserva interactiva conectando cliente y el servicio de la compañera."""
    print("\n--- CREAR NUEVA RESERVA ---")
    id_res = input("Ingrese un código único para la reserva (ej. RES-01): ")
    fecha = input("Ingrese la fecha de la reserva (YYYY-MM-DD): ")
    cantidad = leer_entero("Ingrese la cantidad (horas o días según el servicio): ")

    if cantidad is None:
        raise ErrorSistemaFJ("La cantidad es obligatoria para la reserva.")

    # Instanciamos la reserva
    nueva_reserva = Reserva(id_res, cliente_actual, codigo_serv, cantidad, fecha)
    
    # Intentamos confirmar (lo que validará el servicio y calculará el costo de inmediato)
    nueva_reserva.confirmar()
    
    # Agregamos al gestor de reservas
    gestor_reservas.agregar_reserva(nueva_reserva)
    print("\n¡Reserva creada y confirmada con éxito!")
    print(f"  {nueva_reserva.obtener_descripcion()}")


def ver_lista_reservas() -> None:
    """Muestra todas las reservas del sistema."""
    print("\n--- LISTA DE RESERVAS REGISTRADAS ---")
    todas = gestor_reservas.reservas
    if not todas:
        print("No hay reservas registradas todavía.")
        return
    for i, res in enumerate(todas, 1):
        print(f"{i}. {res.obtener_descripcion()}")


def cambiar_estado_reserva_interactivo() -> None:
    """Permite procesar o cancelar una reserva existente."""
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


# ==========================================================
# MENÚ DEL MÓDULO DE RESERVAS
# ==========================================================
def menu_reservas(cliente_ejemplo) -> None:
    """Menú propio del módulo de reservas."""
    while True:
        print("\n==============================================")
        print("            MÓDULO DE RESERVAS                ")
        print("==============================================")
        print("1. Ver catálogo de servicios disponibles (Módulo 2)")
        print("2. Crear y confirmar una reserva")
        print("3. Ver listado de reservas")
        print("4. Procesar o cancelar una reserva")
        print("5. Volver al menú principal")
        print("==============================================")
        
        opcion = input("Selecciona una opción (1-5): ").strip()
        
        try:
            if opcion == "1":
                # Usamos la función del módulo de tu compañera de forma limpia
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
        except Exception as error:
            registrar_en_log(f"Fallo imprevisto en menú de reservas: {error}", "ERROR")
            print(f"\n[ERROR INESPERADO]: {error}")
