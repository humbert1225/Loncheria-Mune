import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(page_title="Lonchería Muñe - Pedidos y POS", page_icon="🌮", layout="centered")

WHATSAPP_NUMERO = "523751209953"
CLAVE_ADMIN = "mune2402"

st.title("🌮 Lonchería Muñe - Sabor Casero")
st.caption("📍 Calle 13 de Junio #97 | 📞 Tel: 3757584146 | 💬 WhatsApp: 3751209953")
st.info("⏰ Horario: Sábados y Domingos a partir de las 6:00 PM")

# Estado de la aplicación
if "pedidos_recibidos" not in st.session_state:
    st.session_state.pedidos_recibidos = []

if "contador_folio" not in st.session_state:
    st.session_state.contador_folio = 1001

if "owner_authenticated" not in st.session_state:
    st.session_state.owner_authenticated = False

if "num_ordenes_cliente" not in st.session_state:
    st.session_state.num_ordenes_cliente = 1

if "num_ordenes_pos" not in st.session_state:
    st.session_state.num_ordenes_pos = 1

if "menu_data" not in st.session_state:
    st.session_state.menu_data = {
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
    total_general = 0
    total_articulos_general = 0

    for ord_idx in range(1, st.session_state.num_ordenes_cliente + 1):
        with st.expander(f"📦 ORDEN #{ord_idx}", expanded=True):
            items_esta_orden = []
            total_esta_orden = 0
            
            for cat, prods in st.session_state.menu_data.items():
                st.markdown(f"**{cat}**")
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
                f"📝 Detalles / Especificaciones para la Orden #{ord_idx} (ej: sin salsa verde, cebolla aparte, bien dorado)",
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
                total_general += total_esta_orden
                st.info(f"Subtotal Orden #{ord_idx}: **${total_esta_orden} MXN**")

    st.divider()

    if total_articulos_general == 0:
        st.warning("⚠️ Selecciona al menos un producto en tus órdenes para continuar.")
    else:
        st.success(f"🛒 **Resumen general ({len(ordenes_construidas)} orden/es, {total_articulos_general} artículos en total): ${total_general} MXN**")

        st.subheader("2. Opción de Entrega y Datos del Cliente")

        tipo_entrega = st.radio(
            "Selecciona el tipo de entrega *",
            ["🛵 Enviar a domicilio", "🏪 Recoger en el local"],
            horizontal=True
        )

        with st.form("form_cliente"):
            nombre = st.text_input("Nombre completo *")
            telefono = st.text_input("Número de teléfono de contacto (Obligatorio) *")
            
            domicilio = ""
            if tipo_entrega == "🛵 Enviar a domicilio":
                domicilio = st.text_input("Domicilio de entrega (Calle, Número, Colonia) *")
            else:
                st.info("ℹ️ Recogerás tu pedido directamente en el local.")

            notas_generales = st.text_area("Instrucciones generales o notas adicionales (Opcional)", placeholder="Ej: Timbre blanco, aviso previo...")

            confirmar = st.form_submit_button("🚀 Confirmar y Enviar por WhatsApp")

        if confirmar:
            if not nombre.strip():
                st.error("❌ El nombre es un requisito obligatorio.")
            elif not telefono.strip():
                st.error("❌ El número de teléfono es un requisito obligatorio para ambas modalidades de entrega.")
            elif tipo_entrega == "🛵 Enviar a domicilio" and not domicilio.strip():
                st.error("❌ El domicilio de entrega es un requisito obligatorio para envíos a domicilio.")
            else:
                # Asignar Folio Único Interno
                folio_asignado = st.session_state.contador_folio
                st.session_state.contador_folio += 1

                pedido_completo = {
                    "folio": folio_asignado,
                    "origen": "Web Cliente",
                    "nombre": nombre.strip(),
                    "tipo_entrega": tipo_entrega,
                    "domicilio": domicilio.strip() if tipo_entrega == "🛵 Enviar a domicilio" else "Recoger en local",
                    "telefono": telefono.strip(),
                    "ordenes": ordenes_construidas,
                    "total_general": total_general,
                    "notas_generales": notas_generales.strip()
                }
                st.session_state.pedidos_recibidos.append(pedido_completo)

                msg = (
                    f"🌮 *NUEVO PEDIDO - LONCHERÍA MUÑE*\n\n"
                    f"🛵 *Tipo de Entrega:* {tipo_entrega}\n"
                    f"👤 *Cliente:* {nombre.strip()}\n"
                    f"📞 *Teléfono:* {telefono.strip()}\n"
                )
                if tipo_entrega == "🛵 Enviar a domicilio":
                    msg += f"🏠 *Domicilio:* {domicilio.strip()}\n"

                msg += "\n"

                for ord_data in ordenes_construidas:
                    msg += f"📦 *ORDEN #{ord_data['num_orden']}:*\n"
                    for it in ord_data["items"]:
                        msg += f"• {it['descripcion']} = *${it['subtotal']} MXN*\n"
                    if ord_data["nota"]:
                        msg += f"📌 *Detalles:* {ord_data['nota']}\n"
                    msg += "\n"

                msg += f"💰 *TOTAL A PAGAR:* *${total_general} MXN*\n"
                if notas_generales.strip():
                    msg += f"\n📌 *Instrucciones generales:* {notas_generales.strip()}"

                msg_encoded = urllib.parse.quote(msg)
                wa_base = "https://" + "wa.me/" + WHATSAPP_NUMERO + "?text=" + msg_encoded

                st.balloons()
                st.success("🎉 ¡Pedido registrado con éxito en el sistema!")

                st.markdown("### 📲 Envía tu pedido a WhatsApp")
                st.link_button("💬 ENVIAR PEDIDO A WHATSAPP (3751209953)", wa_base, type="primary", use_container_width=True)

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

        # TAB 1: HISTORIAL DE PEDIDOS
        with tab1:
            st.markdown("### 📥 Historial Privado de Pedidos")
            st.caption("🔒 Muestra el Folio de Pedido único y los datos completos. Solo visible para ti.")
            
            if not st.session_state.pedidos_recibidos:
                st.info("Aún no hay pedidos registrados en la sesión actual.")
            else:
                total_acumulado = sum(p["total_general"] for p in st.session_state.pedidos_recibidos)
                c1, c2 = st.columns(2)
                c1.metric("Pedidos Recibidos", len(st.session_state.pedidos_recibidos))
                c2.metric("Venta Acumulada", f"${total_acumulado} MXN")

                st.divider()

                for p in reversed(st.session_state.pedidos_recibidos):
                    with st.container():
                        st.markdown(f"### 🏷️ Pedido Folio #{p['folio']} - {p['nombre']} (💰 Total: **${p['total_general']} MXN**)")
                        st.caption(f"📍 Origen: **{p.get('origen', 'Web')}** | 🛵 Modalidad: **{p.get('tipo_entrega', 'N/A')}**")
                        
                        if p.get("telefono"):
                            st.write(f"📞 **Teléfono:** [{p['telefono']}](tel:{p['telefono']})")
                            tel_clean = "".join(filter(str.isdigit, p['telefono']))
                            if len(tel_clean) == 10:
                                tel_clean = "52" + tel_clean
                            st.link_button("💬 Contactar por WhatsApp", "https://" + "wa.me/" + tel_clean)

                        if p.get("tipo_entrega") == "🛵 Enviar a domicilio" or (p.get("domicilio") and p.get("domicilio") not in ["Recoger en local", "Atención en Local"]):
                            st.write(f"🏠 **Domicilio:** {p['domicilio']}")
                            encoded_address = urllib.parse.quote(p['domicilio'])
                            gmaps_url = "https://" + "www.google.com/maps/search/?api=1&query=" + encoded_address
                            st.link_button("🗺️ Abrir en Google Maps", gmaps_url)

                            st.caption("📍 Ubicación en mapa:")
                            map_embed_url = "https://" + "maps.google.com/maps?q=" + encoded_address + "&t=&z=15&ie=UTF8&iwloc=&output=embed"
                            components.html(
                                f'<iframe width="100%" height="220" frameborder="0" src="{map_embed_url}"></iframe>',
                                height=230
                            )
                        else:
                            st.info("🏪 **Entrega:** Para atender en el local / Recoger.")

                        st.write("**Detalle por Órdenes:**")
                        for ord_d in p["ordenes"]:
                            st.markdown(f"**📦 Orden #{ord_d['num_orden']} (Subtotal: ${ord_d['total_orden']} MXN):**")
                            for it in ord_d["items"]:
                                st.write(f" - {it['descripcion']} → **${it['subtotal']} MXN**")
                            if ord_d["nota"]:
                                st.write(f"   *Detalles/Especificación:* 📝 **{ord_d['nota']}**")

                        if p["notas_generales"]:
                            st.write(f"**Instrucciones generales:** {p['notas_generales']}")

                        st.divider()

        # TAB 2: PUNTO DE VENTA (POS)
        with tab2:
            st.markdown("### 🖥️ Punto de Venta (POS para Pedidos en el Local)")
            st.caption("Usa esta ventana para registrar rápidamente pedidos de clientes que llegan en persona.")

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
            total_pos_general = 0
            total_pos_articulos = 0

            for ord_idx in range(1, st.session_state.num_ordenes_pos + 1):
                with st.expander(f"📦 ORDEN POS #{ord_idx}", expanded=True):
                    items_esta_orden = []
                    total_esta_orden = 0
                    
                    for cat, prods in st.session_state.menu_data.items():
                        st.markdown(f"**{cat}**")
                        for prod in prods:
                            nombre_p = prod["nombre"]
                            precio_p = prod["precio"]
                            disp = prod["disponible"]
                            
                            key_id = f"pos_ord_{ord_idx}_{cat}_{nombre_p}"
                            
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
                        key=f"pos_nota_ord_{ord_idx}",
                        placeholder="Ej: sin salsa verde, bien dorado..."
                    )
                    
                    if items_esta_orden:
                        ordenes_pos_construidas.append({
                            "num_orden": ord_idx,
                            "items": items_esta_orden,
                            "nota": nota_orden_pos.strip(),
                            "total_orden": total_esta_orden
                        })
                        total_pos_general += total_esta_orden
                        st.info(f"Subtotal Orden POS #{ord_idx}: **${total_esta_orden} MXN**")

            st.divider()

            if total_pos_articulos == 0:
                st.info("💡 Selecciona los productos de la orden arriba para continuar.")
            else:
                st.success(f"🛒 **Total del Pedido POS: ${total_pos_general} MXN** ({total_pos_articulos} artículos)")

                with st.form("form_pos_registro"):
                    nombre_pos = st.text_input("Nombre del cliente / Referencia de mesa *")
                    telefono_pos = st.text_input("Número de teléfono de contacto (Opcional)")
                    notas_pos = st.text_area("Instrucciones generales de cocina (Opcional)")

                    guardar_pos = st.form_submit_button("💾 Registrar Pedido en el Sistema (POS)", type="primary")

                if guardar_pos:
                    if not nombre_pos.strip():
                        st.error("❌ El nombre o referencia del cliente es obligatorio.")
                    else:
                        folio_pos = st.session_state.contador_folio
                        st.session_state.contador_folio += 1

                        pedido_pos = {
                            "folio": folio_pos,
                            "origen": "POS Local Directo",
                            "nombre": nombre_pos.strip(),
                            "tipo_entrega": "🏪 Venta Directa en Local",
                            "domicilio": "Atención en Local",
                            "telefono": telefono_pos.strip(),
                            "ordenes": ordenes_pos_construidas,
                            "total_general": total_pos_general,
                            "notas_generales": notas_pos.strip()
                        }
                        st.session_state.pedidos_recibidos.append(pedido_pos)
                        st.balloons()
                        st.success(f"🎉 ¡Pedido registrado exitosamente con Folio #{folio_pos}!")

        # TAB 3: PRECIOS Y DISPONIBILIDAD
        with tab3:
            st.markdown("### 🏷️ Modificar Precios y Disponibilidad (Agotado/Disponible)")
            st.caption("Si un producto se termina, desactiva el interruptor 'Disponible' para que aparezca como AGOTADO para los clientes.")

            for cat, prods in st.session_state.menu_data.items():
                with st.expander(f"📌 Categoría: {cat}", expanded=True):
                    for idx, prod in enumerate(prods):
                        c_nom, c_prec, c_disp = st.columns([2, 1, 1])
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

            st.success("✅ Cambios actualizados automáticamente.")

        # TAB 4: AGREGAR NUEVO PRODUCTO
        with tab4:
            st.markdown("### ➕ Agregar Nuevo Producto al Menú")

            with st.form("form_nuevo_producto"):
                cat_seleccionada = st.selectbox("Selecciona la categoría donde irá el nuevo producto:", list(st.session_state.menu_data.keys()))
                nombre_nuevo = st.text_input("Nombre del nuevo producto (ej: Torta de Milanesa, Taco de Birria)")
                precio_nuevo = st.number_input("Precio ($ MXN)", min_value=1, max_value=500, value=25)

                guardar_prod = st.form_submit_button("✨ Guardar y Publicar Producto")

            if guardar_prod:
                if not nombre_nuevo.strip():
                    st.error("❌ Por favor escribe el nombre del producto.")
                else:
                    st.session_state.menu_data[cat_seleccionada].append({
                        "nombre": nombre_nuevo.strip(),
                        "precio": precio_nuevo,
                        "disponible": True
                    })
                    st.success(f"🎉 ¡Producto '{nombre_nuevo}' agregado con éxito a la categoría {cat_seleccionada}!")
                    st.rerun()
