import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

st.set_page_config(page_title="Lonchería Muñe - Pedidos por WhatsApp", page_icon="🌮", layout="centered")

# Configuración de contacto
WHATSAPP_NUMERO = "523751209953"

st.title("🌮 Lonchería Muñe - Sabor Casero")
st.caption("📍 Calle 13 de Junio #97 | 📞 Tel: 3757584146 | 💬 WhatsApp: 3751209953")
st.info("⏰ Horario: Sábados y Domingos a partir de las 6:00 PM")

if "pedidos_recibidos" not in st.session_state:
    st.session_state.pedidos_recibidos = []

# Menú con Precios
MENU = {
    "Tacos ($22 c/u)": {
        "precio": 22,
        "items": ["Asada", "Adobada", "Chorizo", "Pastor", "Barbacoa"]
    },
    "Lonches ($55 c/u)": {
        "precio": 55,
        "items": ["Asada", "Adobada", "Chorizo", "Pastor", "Barbacoa", "Jamón", "Panela", "Pierna"]
    },
    "Burritas ($50 c/u)": {
        "precio": 50,
        "items": ["Asada", "Adobada", "Chorizo", "Pastor", "Barbacoa"]
    },
    "Quesadillas ($45 c/u)": {
        "precio": 45,
        "items": ["Asada", "Adobada", "Chorizo", "Pastor", "Barbacoa"]
    },
    "Pellizcadas ($40 c/u)": {
        "precio": 40,
        "items": ["Asada", "Adobada", "Chorizo", "Pastor", "Barbacoa"]
    },
    "Especialidades": {
        "items_con_precio": {
            "Hamburguesa Clásica": 70,
            "Sandwich (Panela, Jamón, Pierna)": 50
        }
    }
}

modo = st.sidebar.radio("Navegación", ["🛍️ Hacer Pedido (Cliente)", "👑 Panel Propietario"])

if modo == "🛍️ Hacer Pedido (Cliente)":
    st.subheader("1. Selecciona tus platillos del menú")

    pedido_items = []
    total_articulos = 0
    total_cuenta = 0

    for cat, datos in MENU.items():
        with st.expander(f"📌 {cat}", expanded=True):
            if "precio" in datos:
                precio_unitario = datos["precio"]
                for item in datos["items"]:
                    key_id = f"cant_{cat}_{item}"
                    cant = st.number_input(f"{item} (${precio_unitario} MXN c/u)", min_value=0, max_value=20, value=0, key=key_id)
                    if cant > 0:
                        subtotal = cant * precio_unitario
                        cat_nombre = cat.split(" ")[0]
                        pedido_items.append({
                            "descripcion": f"{cant}x {cat_nombre} de {item}",
                            "subtotal": subtotal,
                            "cantidad": cant
                        })
                        total_articulos += cant
                        total_cuenta += subtotal
            else:
                for item, precio_unitario in datos["items_con_precio"].items():
                    key_id = f"cant_esp_{item}"
                    cant = st.number_input(f"{item} (${precio_unitario} MXN c/u)", min_value=0, max_value=20, value=0, key=key_id)
                    if cant > 0:
                        subtotal = cant * precio_unitario
                        pedido_items.append({
                            "descripcion": f"{cant}x {item}",
                            "subtotal": subtotal,
                            "cantidad": cant
                        })
                        total_articulos += cant
                        total_cuenta += subtotal

    st.divider()

    if total_articulos == 0:
        st.warning("⚠️ Selecciona al menos un producto para ingresar tus datos y realizar tu pedido.")
    else:
        st.success(f"🛒 Resumen actual: **{total_articulos} artículo(s)** | **Total a pagar: ${total_cuenta} MXN**")
        
        with st.expander("👀 Ver desglose del pedido", expanded=True):
            for item in pedido_items:
                st.write(f"- {item['descripcion']} → **${item['subtotal']} MXN**")
            st.markdown(f"### **Total general: ${total_cuenta} MXN**")

        st.subheader("2. Ingresa tus datos de entrega")

        with st.form("form_datos_cliente"):
            nombre = st.text_input("Nombre completo *")
            domicilio = st.text_input("Domicilio de entrega (Calle, Número, Colonia) *")
            telefono = st.text_input("Número de teléfono de contacto *")
            notas = st.text_area("Instrucciones o notas adicionales (Opcional)", placeholder="Ej: Sin cebolla, salsa verde aparte...")

            confirmar = st.form_submit_button("✅ Generar Orden y Enviar a WhatsApp")

        if confirmar:
            if not nombre.strip():
                st.error("❌ El nombre es un requisito obligatorio.")
            elif not domicilio.strip():
                st.error("❌ El domicilio de entrega es un requisito obligatorio.")
            elif not telefono.strip():
                st.error("❌ El número de teléfono es un requisito obligatorio.")
            else:
                nuevo_pedido = {
                    "nombre": nombre.strip(),
                    "domicilio": domicilio.strip(),
                    "telefono": telefono.strip(),
                    "items": pedido_items,
                    "total": total_cuenta,
                    "notas": notas.strip()
                }
                st.session_state.pedidos_recibidos.append(nuevo_pedido)

                st.balloons()
                st.success("🎉 ¡Pedido registrado en el sistema!")

                lineas_pedido = "\n".join([f"• {it['descripcion']} = *${it['subtotal']} MXN*" for it in pedido_items])
                
                msg_whatsapp = (
                    f"🌮 *NUEVO PEDIDO - LONCHERÍA MUÑE*\n\n"
                    f"👤 *Cliente:* {nombre.strip()}\n"
                    f"🏠 *Domicilio:* {domicilio.strip()}\n"
                    f"📞 *Teléfono:* {telefono.strip()}\n\n"
                    f"📝 *Detalle del Pedido:*\n{lineas_pedido}\n\n"
                    f"💰 *TOTAL A PAGAR:* *${total_cuenta} MXN*\n"
                )
                if notas.strip():
                    msg_whatsapp += f"\n📌 *Notas:* {notas.strip()}"

                msg_encoded = urllib.parse.quote(msg_whatsapp)
                wa_base = "https://" + "wa.me/" + WHATSAPP_NUMERO + "?text=" + msg_encoded

                st.markdown("### 📲 ¡Paso final para enviar tu pedido!")
                st.info("Haz clic en el botón para abrir WhatsApp con el pedido listo para enviar:")
                
                st.link_button("💬 ENVIAR PEDIDO A WHATSAPP (3751209953)", wa_base, type="primary", use_container_width=True)

                st.subheader("📄 Resumen de tu Pedido")
                st.write(f"**Cliente:** {nombre}")
                st.write(f"**Domicilio:** {domicilio}")
                st.write(f"**Teléfono:** {telefono}")
                st.write(f"**Total a pagar:** ${total_cuenta} MXN")

