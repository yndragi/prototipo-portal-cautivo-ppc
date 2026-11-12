# Prototipo: Portal Cautivo con Monetización por Pago por Clic (PPC)

Sistema desarrollado bajo el paradigma de Programación Orientada a Objetos (POO) en Python (Flask) que controla el acceso a Internet mediante un portal cautivo web y monetiza el tráfico a través de anuncios publicitarios bajo el modelo Pago por Clic (PPC).

## Características Principales
1. **Portal Cautivo Web (`/`)**: Autenticación de usuarios antes de conceder acceso a Internet y despliegue de banners publicitarios tanto en la pantalla de inicio de sesión como después de la autenticación.
2. **Dashboard del Anunciante (`/dashboard`)**: Gestión de saldo, recarga de fondos, métricas de impresiones, clics, CTR y creación de nuevas campañas.
3. **Panel de Reportes (`/reportes`)**: Auditoría detallada de cada clic registrado con marca de tiempo, usuario, IP de origen y monto descontado.
4. **Corrido en Frío (`test_corrido_frio.py`)**: Simulación por consola de la prueba de escritorio paso a paso.

## Instalación y Ejecución Local

```bash
pip install -r requirements.txt
python3 app.py
```
Abrir en el navegador: `http://127.0.0.1:5000` (Usuario de prueba: `invitado` / Contraseña: `1234`).
