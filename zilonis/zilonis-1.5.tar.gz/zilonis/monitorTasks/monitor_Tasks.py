import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser
from enum import Enum

#Autor: Idelfonso Garcia Villaveitia
#Fecha: 17/Agosto/2021

def getMailCedula():
    cedulasEmail = getCedulaVencimiento()
    sendMailCedulasVencimiento(cedulasEmail)

def getCedulaVencimiento():
    conexion = None
    cedulas = []
    try:
        params = config(seccion='postgresql') # Lectura de los parámetros de conexion
        # print(params)
        conexion = psycopg2.connect(**params) # Conexion al servidor de PostgreSQL
        cur = conexion.cursor()
        cur.execute('SELECT * FROM vwcedulasvencimiento')
        cedulas = cur.fetchall()
        print('SALVAR REGISTROS')
        correosEnviar = list()
        for cedulaTupla in cedulas:
            cur = conexion.cursor()
            cedula = list(cedulaTupla)
            query = ''
            if cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] == None and cedula[enumFieldsRegistroCorreo.correoEnviar.value] != None and cedula[enumFieldsRegistroCorreo.correoEnviar.value] != '':
                query = '''INSERT INTO registro_envio_correos 
                    ("id_Origen", "tabla_Origen", "tipo_Correo", fecha_envio, enviado, created_at, updated_at)
                    VALUES(%s, %s, %s,current_date, false, current_timestamp, current_timestamp)'''
                print(query)
                datos = (str(cedula[enumFieldsRegistroCorreo.idOrigen.value]),cedula[enumFieldsRegistroCorreo.tablaorigen.value],cedula[enumFieldsRegistroCorreo.correoEnviar.value])
                cur.execute(query,datos)
                conexion.commit()
                cur.execute ('SELECT ID FROM registro_envio_correos WHERE "id_Origen"=%s and "tabla_Origen"=%s',(cedula[enumFieldsRegistroCorreo.idOrigen.value],cedula[enumFieldsRegistroCorreo.tablaorigen.value]))
                cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] = cur.fetchone()[0]
                cur.close()
            print("CEDULA-5: " + str(cedula[enumFieldsRegistroCorreo.diferenciadias.value]))
            # CORREO A 5 MESES
            if (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '5M' and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] == None) or (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '5M' and cedula[enumFieldsRegistroCorreo.enviado.value] == False and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] != None):
                    correosEnviar.append(cedula)
            # CORREO A 2 MESES
            elif (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '2M' and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] == None) or (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '2M' and cedula[enumFieldsRegistroCorreo.enviado.value] == False and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] != None):
                    correosEnviar.append(cedula)
            # CORREO A 1 MES
            elif (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '1M' and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] == None) or (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '1M' and cedula[enumFieldsRegistroCorreo.enviado.value] == False and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] != None):
                    correosEnviar.append(cedula)
            # CORREO A 15 DIAS
            elif (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '15D' and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] == None) or (cedula[enumFieldsRegistroCorreo.correoEnviar.value] == '15D' and cedula[enumFieldsRegistroCorreo.enviado.value] == False and cedula[enumFieldsRegistroCorreo.idregistrocorreo.value] != None):
                    correosEnviar.append(cedula)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conexion is not None:
            conexion.close()
            print('Conexión finalizada.')
    return correosEnviar

