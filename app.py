from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import Anunciante, Anuncio, UsuarioPortal, PortalCautivo

app = Flask(__name__)
app.secret_key = "clave_secreta_portal_cautivo_2026"

# Inicialización del sistema con datos de prueba
portal = PortalCautivo(nombre_red="WiFi · Red Inteligente")

anunciante_1 = Anunciante("ANC-01", "Besha Boutique", "@boutique_besha", 15.00)
anunciante_2 = Anunciante("ANC-02", "TechStore Caracas", "@techstore.ve", 8.50)

portal.registrar_anunciante(anunciante_1)
portal.registrar_anunciante(anunciante_2)

anuncio_1 = Anuncio(
    id_anuncio="AD-101",
    anunciante=anunciante_1,
    titulo="Besha Boutique · Colección Exclusiva 2026",
    descripcion="Obtén 20% de descuento en conjuntos y accesorios minimalistas al conectarte.",
    cpc=0.50,
    url_destino="https://www.instagram.com/boutique_besha/",
    ubicacion="login",
    etiqueta="Patrocinado · Acceso Gratis"
)

anuncio_2 = Anuncio(
    id_anuncio="AD-102",
    anunciante=anunciante_2,
    titulo="TechStore Caracas · Equipos & Redes",
    descripcion="Equipos tecnológicos con envío en toda Caracas.",
    cpc=0.75,
    url_destino="https://example.com/techstore",
    ubicacion="post_auth",
    etiqueta="Oferta Verificada"
)

portal.agregar_anuncio(anuncio_1)
portal.agregar_anuncio(anuncio_2)

# Usuarios de prueba
portal.registrar_usuario(UsuarioPortal("USR-001", "invitado", "1234", "192.168.1.50"))
portal.registrar_usuario(UsuarioPortal("USR-002", "estudiante", "2026", "192.168.1.75"))


@app.route("/")
def index():
    """Pantalla 1: Interfaz de Usuario (Portal Cautivo con Banner)."""
    anuncios_login = portal.obtener_anuncios_activos(ubicacion="login")
    anuncios_post = portal.obtener_anuncios_activos(ubicacion="post_auth")
    usuario_actual = session.get("usuario")
    acceso = session.get("acceso_internet", False)
    mensaje = request.args.get("mensaje")
    tipo_alerta = request.args.get("tipo", "info")
    return render_template(
        "index.html",
        red=portal.nombre_red,
        anuncios_login=anuncios_login,
        anuncios_post=anuncios_post,
        usuario=usuario_actual,
        acceso=acceso,
        mensaje=mensaje,
        tipo_alerta=tipo_alerta,
        active_page="portal"
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    ip_origen = request.remote_addr or "192.168.1.100"

    usuario = portal.usuarios.get(username)
    if usuario and usuario.autenticar(password):
        session["usuario"] = usuario.username
        session["acceso_internet"] = True
        return redirect(url_for("index", mensaje="Autenticación verificada. ¡Ya tienes navegación ilimitada!", tipo="success"))

    if username and password == "1234":
        nuevo_usr = UsuarioPortal(f"USR-{len(portal.usuarios)+1:03d}", username, password, ip_origen)
        nuevo_usr.autenticar(password)
        portal.registrar_usuario(nuevo_usr)
        session["usuario"] = username
        session["acceso_internet"] = True
        return redirect(url_for("index", mensaje=f"Bienvenido {username}. Acceso a Internet habilitado.", tipo="success"))

    return redirect(url_for("index", mensaje="Credenciales incorrectas. Prueba con usuario: invitado / clave: 1234", tipo="error"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index", mensaje="Sesión finalizada. Autentícate o haz clic en un anuncio para volver a conectarte.", tipo="info"))


@app.route("/clic/<id_anuncio>")
def registrar_clic(id_anuncio):
    """Procesa el clic en el banner, cobra al anunciante y habilita internet."""
    id_usuario = session.get("usuario", "visitante_wifi")
    ip_origen = request.remote_addr or "192.168.1.50"

    resultado = portal.procesar_clic_anuncio(id_anuncio, id_usuario, ip_origen)

    if resultado["status"] == "ok":
        session["usuario"] = id_usuario
        session["acceso_internet"] = True
        cpc_cobrado = portal.anuncios[id_anuncio].cpc
        return redirect(
            url_for(
                "index",
                mensaje=f"¡Clic validado ({resultado['id_transaccion']})! Se cobró ${cpc_cobrado:.2f} USD al anunciante y se desbloqueó tu acceso a Internet.",
                tipo="success"
            )
        )
    return redirect(url_for("index", mensaje=f"No se pudo procesar el anuncio: {resultado['transaccion']}", tipo="error"))


@app.route("/dashboard")
def dashboard():
    """Pantalla 2: Dashboard del Anunciante."""
    anunciantes = [a.to_dict() for a in portal.anunciantes.values()]
    anuncios = [a.to_dict() for a in portal.anuncios.values()]
    total_clics = sum(a.clicks_totales for a in portal.anuncios.values())
    total_impresiones = sum(a.impresiones for a in portal.anuncios.values())
    ctr_global = round((total_clics / total_impresiones * 100), 2) if total_impresiones > 0 else 0.0
    return render_template(
        "dashboard.html",
        anunciantes=anunciantes,
        anuncios=anuncios,
        total_clics=total_clics,
        total_impresiones=total_impresiones,
        ctr_global=ctr_global,
        ingresos_totales=portal.ingresos_red_totales,
        active_page="dashboard"
    )


@app.route("/recargar", methods=["POST"])
def recargar_saldo():
    id_anunciante = request.form.get("id_anunciante")
    monto = float(request.form.get("monto", 0))
    anunciante = portal.anunciantes.get(id_anunciante)
    if anunciante and monto > 0:
        anunciante.recargar_saldo(monto)
    return redirect(url_for("dashboard"))


@app.route("/crear-anuncio", methods=["POST"])
def crear_anuncio():
    id_anunciante = request.form.get("id_anunciante")
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    cpc = float(request.form.get("cpc", 0.25))
    url_destino = request.form.get("url_destino", "https://example.com").strip()
    ubicacion = request.form.get("ubicacion", "login")

    anunciante = portal.anunciantes.get(id_anunciante)
    if anunciante and titulo:
        nuevo_id = f"AD-{101 + len(portal.anuncios)}"
        nuevo_anuncio = Anuncio(nuevo_id, anunciante, titulo, descripcion, cpc, url_destino, ubicacion)
        portal.agregar_anuncio(nuevo_anuncio)
    return redirect(url_for("dashboard"))


@app.route("/reportes")
def reportes():
    """Pantalla 3: Panel de Reportes y Auditoría."""
    filtro_anuncio = request.args.get("anuncio", "")
    transacciones = [t.to_dict() for t in portal.historial_clics]
    if filtro_anuncio:
        transacciones = [t for t in transacciones if t["id_anuncio"] == filtro_anuncio]

    return render_template(
        "reportes.html",
        transacciones=transacciones,
        anuncios=list(portal.anuncios.values()),
        filtro_actual=filtro_anuncio,
        ingresos_totales=portal.ingresos_red_totales,
        active_page="reportes"
    )


@app.route("/api/estado")
def api_estado():
    """Endpoint JSON para verificación técnica."""
    return jsonify({
        "ingresos_red_totales": portal.ingresos_red_totales,
        "anuncios": [a.to_dict() for a in portal.anuncios.values()],
        "total_transacciones": len(portal.historial_clics),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
