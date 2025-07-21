import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from pytz import timezone
import json
from streamlit_drawable_canvas import st_canvas
import base64
import io
from PIL import Image

# Zona horaria de Colombia
colombia = timezone("America/Bogota")

# Configuración de Google Sheets usando st.secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
CREDS = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(CREDS)

# ID y nombre de la hoja de cálculo
SHEET_ID = "1bhqn8AC_MbZhLPt44rs5OQ4IVLYG4-oOwNK_uAmw1hM"
SHEET_NAME = "Hoja"
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)


# Título de la aplicación
st.set_page_config(page_title="Visitantes", layout="wide")
col1, col2 = st.columns([1, 4])  
with col1:
    st.image("logo.png", width=150) 
with col2:
    st.markdown(
        "<h1 style='margin-bottom: 0; color: #19287f; text-align: center; font-size: 2rem;'>"
        "Muelles y Frenos Simón Bolívar<br>Registro de Visitantes"
        "</h1>",
        unsafe_allow_html=True
    )


st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f6f6; 
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Ocultar la foto de perfil, el botón de ayuda (?) y el botón "Manage app"
hide_streamlit_ui = """
    <style>
        /* Oculta la foto de perfil */
        [data-testid="stUserMenu"] {
            display: none !important;
        }

        /* Oculta el ícono de ayuda (?) */
        [data-testid="stToolbar"] {
            display: none !important;
        }

        /* Oculta el botón "Manage app" en el pie de página */
        footer {
            visibility: hidden;
        }
    </style>
"""
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)

# Limpiar estado de sesión 
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Entrada de datos
cedula = st.text_input("Ingrese su número de cédula  (*)", placeholder="Ingrese su número de cédula", key="cedula")

# Elección de registro
accion = st.radio("¿Qué desea registrar?", ("Entrada", "Salida"))
# Si es "Entrada", mostrar formulario
st.markdown("""
    <style>
    /* Cambia el color de los labels */
    label, .stRadio label {
        color:  #19287f !important;
        font-weight: bold;
    }
    /* Cambia el color del botón */
    div.stButton > button {
        background-color:  #19287f;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    /* Cambia el color del borde de los inputs */
    .stTextInput > div > div > input {
        border: 2px solid  #19287f;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Cambia el fondo del formulario */
    div[data-testid="stForm"] {
        background-color: #f5faff !important;  /* Cambia este color a tu preferido */
        border-radius: 16px;
        padding: 32px 24px 24px 24px;
        box-shadow: 0 2px 8px rgba(25, 40, 127, 0.08);
        border: 1px solid #1976D210;
    }
    </style>
""", unsafe_allow_html=True)
if accion == "Entrada":
    if not st.session_state.submitted: 
       with st.form("form_entrada"):
            nombre = st.text_input("Nombre completo (*) ", placeholder="Ingrese su nombre completo")
            empresa = st.text_input("Empresa  (*)", placeholder="Ingrese el nombre de su empresa")
            celular = st.text_input("Celular  (*)", placeholder="Ingrese su número de celular")
            eps = st.text_input("EPS  (*)", placeholder="Ingrese el nombre de su EPS")      
            arl = st.text_input("ARL   (*)", placeholder="Ingrese el nombre de su ARL")
            nombrecontacto = st.text_input("Nombre de contacto de emergencia  (*)", placeholder="Ingrese el nombre de su contacto de emergencia")
            contacto = st.text_input("Número de contacto de emergencia   (*)", placeholder="Ingrese el número de su contacto de emergencia")
            tratamientodatos = st.radio("Según la Ley 1581 de 2012, ¿Acepta el tratamiento de sus datos personales?", ["Sí", "No"])
            st.markdown(
                '<a href="https://docs.google.com/viewer?url=https://raw.githubusercontent.com/MYF-SIMONBOLIVAR/registro_visitantes/main/FolletoSST.pdf&embedded=true" target="_blank">Clic aqui para leer la información de SST antes de continuar</a>',
                unsafe_allow_html=True
            )

            sst = st.radio("¿Leyó y entendió la información de SST?", ["Sí", "No"])
            st.write("Firma (dibuje su firma en el recuadro):")
            canvas_result = st_canvas(
                fill_color="rgba(235, 245, 251)",  # Fondo transparente
                stroke_width=2,
                stroke_color="#000000",
                background_color="#fcf3cf",
                height=150,
                width=650,
                drawing_mode="freedraw",
                key="canvas",
            )
            enviar = st.form_submit_button("Registrar Entrada")
            if enviar:
                if sst == "No":
                    st.error("Debe leer y entender la información de SST antes de continuar.")
                elif not all([cedula, nombre, empresa, celular, eps, arl, nombrecontacto, contacto]):
                    st.error("Por favor, complete todos los campos obligatorios.")
                else:
                    now = datetime.now(colombia)
                    fecha = now.strftime("%Y-%m-%d")
                    hora_entrada = now.strftime("%H:%M:%S")
                     # Convertir firma a base64
                    if canvas_result.image_data is not None:
                        image = Image.fromarray(canvas_result.image_data.astype('uint8'))
                        buffered = io.BytesIO()
                        image.save(buffered, format="PNG")
                        firma_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    else:
                        firma_base64 = "Sin firma"
                        
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
                        "",  # Hora de salida
                        sst,
                        tratamientodatos,
                        firma_base64
                        
                        
                    ]
                    sheet.append_row(fila)
                    st.session_state.submitted = True
                    st.rerun()
    else:
        st.success("Registro exitoso. Puedes registrar otro visitante.")
        if st.button("Registrar otro visitante"):
            st.session_state.submitted = False
            st.rerun()

# Si es "Salida", mostrar botón para registrar salida
elif accion == "Salida":
    if st.button("Registrar Salida"):
        data = sheet.get_all_records()
        encontrado = False
        for idx, row in enumerate(data, start=2):  # start=2 para tener en cuenta encabezado
            if str(row["Cédula"]).strip() == cedula.strip() and row["Hora de salida"] == "":
                hora_salida = datetime.now(colombia).strftime("%H:%M:%S")
                sheet.update_cell(idx, 11, hora_salida)  # Columna 11 = Hora de salida
                st.success("Salida registrada exitosamente, Gracias por tu visita, esperamos verte de nuevo.")
                encontrado = True
                break
        if not encontrado:
            st.error("No se encontró un registro de entrada pendiente para esta cédula.")
st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #19277f;">
        <p>© 2025 Muelles y Frenos Simón Bolívar. Todos los derechos reservados.</p>
    </div>
""", unsafe_allow_html=True)

