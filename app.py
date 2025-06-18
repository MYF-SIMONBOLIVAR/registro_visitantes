import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Configuración de Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("streamlit-visitas-83ccb372c88c.json", SCOPE)
client = gspread.authorize(CREDS)
# ID y nombre de la hoja de cálculo donde se insertan los datos
SHEET_ID = "1bhqn8AC_MbZhLPt44rs5OQ4IVLYG4-oOwNK_uAmw1hM"
SHEET_NAME = "Hoja"
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
# Título de la aplicación
st.set_page_config(page_title="Registro de Visitantes", page_icon="logo.png", layout="centered")
st.markdown("<h1 style='text-align: center; color: #19287f;'>Muelles y Frenos Simón Bolívar<br> Registro de Visitantes</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center;'>Bienvenido a nuestro Hogar, Por favor, complete el siguiente formulario para registrar su entrada, y al momento de salir registra tu salida.</p>",
    unsafe_allow_html=True
)
# Limpiar estado de sesión 
if "submitted" not in st.session_state:
    st.session_state.submitted = False
# Entrada de datos
cedula = st.text_input("Ingrese su número de cédula  (*)", placeholder="Ingrese su número de cédula", key="cedula")
# eleccion de registro
accion = st.radio("¿Qué desea registrar?", ("Entrada", "Salida"))
# Si es "entrada ", mostrar formulario
if accion == "Entrada":
    if not st.session_state.submitted:      
        with st.form("form_entrada"):
            nombre = st.text_input("Nombre completo (*) ", placeholder="Ingrese su nombre completo")
            empresa = st.text_input("Empresa  (*)", placeholder="Ingrese el nombre de su empresa")
            celular = st.text_input("Celular  (*)", placeholder="Ingrese su número de celular")
            eps = st.text_input("EPS  (*)", placeholder="Ingrese el nombre de su EPS")      
            arl = st.text_input("ARL   (*)", placeholder="Ingrese el nombre de su ARL")
            nombrecontacto = st.text_input("Nombre de contacto de emergencia  (*)", placeholder="Ingrese el nombre de su contacto de emergencia")
            contacto = st.text_input("Contacto de emergencia   (*)", placeholder="Ingrese el número de su contacto de emergencia")
            sst = st.radio("¿Leyó y entendió la información de SST?", ["Sí", "No"])
            enviar = st.form_submit_button("Registrar Entrada")

            if enviar:
                if not all([cedula, nombre, empresa, celular, eps, arl, nombrecontacto, contacto]):
                    st.error("Por favor, complete todos los campos obligatorios.")
                else:
                    now = datetime.now()
                    fecha = now.strftime("%Y-%m-%d")
                    hora_entrada = now.strftime("%H:%M:%S")
                    fila = [
                        cedula,
                        nombre,
                        empresa,
                        eps,
                        arl,
                        nombrecontacto,
                        contacto,
                        celular,
                        fecha,
                        hora_entrada,
                        "",  
                        sst
                    ]
                    sheet.append_row(fila)
                    st.session_state.submitted = True
                    st.rerun()
    else:
        st.success("Registro exitoso. Puedes registrar otro visitante.")
        if st.button("Registrar otro visitante"):
            st.session_state.submitted = False
            st.rerun()
# Si es "salida", mostrar botón para registrar salida
elif accion == "Salida":
    if st.button("Registrar Salida"):
        data = sheet.get_all_records()
        encontrado = False
        for idx, row in enumerate(data, start=2):
            if str(row["Cédula"]).strip() == cedula.strip() and row["Hora de salida"] == "":
                hora_salida = datetime.now().strftime("%H:%M:%S")
                sheet.update_cell(idx, 11, hora_salida)
                st.success("Salida registrada exitosamente, Gracias por tu visita, esperamos verte de nuevo.")
                encontrado = True
                break
        if not encontrado:
            st.error("No se encontró un registro de entrada pendiente para esta cédula.")
