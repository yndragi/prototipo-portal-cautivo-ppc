from datetime import datetime


class Anunciante:
    """Representa a la empresa o persona que contrata publicidad en el portal."""

    def __init__(self, id_anunciante: str, nombre: str, email: str, saldo_inicial: float):
        self.id_anunciante = id_anunciante
        self.nombre = nombre
        self.email = email
        self.saldo = float(saldo_inicial)

    def recargar_saldo(self, monto: float) -> float:
        if monto <= 0:
            raise ValueError("El monto de recarga debe ser mayor a cero.")
        self.saldo = round(self.saldo + monto, 2)
        return self.saldo

    def consultar_saldo(self) -> float:
        return round(self.saldo, 2)

    def to_dict(self) -> dict:
        return {
            "id_anunciante": self.id_anunciante,
            "nombre": self.nombre,
            "email": self.email,
            "saldo": self.consultar_saldo(),
        }


class Anuncio:
    """Modela un banner publicitario bajo el esquema de Pago por Clic (PPC)."""

    def __init__(
        self,
        id_anuncio: str,
        anunciante: Anunciante,
        titulo: str,
        descripcion: str,
        cpc: float,
        url_destino: str,
        ubicacion: str = "login",  # 'login' (antes) o 'post_auth' (después de autenticar)
        etiqueta: str = "Destacado"
    ):
        self.id_anuncio = id_anuncio
        self.anunciante = anunciante
        self.titulo = titulo
        self.descripcion = descripcion
        self.cpc = float(cpc)
        self.url_destino = url_destino
        self.ubicacion = ubicacion
        self.etiqueta = etiqueta
        self.impresiones = 0
        self.clicks_totales = 0
        self.activo = True

    def registrar_impresion(self):
        if self.esta_disponible():
            self.impresiones += 1

    def esta_disponible(self) -> bool:
        return self.activo and (self.anunciante.saldo >= self.cpc)

    def calcular_ctr(self) -> float:
        if self.impresiones == 0:
            return 0.0
        return round((self.clicks_totales / self.impresiones) * 100, 2)

    def to_dict(self) -> dict:
        return {
            "id_anuncio": self.id_anuncio,
            "anunciante": self.anunciante.nombre,
            "id_anunciante": self.anunciante.id_anunciante,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "cpc": self.cpc,
            "url_destino": self.url_destino,
            "ubicacion": self.ubicacion,
            "etiqueta": self.etiqueta,
            "impresiones": self.impresiones,
            "clicks_totales": self.clicks_totales,
            "ctr": self.calcular_ctr(),
            "disponible": self.esta_disponible(),
            "saldo_anunciante": self.anunciante.consultar_saldo(),
        }


class UsuarioPortal:
    """Representa al cliente de la red que solicita acceso a Internet."""

    def __init__(self, id_usuario: str, username: str, password: str, ip_address: str):
        self.id_usuario = id_usuario
        self.username = username
        self._password = password
        self.ip_address = ip_address
        self.autenticado = False
        self.acceso_internet = False
        self.metodo_acceso = None

    def autenticar(self, password_ingresado: str) -> bool:
        if self._password == password_ingresado:
            self.autenticado = True
            self.conceder_acceso("Credenciales")
            return True
        return False

    def conceder_acceso(self, metodo: str):
        self.acceso_internet = True
        self.metodo_acceso = metodo


class TransaccionClic:
    """Registro de auditoría por cada clic validado y cobrado."""

    def __init__(self, id_transaccion: str, id_anuncio: str, titulo_anuncio: str, id_usuario: str, ip_origen: str, monto_cpc: float):
        self.id_transaccion = id_transaccion
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.id_anuncio = id_anuncio
        self.titulo_anuncio = titulo_anuncio
        self.id_usuario = id_usuario
        self.ip_origen = ip_origen
        self.monto_cpc = monto_cpc

    def to_dict(self) -> dict:
        return {
            "id_transaccion": self.id_transaccion,
            "timestamp": self.timestamp,
            "id_anuncio": self.id_anuncio,
            "titulo_anuncio": self.titulo_anuncio,
            "id_usuario": self.id_usuario,
            "ip_origen": self.ip_origen,
            "monto_cpc": round(self.monto_cpc, 2),
        }


class PortalCautivo:
    """Controlador central que gestiona anuncios, sesiones, autenticación y cobros PPC."""

    def __init__(self, nombre_red: str = "WiFi-Publico-Libre"):
        self.nombre_red = nombre_red
        self.anunciantes: dict[str, Anunciante] = {}
        self.anuncios: dict[str, Anuncio] = {}
        self.usuarios: dict[str, UsuarioPortal] = {}
        self.historial_clics: list[TransaccionClic] = []
        self.ingresos_red_totales: float = 0.0

    def registrar_anunciante(self, anunciante: Anunciante):
        self.anunciantes[anunciante.id_anunciante] = anunciante

    def agregar_anuncio(self, anuncio: Anuncio):
        self.anuncios[anuncio.id_anuncio] = anuncio

    def registrar_usuario(self, usuario: UsuarioPortal):
        self.usuarios[usuario.username] = usuario

    def obtener_anuncios_activos(self, ubicacion: str = None) -> list[Anuncio]:
        resultado = []
        for anuncio in self.anuncios.values():
            if anuncio.esta_disponible():
                if ubicacion is None or anuncio.ubicacion == ubicacion:
                    anuncio.registrar_impresion()
                    resultado.append(anuncio)
        return resultado

    def procesar_clic_anuncio(self, id_anuncio: str, id_usuario: str, ip_origen: str) -> dict:
        """
        Función principal del sistema:
        - Entrada: id_anuncio, id_usuario, ip_origen
        - Proceso: valida saldo del anunciante, descuenta CPC, registra auditoría y habilita internet
        - Salida: diccionario con resultado de transacción, nuevo saldo y estado de acceso
        """
        if id_anuncio not in self.anuncios:
            return {"status": "error", "transaccion": "Anuncio_No_Encontrado"}

        anuncio = self.anuncios[id_anuncio]

        if anuncio.esta_disponible():
            anuncio.anunciante.saldo = round(anuncio.anunciante.saldo - anuncio.cpc, 2)
            anuncio.clicks_totales += 1
            self.ingresos_red_totales = round(self.ingresos_red_totales + anuncio.cpc, 2)

            usuario = self.usuarios.get(id_usuario)
            if usuario:
                usuario.conceder_acceso("Clic_Publicitario")

            tx_id = f"TX-{len(self.historial_clics) + 1:04d}"
            tx = TransaccionClic(
                id_transaccion=tx_id,
                id_anuncio=anuncio.id_anuncio,
                titulo_anuncio=anuncio.titulo,
                id_usuario=id_usuario,
                ip_origen=ip_origen,
                monto_cpc=anuncio.cpc,
            )
            self.historial_clics.insert(0, tx)

            return {
                "status": "ok",
                "transaccion": "Aprobado",
                "id_transaccion": tx_id,
                "id_anuncio": anuncio.id_anuncio,
                "url_destino": anuncio.url_destino,
                "nuevo_saldo_anunciante": anuncio.anunciante.consultar_saldo(),
                "clics_totales": anuncio.clicks_totales,
                "acceso_internet": "Autorizado",
            }
        else:
            return {
                "status": "denied",
                "transaccion": "Rechazado_Sin_Fondos",
                "id_anuncio": anuncio.id_anuncio,
                "nuevo_saldo_anunciante": anuncio.anunciante.consultar_saldo(),
                "clics_totales": anuncio.clicks_totales,
                "acceso_internet": "Denegado",
            }
