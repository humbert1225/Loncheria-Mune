import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import json
import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Lonchería Muñe - Pedidos y POS", page_icon="🌮", layout="centered")

CLAVE_ADMIN = "13junio97"
DATA_FILE = "pedidos_data.json"
COSTO_ENVIO = 15

st.title("🌮 Lonchería Muñe - Sabor Casero")
st.caption("📍 Calle 13 de Junio #97, San Antonio Matute | 📞 Tel: 3757584146")
st.info("⏰ Horario: Sábados y Domingos a partir de las 6:00 PM")

# ---------------------------------------------------------
# FUNCIONES DE PERSISTENCIA Y BASE DE DATOS
# ---------------------------------------------------------
def get_jornada_actual():
    now = datetime.now(ZoneInfo('America/Mexico_City'))
    if now.hour < 2:
        jornada_fecha = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        jornada_fecha = now.strftime("%Y-%m-%d")
    return jornada_fecha

def cargar_db():
    default_db = {
        "contador_folio": 1001,
        "pedidos": [],
        "menu": {
            "Tacos": [
                {"nombre": "Asada", "precio": 22, "disponible": True},
                {"nombre": "Adobada", "precio": 22, "disponible": True},
                {"nombre": "Chorizo", "precio": 22, "disponible": True},
                {"nombre": "Pastor", "precio": 22, "disponible": True},
                {"nombre": "Barbacoa", "precio": 22, "disponible": True},
            ],
            "Lonches": [
                {"nombre": "Asada", "precio": 55, "disponible": True},
                {"nombre": "Adobada", "precio": 55, "disponible": True},
                {"nombre": "Chorizo", "precio": 55, "disponible": True},
                {"nombre": "Pastor", "precio": 55, "disponible": True},
                {"nombre": "Barbacoa", "precio": 55, "disponible": True},
                {"nombre": "Jamón", "precio": 55, "disponible": True},
                {"nombre": "Panela", "precio": 55, "disponible": True},
                {"nombre": "Pierna", "precio": 55, "disponible": True},
            ],
            "Burritas": [
                {"nombre": "Asada", "precio": 50, "disponible": True},
                {"nombre": "Adobada", "precio": 50, "disponible": True},
                {"nombre": "Chorizo", "precio": 50, "disponible": True},
                {"nombre": "Pastor", "precio": 50, "disponible": True},
                {"nombre": "Barbacoa", "precio": 50, "disponible": True},
            ],
            "Quesadillas": [
                {"nombre": "Asada", "precio": 45, "disponible": True},
                {"nombre": "Adobada", "precio": 45, "disponible": True},
                {"nombre": "Chorizo", "precio": 45, "disponible": True},
                {"nombre": "Pastor", "precio": 45, "disponible": True},
                {"nombre": "Barbacoa", "precio": 45, "disponible": True},
            ],
            "Pellizcadas": [
                {"nombre": "Asada", "precio": 40, "disponible": True},
                {"nombre": "Adobada", "precio": 40, "disponible": True},
                {"nombre": "Chorizo", "precio": 40, "disponible": True},
                {"nombre": "Pastor", "precio": 40, "disponible": True},
                {"nombre": "Barbacoa", "precio": 40, "disponible": True},
            ],
            "Especialidades": [
                {"nombre": "Hamburguesa Clásica", "precio": 70, "disponible": True},
                {"nombre": "Sandwich (Panela, Jamón, Pierna)", "precio": 50, "disponible": True},
            ],
            "Bebidas": [
                {"nombre": "Coca de 500ml", "precio": 25, "disponible": True},
            ]
        }
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                db_data = json.load(f)
        except Exception:
            db_data = default_db
    else:
        db_data = default_db
    return db_data

def guardar_db(db):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al guardar datos: {e}")

def generar_html_ticket(p):
    folio = p.get("folio", "N/A")
    fecha = p.get("fecha_hora", datetime.now(ZoneInfo('America/Mexico_City')).strftime("%d/%m/%Y %H:%M"))
    nombre = p.get("nombre", "Cliente")
    telefono = p.get("telefono", "N/A")
    tipo_entrega = p.get("tipo_entrega", "Local")
    domicilio = p.get("domicilio", "")
    subtotal_platillos = p.get("subtotal_platillos", p.get("total_general", 0))
    costo_envio = p.get("costo_envio", 0)
    total_general = p.get("total_general", 0)
    estado_pago = p.get("estado_pago", "No Pagado")

    filas_ordenes = ""
    for ord_d in p.get("ordenes", []):
        filas_ordenes += f'<div style="font-weight:bold; margin-top:6px; border-bottom:1px solid #ccc;">ORDEN #{ord_d["num_orden"]}</div>'
        for it in ord_d.get("items", []):
            filas_ordenes += f'<div style="display:flex; justify-content:space-between; font-size:12px;"><span>{it["descripcion"]}</span><span>${it["subtotal"]}</span></div>'
        if ord_d.get("nota"):
            filas_ordenes += f'<div style="font-size:11px; font-style:italic; color:#555;">Detalle: {ord_d["nota"]}</div>'

    html_domicilio = ""
    if "Enviar a domicilio" in tipo_entrega and domicilio and domicilio not in ["Recoger en local", "Atención en Local"]:
        html_domicilio = f'<p style="font-size:12px; margin:2px 0;"><b>DOMICILIO:</b> {domicilio}</p>'

    html_envio = ""
    if costo_envio > 0:
        html_envio = f'<div style="display:flex; justify-content:space-between; font-size:12px;"><span>Envío a domicilio:</span><span>${costo_envio} MXN</span></div>'

    pago_label = "💳 PAGADO" if estado_pago == "Pagado" else "💵 NO PAGADO"

    html_code = f"""
    <div id="ticket-{folio}" style="font-family: 'Courier New', Courier, monospace; width: 280px; padding: 12px; border: 1px dashed #333; background-color: #fff; color: #000; margin: 0 auto; border-radius: 4px;">
        <h3 style="text-align: center; margin: 0; font-size: 16px;">🌮 LONCHERÍA MUÑE</h3>
        <p style="text-align: center; font-size: 11px; margin: 2px 0; font-weight: bold;">Sabor Casero</p>
        <p style="text-align: center; font-size: 10px; margin: 2px 0;">📍 Calle 13 de Junio #97, San Antonio Matute<br>📞 Tel: 3757584146</p>
        <hr style="border-top: 1px dashed #000; margin: 6px 0;">
        <p style="font-size: 12px; margin: 2px 0;"><b>FOLIO:</b> #{folio}</p>
        <p style="font-size: 11px; margin: 2px 0;"><b>FECHA:</b> {fecha}</p>
        <p style="font-size: 12px; margin: 2px 0;"><b>CLIENTE:</b> {nombre}</p>
        <p style="font-size: 12px; margin: 2px 0;"><b>TELÉFONO:</b> {telefono}</p>
        <p style="font-size: 12px; margin: 2px 0;"><b>ENTREGA:</b> {tipo_entrega}</p>
        {html_domicilio}
        <p style="font-size: 12px; margin: 2px 0;"><b>ESTADO PAGO:</b> {pago_label}</p>
        <hr style="border-top: 1px dashed #000; margin: 6px 0;">
        {filas_ordenes}
        <hr style="border-top: 1px dashed #000; margin: 6px 0;">
        <div style="display:flex; justify-content:space-between; font-size:12px;"><span>Subtotal platillos:</span><span>${subtotal_platillos} MXN</span></div>
        {html_envio}
        <h4 style="margin: 6px 0 2px 0; text-align: right; font-size: 14px;">TOTAL: ${total_general} MXN</h4>
        <hr style="border-top: 1px dashed #000; margin: 6px 0;">
        <p style="text-align: center; font-size: 11px; margin: 6px 0 0 0; font-weight: bold;">¡Gracias por su preferencia!</p>
    </div>
    <div style="text-align: center; margin-top: 8px;">
        <button onclick="window.print()" style="background-color: #2e7d32; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; cursor: pointer;">
        🖨️ Imprimir Ticket
        </button>
    </div>
    """
    return html_code

db = cargar_db()

# Session State Variables
if "owner_authenticated" not in st.session_state:
    st.session_state.owner_authenticated = False
if "num_ordenes_cliente" not in st.session_state:
    st.session_state.num_ordenes_cliente = 1
if "num_ordenes_pos" not in st.session_state:
    st.session_state.num_ordenes_pos = 1
if "pos_version" not in st.session_state:
    st.session_state.pos_version = 1

modo = st.sidebar.radio("Navegación", ["🛍️ Hacer Pedido (Cliente)", "👑 Panel Propietario"])

# ---------------------------------------------------------
# VISTA 1: CLIENTE
# ---------------------------------------------------------
if modo == "🛍️ Hacer Pedido (Cliente)":
    st.subheader("1. Arma tu pedido por orden(es)")
    st.caption("💡 Puedes dividir el pedido en varias órdenes para distintas personas (ej: Orden 1, Orden 2, Orden 3).")

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("➕ Agregar otra orden al pedido", use_container_width=True):
            st.session_state.num_ordenes_cliente += 1
            st.rerun()
    with col_btn2:
        if st.session_state.num_ordenes_cliente > 1:
            if st.button("🗑️ Eliminar última orden", use_container_width=True):
                st.session_state.num_ordenes_cliente -= 1
                st.rerun()

    ordenes_construidas = []
    subtotal_platillos_general = 0
    total_articulos_general = 0

    for ord_idx in range(1, st.session_state.num_ordenes_cliente + 1):
        with st.expander(f"📦 ORDEN #{ord_idx}", expanded=True):
            items_esta_orden = []
            total_esta_orden = 0

            for cat, prods in db["menu"].items():
                with st.expander(f"📌 {cat}", expanded=False):
                    for prod in prods:
                        nombre_p = prod["nombre"]
                        precio_p = prod["precio"]
                        disp = prod["disponible"]
                        key_id = f"cli_ord_{ord_idx}_{cat}_{nombre_p}"

                        if not disp:
                            st.caption(f"❌ {nombre_p} - (AGOTADO)")
                        else:
                            cant = st.number_input(
                                f"{nombre_p} (${precio_p} MXN c/u)",
                                min_value=0, max_value=20, value=0,
                                key=key_id
                            )
                            if cant > 0:
                                subtotal = cant * precio_p
                                if cat in ["Especialidades", "Bebidas"]:
                                    desc = f"{cant}x {nombre_p}"
                                else:
                                    cat_label = cat.rstrip("s")
                                    desc = f"{cant}x {cat_label} de {nombre_p}"
                                items_esta_orden.append({
                                    "descripcion": desc,
                                    "subtotal": subtotal,
                                    "cantidad": cant
                                })
                                total_esta_orden += subtotal
                                total_articulos_general += cant

            nota_orden = st.text_input(
                f"📝 Detalles / Especificaciones para la Orden #{ord_idx} (ej: sin salsa verde, sin cebolla, bien dorado)",
                key=f"cli_nota_ord_{ord_idx}",
                placeholder="Ej: sin salsa verde, sin cebolla..."
            )

            if items_esta_orden:
                ordenes_construidas.append({
                    "num_orden": ord_idx,
                    "items": items_esta_orden,
                    "nota": nota_orden.strip(),
                    "total_orden": total_esta_orden
                })
                subtotal_platillos_general += total_esta_orden
                st.info(f"Subtotal Orden #{ord_idx}: **${total_esta_orden} MXN**")

    st.divider()

    if total_articulos_general == 0:
        st.warning("⚠️ Selecciona al menos un producto en tus órdenes para continuar.")
    else:
        st.subheader("2. Opción de Entrega y Datos del Cliente")
        tipo_entrega = st.radio(
            "Selecciona el tipo de entrega *",
            ["🛵 Enviar a domicilio (+$15 MXN de envío)", "🏪 Recoger en el local"],
            horizontal=True
        )
        costo_envio = COSTO_ENVIO if "Enviar a domicilio" in tipo_entrega else 0
        total_general = subtotal_platillos_general + costo_envio

        if costo_envio > 0:
            st.info(f"🛵 Subtotal Platillos: **${subtotal_platillos_general} MXN** | Envío a Domicilio: **+$15 MXN** | **Total General: ${total_general} MXN**")
        else:
            st.success(f"🏪 **Total a Pagar (Recoger en local): ${total_general} MXN** ({total_articulos_general} artículos)")

        with st.form("form_cliente"):
            nombre = st.text_input("Nombre completo *")
            telefono = st.text_input("Número de teléfono de contacto (Obligatorio) *")

            domicilio = ""
            calle = ""
            num_ext = ""
            num_int = ""

            if "Enviar a domicilio" in tipo_entrega:
                st.markdown("**Datos del Domicilio de Entrega:**")
                col_d1, col_d2, col_d3 = st.columns([2, 1, 1])
                with col_d1:
                    calle = st.text_input("Nombre de la calle *", key="cli_calle")
                with col_d2:
                    num_ext = st.text_input("Número exterior *", key="cli_num_ext")
                with col_d3:
                    num_int = st.text_input("Número interior (Opcional)", key="cli_num_int")
                domicilio = f"Calle {calle.strip()} #{num_ext.strip()}" + (f" Int. {num_int.strip()}" if num_int.strip() else "")
            else:
                st.info("ℹ️ Recogerás tu pedido directamente en el local.")

            notas_generales = st.text_area("Instrucciones generales o notas adicionales (Opcional)", placeholder="Ej: Timbre blanco, aviso previo...")

            confirmar = st.form_submit_button("🚀 Confirmar y Enviar Pedido", type="primary")

            if confirmar:
                if not nombre.strip():
                    st.error("❌ El nombre es un requisito obligatorio.")
                elif not telefono.strip():
                    st.error("❌ El número de teléfono es un requisito obligatorio.")
                elif "Enviar a domicilio" in tipo_entrega and (not calle.strip() or not num_ext.strip()):
                    st.error("❌ El nombre de la calle y el número exterior son requisitos obligatorios para envíos a domicilio.")
                else:
                    db_actual = cargar_db()
                    folio_asignado = db_actual.get("contador_folio", 1001)
                    db_actual["contador_folio"] = folio_asignado + 1
                    fecha_hora_str = datetime.now(ZoneInfo('America/Mexico_City')).strftime("%d/%m/%Y %H:%M")
                    jornada_actual = get_jornada_actual()

                    pedido_completo = {
                        "folio": folio_asignado,
                        "jornada": jornada_actual,
                        "fecha_hora": fecha_hora_str,
                        "origen": "Web Cliente",
                        "estado": "Pendiente",
                        "estado_pago": "No Pagado",
                        "nombre": nombre.strip(),
                        "tipo_entrega": "🛵 Enviar a domicilio" if "Enviar a domicilio" in tipo_entrega else "🏪 Recoger en el local",
                        "domicilio": domicilio.strip() if "Enviar a domicilio" in tipo_entrega else "Recoger en local",
                        "telefono": telefono.strip(),
                        "ordenes": ordenes_construidas,
                        "subtotal_platillos": subtotal_platillos_general,
                        "costo_envio": costo_envio,
                        "total_general": total_general,
                        "notas_generales": notas_generales.strip()
                    }

                    db_actual["pedidos"].append(pedido_completo)
                    guardar_db(db_actual)

                    st.balloons()
                    st.success(f"🎉 ¡Tu pedido ha sido registrado con éxito en Lonchería Muñe con el Folio #{folio_asignado}!")
                    st.subheader("📄 Ticket de Tu Pedido")
                    components.html(generar_html_ticket(pedido_completo), height=440, scrolling=True)

# ---------------------------------------------------------
# VISTA 2: PANEL PROPIETARIO / POS
# ---------------------------------------------------------
elif modo == "👑 Panel Propietario":
    st.subheader("👑 Iniciar Sesión de Administrador")

    if not st.session_state.owner_authenticated:
        clave_ingresada = st.text_input("Ingresa tu clave de acceso de propietario:", type="password")
        if st.button("🔓 Entrar al Panel"):
            if clave_ingresada == CLAVE_ADMIN:
                st.session_state.owner_authenticated = True
                st.success("¡Acceso correcto!")
                st.rerun()
            else:
                st.error("❌ Clave de acceso incorrecta.")
    else:
        col_header, col_logout = st.columns([3, 1])
        with col_header:
            st.write("✅ Sesión activa de Propietario")
        with col_logout:
            if st.button("🔒 Cerrar Sesión"):
                st.session_state.owner_authenticated = False
                st.rerun()

        tab1, tab2, tab3, tab4 = st.tabs([
            "📦 Pedidos Recibidos (Privado)",
            "🖥️ Punto de Venta (POS Local)",
            "🏷️ Precios y Disponibilidad",
            "➕ Agregar Nuevo Producto"
        ])

        # TAB 1: HISTORIAL DE PEDIDOS Y ESTADOS
        with tab1:
            st.markdown("### 📥 Historial Privado de Pedidos del Día")
            st.caption("🔒 Acceso exclusivo. ⚡ **Auto-actualización en vivo cada 5 segundos activa**.")

            @st.fragment(run_every=5)
            def render_tab1_pedidos():
                db_fresca = cargar_db()
                pedidos_lista = db_fresca.get("pedidos", [])

                col_refresh1, col_refresh2 = st.columns([3, 1])
                with col_refresh1:
                    st.caption(f"⏱️ Última sincronización: {datetime.now(ZoneInfo('America/Mexico_City')).strftime('%H:%M:%S')} (Actualizando en vivo...)")
                with col_refresh2:
                    if st.button("🔄 Actualizar ahora", key="btn_manual_refresh_tab1", use_container_width=True):
                        st.rerun()

                if not pedidos_lista:
                    st.info("Aún no hay pedidos registrados para la jornada de hoy.")
                else:
                    total_acumulado = sum(p["total_general"] for p in pedidos_lista)
                    c1, c2 = st.columns(2)
                    c1.metric("Pedidos Recibidos Hoy", len(pedidos_lista))
                    c2.metric("Venta Acumulada", f"${total_acumulado} MXN")
                    st.write("")

                    with st.expander("🗑️ Limpiar / Borrar Todos los Pedidos del Día", expanded=False):
                        st.warning("⚠️ Esta acción borrará permanentemente todos los pedidos registrados en el sistema.")
                        clave_limpieza = st.text_input("Ingresa la clave de propietario para confirmar:", type="password", key="pwd_limpiar_pedidos")
                        if st.button("🚨 Confirmar y Borrar Pedidos", type="primary", key="btn_confirmar_limpieza"):
                            if clave_limpieza == CLAVE_ADMIN:
                                db_fresca["pedidos"] = []
                                guardar_db(db_fresca)
                                st.success("🎉 ¡Todos los pedidos han sido eliminados con éxito!")
                                st.rerun()
                            else:
                                st.error("❌ Clave de propietario incorrecta. No se borraron los pedidos.")

                    st.divider()

                    for idx, p in enumerate(reversed(pedidos_lista)):
                        fol_id = p.get("folio", idx)
                        estado_actual = p.get("estado", "Pendiente")
                        estado_pago_actual = p.get("estado_pago", "No Pagado")

                        with st.container():
                            st.markdown(f"### 🏷️ Pedido Folio #{fol_id} - {p['nombre']} (💰 Total: **${p['total_general']} MXN**)")
                            col_est1, col_est2, col_est3 = st.columns([2, 1, 1])
                            with col_est1:
                                st.caption(f"📍 Origen: **{p.get('origen', 'Web')}** | 🛵 Modalidad: **{p.get('tipo_entrega', 'N/A')}** | 🕒 Hora: **{p.get('fecha_hora', '')}**")
                            with col_est2:
                                if estado_actual == "Entregado":
                                    st.success("🟢 ENTREGADO")
                                else:
                                    st.warning("🔴 PENDIENTE")
                            with col_est3:
                                if estado_pago_actual == "Pagado":
                                    st.success("💳 PAGADO")
                                else:
                                    st.error("💵 NO PAGADO")

                            # Botones para cambiar el estado de entrega y de pago
                            col_b_est1, col_b_est2 = st.columns([1, 1])
                            with col_b_est1:
                                if estado_actual != "Entregado":
                                    if st.button("✅ Marcar como Entregado", key=f"btn_ent_{fol_id}"):
                                        p["estado"] = "Entregado"
                                        guardar_db(db_fresca)
                                        st.rerun()
                                else:
                                    if st.button("↩️ Cambiar a Pendiente", key=f"btn_pend_{fol_id}"):
                                        p["estado"] = "Pendiente"
                                        guardar_db(db_fresca)
                                        st.rerun()
                            with col_b_est2:
                                if estado_pago_actual != "Pagado":
                                    if st.button("💵 Marcar como Pagado", key=f"btn_pag_{fol_id}"):
                                        p["estado_pago"] = "Pagado"
                                        guardar_db(db_fresca)
                                        st.rerun()
                                else:
                                    if st.button("↩️ Cambiar a No Pagado", key=f"btn_nopag_{fol_id}"):
                                        p["estado_pago"] = "No Pagado"
                                        guardar_db(db_fresca)
                                        st.rerun()

                            if p.get("telefono"):
                                st.write(f"📞 **Teléfono:** [{p['telefono']}](tel:{p['telefono']})")

                            if p.get("tipo_entrega") == "🛵 Enviar a domicilio" or (p.get("domicilio") and p.get("domicilio") not in ["Recoger en local", "Atención en Local"]):
                                st.write(f"🏠 **Domicilio:** {p['domicilio']}")
                            else:
                                st.info("🏪 **Entrega:** Para atender en el local / Recoger.")

                            st.write("**Detalle por Órdenes:**")
                            for ord_d in p.get("ordenes", []):
                                st.markdown(f"**📦 Orden #{ord_d['num_orden']} (Subtotal: ${ord_d['total_orden']} MXN):**")
                                for it in ord_d.get("items", []):
                                    st.write(f" - {it['descripcion']} → **${it['subtotal']} MXN**")
                                if ord_d.get("nota"):
                                    st.write(f"   *Detalles/Especificación:* 📝 **{ord_d['nota']}**")

                            if p.get("costo_envio", 0) > 0:
                                st.write(f"🛵 **Costo de envío a domicilio:** $15 MXN")

                            if p.get("notas_generales"):
                                st.write(f"**Instrucciones generales:** {p['notas_generales']}")

                            # SECCIÓN DE EDICIÓN Y MODIFICACIÓN DE PRODUCTOS Y TIPO DE ENTREGA EN EL PEDIDO
                            with st.expander(f"✏️ Editar Productos / Entrega en Pedido #{fol_id}", expanded=False):
                                st.markdown("##### 🛒 Modificar o Eliminar Productos Existentes")
                                items_modificados = False

                                for ord_d in p.get("ordenes", []):
                                    st.caption(f"📦 **Orden #{ord_d['num_orden']}**")
                                    items_restantes = []
                                    for it_idx, it in enumerate(ord_d.get("items", [])):
                                        c_it1, c_it2, c_it3 = st.columns([3, 2, 1])
                                        with c_it1:
                                            st.write(f"• **{it['descripcion']}**")
                                        with c_it2:
                                            p_unit = int(it['subtotal'] / it['cantidad']) if it['cantidad'] > 0 else 0
                                            nueva_cant = st.number_input(
                                                "Cantidad", min_value=0, max_value=50, value=it['cantidad'],
                                                key=f"edit_qty_{fol_id}_{ord_d['num_orden']}_{it_idx}"
                                            )
                                            if nueva_cant != it['cantidad']:
                                                items_modificados = True
                                                if nueva_cant > 0:
                                                    it['cantidad'] = nueva_cant
                                                    it['subtotal'] = nueva_cant * p_unit
                                                    it['descripcion'] = re.sub(r'^\d+x', f'{nueva_cant}x', it['descripcion'])
                                                    items_restantes.append(it)
                                                else:
                                                    pass
                                            else:
                                                items_restantes.append(it)
                                        with c_it3:
                                            if st.button("🗑️", key=f"del_item_{fol_id}_{ord_d['num_orden']}_{it_idx}"):
                                                items_modificados = True
                                                if it in items_restantes:
                                                    items_restantes.remove(it)

                                    ord_d["items"] = items_restantes
                                    ord_d["total_orden"] = sum(x["subtotal"] for x in ord_d["items"])

                                st.markdown("---")
                                st.markdown("##### ➕ Agregar un Producto Nuevo a este Pedido")
                                col_add1, col_add2, col_add3 = st.columns([2, 2, 1])
                                with col_add1:
                                    cat_add = st.selectbox("Categoría", list(db_fresca["menu"].keys()), key=f"add_cat_{fol_id}")
                                with col_add2:
                                    prods_cat = [pr for pr in db_fresca["menu"][cat_add] if pr["disponible"]]
                                    nombres_prods = [pr["nombre"] for pr in prods_cat] if prods_cat else ["(Sin disponibles)"]
                                    prod_add_nom = st.selectbox("Producto", nombres_prods, key=f"add_prod_{fol_id}")
                                with col_add3:
                                    cant_add = st.number_input("Cantidad", min_value=1, max_value=20, value=1, key=f"add_cant_{fol_id}")

                                if st.button("➕ Añadir Producto al Pedido", key=f"btn_add_prod_to_{fol_id}", type="primary"):
                                    if prod_add_nom != "(Sin disponibles)":
                                        prod_obj = next((pr for pr in prods_cat if pr["nombre"] == prod_add_nom), None)
                                        if prod_obj:
                                            precio_u = prod_obj["precio"]
                                            subt = cant_add * precio_u
                                            if cat_add in ["Especialidades", "Bebidas"]:
                                                desc_new = f"{cant_add}x {prod_add_nom}"
                                            else:
                                                cat_lbl = cat_add.rstrip("s")
                                                desc_new = f"{cant_add}x {cat_lbl} de {prod_add_nom}"
                                            new_item = {
                                                "descripcion": desc_new,
                                                "subtotal": subt,
                                                "cantidad": cant_add
                                            }
                                            if not p.get("ordenes"):
                                                p["ordenes"] = [{"num_orden": 1, "items": [], "nota": "", "total_orden": 0}]
                                            p["ordenes"][0]["items"].append(new_item)
                                            p["ordenes"][0]["total_orden"] = sum(x["subtotal"] for x in p["ordenes"][0]["items"])
                                            items_modificados = True

                                if items_modificados:
                                    p["subtotal_platillos"] = sum(ord_d["total_orden"] for ord_d in p.get("ordenes", []))
                                    p["total_general"] = p["subtotal_platillos"] + p.get("costo_envio", 0)
                                    guardar_db(db_fresca)
                                    st.success(f"🎉 ¡Pedido #{fol_id} actualizado correctamente!")
                                    st.rerun()

                                # ---------------------------------------------------------
                                # MODIFICACIÓN DEL TIPO DE ENTREGA Y DOMICILIO
                                # ---------------------------------------------------------
                                st.markdown("---")
                                st.markdown("##### 🛵 Modificar Tipo de Entrega y Domicilio")

                                es_domicilio_actual = "Enviar a domicilio" in p.get("tipo_entrega", "")
                                opcion_entrega = st.radio(
                                    "Selecciona la nueva modalidad de entrega:",
                                    ["🛵 Enviar a domicilio", "🏪 Recoger en el local"],
                                    index=0 if es_domicilio_actual else 1,
                                    key=f"radio_entrega_{fol_id}"
                                )

                                domicilio_actual = p.get("domicilio", "")
                                if domicilio_actual in ["Recoger en local", "Atención en Local"]:
                                    domicilio_actual = ""

                                nuevo_domicilio = domicilio_actual
                                if "Enviar a domicilio" in opcion_entrega:
                                    nuevo_domicilio = st.text_input(
                                        "Dirección de entrega *",
                                        value=domicilio_actual,
                                        key=f"input_domicilio_{fol_id}",
                                        placeholder="Ej: Calle Hidalgo #123 Int. A"
                                    )

                                if st.button("💾 Guardar Cambio de Entrega", key=f"btn_save_entrega_{fol_id}", type="primary"):
                                    if "Enviar a domicilio" in opcion_entrega:
                                        if not nuevo_domicilio.strip():
                                            st.error("❌ Por favor ingresa una dirección válida para la entrega a domicilio.")
                                        else:
                                            p["tipo_entrega"] = "🛵 Enviar a domicilio"
                                            p["costo_envio"] = COSTO_ENVIO
                                            p["domicilio"] = nuevo_domicilio.strip()
                                            p["subtotal_platillos"] = sum(ord_d["total_orden"] for ord_d in p.get("ordenes", []))
                                            p["total_general"] = p["subtotal_platillos"] + COSTO_ENVIO
                                            guardar_db(db_fresca)
                                            st.success(f"✅ Pedido #{fol_id} cambiado a 'Enviar a domicilio' (+$15 MXN de envío).")
                                            st.rerun()
                                    else:
                                        p["tipo_entrega"] = "🏪 Recoger en el local"
                                        p["costo_envio"] = 0
                                        p["domicilio"] = "Recoger en local"
                                        p["subtotal_platillos"] = sum(ord_d["total_orden"] for ord_d in p.get("ordenes", []))
                                        p["total_general"] = p["subtotal_platillos"]
                                        guardar_db(db_fresca)
                                        st.success(f"✅ Pedido #{fol_id} cambiado a 'Recoger en el local'.")
                                        st.rerun()

                            # OPCIÓN DE IMPRIMIR TICKET EN CADA PEDIDO DEL PANEL PROPIETARIO
                            with st.expander(f"🖨️ Opción de Imprimir Ticket (Folio #{fol_id})", expanded=False):
                                components.html(generar_html_ticket(p), height=440, scrolling=True)

                            st.divider()

            render_tab1_pedidos()

        # TAB 2: PUNTO DE VENTA (POS)
        with tab2:
            col_pos_head1, col_pos_head2 = st.columns([2, 1])
            with col_pos_head1:
                st.markdown("### 🖥️ Punto de Venta (POS Local)")
            with col_pos_head2:
                if st.button("🔄 Comenzar Nuevo Pedido", key="btn_reset_pos_top", use_container_width=True, type="primary"):
                    st.session_state.num_ordenes_pos = 1
                    st.session_state.pos_version += 1
                    st.rerun()

            st.caption("Usa este botón o guarda la orden actual para iniciar un nuevo pedido en el local.")
            v_pos = st.session_state.pos_version

            col_pos_b1, col_pos_b2 = st.columns([1, 1])
            with col_pos_b1:
                if st.button("➕ Agregar otra orden al pedido POS", key="pos_add_ord", use_container_width=True):
                    st.session_state.num_ordenes_pos += 1
                    st.rerun()
            with col_pos_b2:
                if st.session_state.num_ordenes_pos > 1:
                    if st.button("🗑️ Eliminar última orden POS", key="pos_del_ord", use_container_width=True):
                        st.session_state.num_ordenes_pos -= 1
                        st.rerun()

            ordenes_pos_construidas = []
            subtotal_pos_platillos = 0
            total_pos_articulos = 0

            for ord_idx in range(1, st.session_state.num_ordenes_pos + 1):
                with st.expander(f"📦 ORDEN POS #{ord_idx}", expanded=True):
                    items_esta_orden = []
                    total_esta_orden = 0

                    for cat, prods in db["menu"].items():
                        with st.expander(f"📌 {cat}", expanded=False):
                            for prod in prods:
                                nombre_p = prod["nombre"]
                                precio_p = prod["precio"]
                                disp = prod["disponible"]
                                key_id = f"pos_v{v_pos}_ord_{ord_idx}_{cat}_{nombre_p}"

                                if not disp:
                                    st.caption(f"❌ {nombre_p} - (AGOTADO)")
                                else:
                                    cant = st.number_input(
                                        f"{nombre_p} (${precio_p} MXN)",
                                        min_value=0, max_value=20, value=0,
                                        key=key_id
                                    )
                                    if cant > 0:
                                        subtotal = cant * precio_p
                                        if cat in ["Especialidades", "Bebidas"]:
                                            desc = f"{cant}x {nombre_p}"
                                        else:
                                            cat_label = cat.rstrip("s")
                                            desc = f"{cant}x {cat_label} de {nombre_p}"
                                        items_esta_orden.append({
                                            "descripcion": desc,
                                            "subtotal": subtotal,
                                            "cantidad": cant
                                        })
                                        total_esta_orden += subtotal
                                        total_pos_articulos += cant

                    nota_orden_pos = st.text_input(
                        f"📝 Detalles / Especificaciones para la Orden POS #{ord_idx} (ej: sin salsa verde, sin cebolla)",
                        key=f"pos_v{v_pos}_nota_ord_{ord_idx}",
                        placeholder="Ej: sin salsa verde, bien dorado..."
                    )

                    if items_esta_orden:
                        ordenes_pos_construidas.append({
                            "num_orden": ord_idx,
                            "items": items_esta_orden,
                            "nota": nota_orden_pos.strip(),
                            "total_orden": total_esta_orden
                        })
                        subtotal_pos_platillos += total_esta_orden
                        st.info(f"Subtotal Orden POS #{ord_idx}: **${total_esta_orden} MXN**")

            st.divider()

            if total_pos_articulos == 0:
                st.info("💡 Selecciona los productos de la orden en las categorías desplegables arriba.")
            else:
                tipo_entrega_pos = st.radio(
                    "Modalidad de entrega POS",
                    ["🏪 Atención en local / Recoger", "🛵 Enviar a domicilio (+$15 MXN)"],
                    horizontal=True,
                    key=f"pos_v{v_pos}_tipo_entrega"
                )
                costo_envio_pos = COSTO_ENVIO if "Enviar a domicilio" in tipo_entrega_pos else 0
                total_pos_general = subtotal_pos_platillos + costo_envio_pos

                st.success(f"🛒 **Total del Pedido POS: ${total_pos_general} MXN** ({total_pos_articulos} artículos)")

                with st.form("form_pos_registro"):
                    nombre_pos = st.text_input("Nombre del cliente / Referencia de mesa *")
                    telefono_pos = st.text_input("Número de teléfono de contacto (Opcional)")

                    domicilio_pos = ""
                    calle_pos = ""
                    num_ext_pos = ""
                    num_int_pos = ""

                    if "Enviar a domicilio" in tipo_entrega_pos:
                        st.markdown("**Datos del Domicilio de Entrega:**")
                        col_pd1, col_pd2, col_pd3 = st.columns([2, 1, 1])
                        with col_pd1:
                            calle_pos = st.text_input("Nombre de la calle *", key=f"pos_v{v_pos}_calle")
                        with col_pd2:
                            num_ext_pos = st.text_input("Número exterior *", key=f"pos_v{v_pos}_num_ext")
                        with col_pd3:
                            num_int_pos = st.text_input("Número interior (Opcional)", key=f"pos_v{v_pos}_num_int")
                        domicilio_pos = f"Calle {calle_pos.strip()} #{num_ext_pos.strip()}" + (f" Int. {num_int_pos.strip()}" if num_int_pos.strip() else "")

                    notas_pos = st.text_area("Instrucciones generales de cocina (Opcional)")

                    guardar_pos = st.form_submit_button("💾 Registrar Pedido en el Sistema (POS)", type="primary")

                    if guardar_pos:
                        if not nombre_pos.strip():
                            st.error("❌ El nombre o referencia del cliente es obligatorio.")
                        elif "Enviar a domicilio" in tipo_entrega_pos and (not calle_pos.strip() or not num_ext_pos.strip()):
                            st.error("❌ La calle y número exterior son obligatorios para envíos a domicilio.")
                        else:
                            db_actual = cargar_db()
                            folio_pos = db_actual.get("contador_folio", 1001)
                            db_actual["contador_folio"] = folio_pos + 1
                            fecha_hora_pos = datetime.now(ZoneInfo('America/Mexico_City')).strftime("%d/%m/%Y %H:%M")
                            jornada_pos = get_jornada_actual()

                            pedido_pos = {
                                "folio": folio_pos,
                                "jornada": jornada_pos,
                                "fecha_hora": fecha_hora_pos,
                                "origen": "POS Local Directo",
                                "estado": "Entregado" if "Atención" in tipo_entrega_pos else "Pendiente",
                                "estado_pago": "Pagado",
                                "nombre": nombre_pos.strip(),
                                "tipo_entrega": "🛵 Enviar a domicilio" if "Enviar a domicilio" in tipo_entrega_pos else "🏪 Venta Directa en Local",
                                "domicilio": domicilio_pos.strip() if "Enviar a domicilio" in tipo_entrega_pos else "Atención en Local",
                                "telefono": telefono_pos.strip(),
                                "ordenes": ordenes_pos_construidas,
                                "subtotal_platillos": subtotal_pos_platillos,
                                "costo_envio": costo_envio_pos,
                                "total_general": total_pos_general,
                                "notas_generales": notas_pos.strip()
                            }

                            db_actual["pedidos"].append(pedido_pos)
                            guardar_db(db_actual)

                            st.session_state.num_ordenes_pos = 1
                            st.session_state.pos_version += 1

                            st.balloons()
                            st.success(f"🎉 ¡Pedido POS registrado con Folio #{folio_pos}!")

                            if st.button("➕ Limpiar pantalla y comenzar otro pedido nuevo", key=f"btn_next_pos_{folio_pos}", type="primary", use_container_width=True):
                                st.session_state.num_ordenes_pos = 1
                                st.session_state.pos_version += 1
                                st.rerun()

                            with st.expander(f"🖨️ Imprimir Ticket de Venta POS (Folio #{folio_pos})", expanded=True):
                                components.html(generar_html_ticket(pedido_pos), height=440, scrolling=True)

        # TAB 3: PRECIOS, DISPONIBILIDAD Y ELIMINAR PRODUCTOS
        with tab3:
            st.markdown("### 🏷️ Modificar Precios, Disponibilidad y Eliminar Productos")
            st.caption("Ajusta precios, marca productos como AGOTADOS o elimínalos del menú definitivamente.")

            for cat, prods in db["menu"].items():
                with st.expander(f"📌 Categoría: {cat}", expanded=True):
                    if not prods:
                        st.info("No hay productos en esta categoría.")
                    for idx, prod in enumerate(prods):
                        c_nom, c_prec, c_disp, c_del = st.columns([2, 1, 1, 1])
                        with c_nom:
                            st.write(f"**{prod['nombre']}**")
                        with c_prec:
                            nuevo_p = st.number_input(
                                "Precio ($)", min_value=1, max_value=500,
                                value=prod["precio"], key=f"p_{cat}_{idx}"
                            )
                            prod["precio"] = nuevo_p
                        with c_disp:
                            disp_state = st.toggle("Disponible", value=prod["disponible"], key=f"d_{cat}_{idx}")
                            prod["disponible"] = disp_state
                        with c_del:
                            if st.button("🗑️ Eliminar", key=f"del_{cat}_{idx}"):
                                db_actual = cargar_db()
                                db_actual["menu"][cat] = [p for p in db_actual["menu"][cat] if p["nombre"] != prod["nombre"]]
                                guardar_db(db_actual)
                                st.success(f"¡Producto '{prod['nombre']}' eliminado de {cat}!")
                                st.rerun()

            if st.button("💾 Guardar Cambios de Precios y Disponibilidad", type="primary"):
                guardar_db(db)
                st.success("✅ Precios y disponibilidad guardados permanentemente.")

        # TAB 4: AGREGAR NUEVO PRODUCTO
        with tab4:
            st.markdown("### ➕ Agregar Nuevo Producto al Menú")
            with st.form("form_nuevo_producto"):
                cat_seleccionada = st.selectbox("Selecciona la categoría donde irá el nuevo producto:", list(db["menu"].keys()))
                nombre_nuevo = st.text_input("Nombre del nuevo producto (ej: Torta de Milanesa, Taco de Birria)")
                precio_nuevo = st.number_input("Precio ($ MXN)", min_value=1, max_value=500, value=25)
                guardar_prod = st.form_submit_button("✨ Guardar y Publicar Producto")

                if guardar_prod:
                    if not nombre_nuevo.strip():
                        st.error("❌ Por favor escribe el nombre del producto.")
                    else:
                        db_actual = cargar_db()
                        db_actual["menu"][cat_seleccionada].append({
                            "nombre": nombre_nuevo.strip(),
                            "precio": precio_nuevo,
                            "disponible": True
                        })
                        guardar_db(db_actual)
                        st.success(f"🎉 ¡Producto '{nombre_nuevo}' agregado con éxito a la categoría {cat_seleccionada}!")
                        st.rerun()