elif modo == "👑 Panel Propietario":
    st.subheader("👑 Panel de Administración - Lonchería Muñe")

    if not st.session_state.pedidos_recibidos:
        st.info("Aún no hay pedidos registrados en la sesión actual.")
    else:
        total_ventas = sum(p['total'] for p in st.session_state.pedidos_recibidos)
        col1, col2 = st.columns(2)
        col1.metric("Pedidos Recibidos", len(st.session_state.pedidos_recibidos))
        col2.metric("Venta Total Acumulada", f"${total_ventas} MXN")

        st.divider()

        for idx, p in enumerate(st.session_state.pedidos_recibidos, 1):
            with st.container():
                st.markdown(f"### Pedido #{idx} - {p['nombre']} (💰 ${p['total']} MXN)")
                st.write(f"📞 **Teléfono:** [{p['telefono']}](tel:{p['telefono']})")
                st.write(f"🏠 **Domicilio:** {p['domicilio']}")

                tel_clean = "".join(filter(str.isdigit, p['telefono']))
                if len(tel_clean) == 10:
                    tel_clean = f"52{tel_clean}"
                wa_client_url = "https://" + "wa.me/" + tel_clean
                st.link_button("💬 Contactar cliente por WhatsApp", wa_client_url)

                encoded_address = urllib.parse.quote(p['domicilio'])
                gmaps_url = "https://" + "www.google.com/maps/search/?api=1&query=" + encoded_address

                st.link_button("🗺️ Abrir ubicación en Google Maps", gmaps_url)

                st.write("**Detalle del pedido:**")
                for item in p['items']:
                    st.write(f"- {item['descripcion']} → **${item['subtotal']} MXN**")
                
                if p['notas']:
                    st.write(f"**Notas del cliente:** {p['notas']}")

                st.caption("📍 Mapa de ubicación de entrega:")
                map_embed_url = "https://" + "maps.google.com/maps?q=" + encoded_address + "&t=&z=15&ie=UTF8&iwloc=&output=embed"
                components.html(
                    f'<iframe width="100%" height="250" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{map_embed_url}"></iframe>',
                    height=260
                )
                st.divider()
