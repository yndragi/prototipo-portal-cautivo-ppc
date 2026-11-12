from models import Anunciante, Anuncio, UsuarioPortal, PortalCautivo


def ejecutar_corrido_en_frio():
    print("=" * 65)
    print("SIMULACIÓN DE CORRIDO EN FRÍO (PRUEBA DE ESCRITORIO) - MODELO PPC")
    print("=" * 65)

    portal = PortalCautivo()
    anunciante = Anunciante("ANC-01", "Besha Boutique", "ventas@besha.com", saldo_inicial=1.00)
    anuncio = Anuncio("AD-101", anunciante, "Promo Moda 2026", "Descuentos", cpc=0.50, url_destino="https://besha.com")

    portal.registrar_anunciante(anunciante)
    portal.agregar_anuncio(anuncio)

    u1 = UsuarioPortal("usr_001", "usr_001", "1234", "192.168.1.50")
    u2 = UsuarioPortal("usr_002", "usr_002", "1234", "192.168.1.75")
    u3 = UsuarioPortal("usr_003", "usr_003", "1234", "192.168.1.90")

    portal.registrar_usuario(u1)
    portal.registrar_usuario(u2)
    portal.registrar_usuario(u3)

    print(f"Estado Inicial -> Saldo: ${anunciante.consultar_saldo():.2f} | CPC: ${anuncio.cpc:.2f} | Clics: {anuncio.clicks_totales}\n")

    escenarios = [
        ("Iteración 1 (Primer Clic Válido)", "AD-101", "usr_001", "192.168.1.50"),
        ("Iteración 2 (Segundo Clic Válido)", "AD-101", "usr_002", "192.168.1.75"),
        ("Iteración 3 (Saldo Agotado)", "AD-101", "usr_003", "192.168.1.90"),
    ]

    for titulo, id_ad, id_usr, ip in escenarios:
        print(f"--- {titulo} ---")
        res = portal.procesar_clic_anuncio(id_ad, id_usr, ip)
        print(f"Entrada : id_anuncio={id_ad}, id_usuario={id_usr}, ip={ip}")
        print(f"Salida  : {res}\n")


if __name__ == "__main__":
    ejecutar_corrido_en_frio()