def sendMailCedulasVencimiento(cedulasEmail):
    params = config(seccion='smtp_correo')
    paramsBD = config(seccion='postgresql') 
    try:
        sql = ''
        for cedula in cedulasEmail:
            try:
                conexion = psycopg2.connect(**paramsBD) 
                cur = conexion.cursor()
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'Zilonis: Vencimiento de Cedula'
                msg['From'] = params['default_from_email'] # DEFAULT_FROM_EMAIL

                if cedula[enumFieldsRegistroCorreo.email.value] == None or cedula[enumFieldsRegistroCorreo.email.value] == '':
                    print('El agente o la promotoria no tiene un correo registrado')
                    sql = '''UPDATE registro_envio_correos
                        SET "tipo_Correo"=%s, fecha_envio=current_date, enviado=false, comentarios=%s, updated_at=current_timestamp
                        WHERE id = %s'''
                    datos = (str(cedula[enumFieldsRegistroCorreo.correoEnviar.value]),'No se tiene un correo registrado a cual enviar el correo',cedula[enumFieldsRegistroCorreo.idregistrocorreo.value])
                    cur.execute(sql,datos)
                    conexion.commit()
                    cur.close()
                    print('Registro actualizado con el mensaje: El agente o la promotoria no tiene un correo registrado')
                else:
                    print('Inicia proceso de envio de correo')
                    toAddress = [cedula[enumFieldsRegistroCorreo.email.value]]
                    msg['To'] = ', '.join(toAddress)
                    text = '''Cedula: ''' + cedula[enumFieldsRegistroCorreo.cedula.value] + '''\n Vencimiento: ''' + cedula[enumFieldsRegistroCorreo.vencimiento.value].strftime("%d/%m/%Y") + '''\n Te recordamos que tu cédula está 
                        próxima a vencer, si no has exentado favor de presentar el examen en el portal:  https://www.examencei.com.mx . \n
                        \n\n * Zilonis te enviara recordatorios anticipados a tu fecha de vencimiento a los 5 meses, 2 meses, 1 mes y 15 dias antes de la fecha de vencimiento de tu cedula.''' 
                    html = """\
                    <html>
                    <head></head>
                    <body><img src="http://zilonis-web-dev-env.eba-aa9nktu7.us-east-1.elasticbeanstalk.com/static/assets/zilonis/logo-sidebar.png" alt="ZILONIS" width="100" height="120">
                        <p>Cedula: """ + cedula[enumFieldsRegistroCorreo.cedula.value] + """</p>
                        <p>Vencimiento: """ + cedula[enumFieldsRegistroCorreo.vencimiento.value].strftime("%d/%m/%Y") + """ </p>
                        <p>Te recordamos que tu cédula está próxima a vencer, si no has exentado favor de presentar el examen en el portal: </p> 
                        <p> https://www.examencei.com.mx .<br> </p>
                        <p></p>
                        <small>* Zilonis te enviara recordatorios anticipados a tu fecha de vencimiento 
                        <p>a los 5 meses, 2 meses, 1 mes y 15 dias antes de la fecha de vencimiento de tu cedula.</p>
                        </small>
                    </body>
                    </html>
                    """  

                    part1 = MIMEText(text, 'plain') # Record the MIME types of both parts - text/plain and text/html.
                    part2 = MIMEText(html, 'html')

                    # Attach parts into message container.
                    # According to RFC 2046, the last part of a multipart message, in this case the HTML message, is best and preferred.
                    msg.attach(part1)
                    msg.attach(part2)
                    s = smtplib.SMTP(params['email_host'],params['email_port']) 
                    s.ehlo()
                    s.starttls()
                    s.login(params['email_host_user'],params['email_host_password']) 
                    s.sendmail(params['default_from_email'],toAddress,msg.as_string()) 
                    s.quit()

                    sql = '''UPDATE registro_envio_correos
                        SET "tipo_Correo"=%s, fecha_envio=current_date, enviado=true, updated_at=current_timestamp
                        WHERE id = %s'''
                    datos = (str(cedula[enumFieldsRegistroCorreo.correoEnviar.value]),cedula[enumFieldsRegistroCorreo.idregistrocorreo.value])
                    cur.execute(sql,datos)
                    conexion.commit()
                    cur.close()
                    print('Correo enviado y registro actualizado')
            except Exception as ex:
                print('Error al enviar correo: ' + str(ex))
                sql = '''UPDATE registro_envio_correos
                        SET "tipo_Correo"=%s, fecha_envio=current_date, enviado=false, comentarios=%s, updated_at=current_timestamp
                        WHERE id = %s'''
                datos = (str(cedula[enumFieldsRegistroCorreo.correoEnviar.value]),'Error al enviar correo: ' + str(ex),cedula[enumFieldsRegistroCorreo.idregistrocorreo.value])
                cur.execute(sql,datos)
                conexion.commit()
                cur.close()
            finally:
                conexion.close()
                print('Envio de registro llego al Finally.')
                
    except Exception as ex:
        print('Error en el manejo de las excepciones del envio de correo: ' + str(ex))
    finally:
        if conexion is not None:
            conexion.close()
            print('Conexión finalizada.')
    

def config(archivo='config.ini', seccion='postgresql'):
    # archivo = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.ini')
    # Crear el parser y leer el archivo
    parser = ConfigParser()
    parser.read(archivo)
    
    # Obtener la sección de conexión a la base de datos
    db = {}
    if parser.has_section(seccion):
        print('Tiene seccion {0}'.format(seccion))
        params = parser.items(seccion)
        print(params)
        for param in params:
            db[param[0]] = param[1]
        return db
    else:
        raise Exception('Secccion {0} no encontrada en el archivo {1}'.format(seccion, archivo))

class enumFieldsRegistroCorreo(Enum):
    idOrigen = 0
    nombre = 1
    email = 2
    cedula = 3
    vencimiento = 4
    diferenciadias = 5
    correoEnviar = 6
    tablaorigen = 7
    tipo_correo = 8
    enviado = 9
    idregistrocorreo = 10
