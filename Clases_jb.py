import pymysql
from tabulate import tabulate
import hashlib


class Connection:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host=os.getenv("DB_HOST", "gonz.mysql.database.azure.com"),
                user=os.getenv("DB_USER", "gonz"),
                password=os.getenv("DB_PASSWORD", "JuanitoIsSafe1"),
                db=os.getenv("DB_NAME", "jbikes"),
                port=int(os.getenv("DB_PORT", 3306)),
                ssl={"ssl": {}}, # Railway might require a specific port

            )
            self.cursor = self.connection.cursor()
        except pymysql.MySQLError as e:
            raise SystemExit(f"Error de conexión con la base de datos. Programa terminado. {e}")

    def close(self):
        self.cursor.close()
        self.connection.close()


class People:
    def __init__(self, conexion, rut, nombre, ap_paterno, ap_materno):
        self.rut = rut
        self.nombre = nombre
        self.ap_paterno = ap_paterno
        self.ap_materno = ap_materno
        self.connection = conexion.connection
        self.cursor = conexion.cursor    

    def rut_validation(self):
        rut_check = False
        while not rut_check:
            user_rut = input("Ingresa tu rut con guión y dígito verificador \nEj: xx.xxx.xxx-x\n")
            user_rut = user_rut.replace('.', '')
            while len(user_rut) < 10:
                user_rut = "0" + user_rut
            n0 = int(user_rut[0]) * 3
            n1 = int(user_rut[1]) * 2
            n2 = int(user_rut[2]) * 7
            n3 = int(user_rut[3]) * 6
            n4 = int(user_rut[4]) * 5
            n5 = int(user_rut[5]) * 4
            n6 = int(user_rut[6]) * 3
            n7 = int(user_rut[7]) * 2
            total = (n0 + n1 + n2 + n3 + n4 + n5 + n6 + n7) / 11
            integer_part = int(total)
            decimals = total - integer_part
            formula = (round(11 - (11 * decimals)))
            if formula == 11:
                formula = 0
            elif formula == 10:
                formula = "k"
            formula = str(formula)
            if user_rut[9] == 'K':
                if formula == user_rut[9].lower():
                    return True
            elif formula == (user_rut[9]):
                return user_rut
            else:
                print("El RUT ingresado es inválido")

    def rut_validation_soft(self):
        rut_check = False
        while not rut_check:
            user_rut = input("Ingresa el RUT del cliente \nEj: xx.xxx.xxx-x\n")
            user_rut = user_rut.replace('.', '')
            while len(user_rut) < 10:
                user_rut = "0" + user_rut
            if len(user_rut) < 11:
                return user_rut
            else:
                print("El RUT ingresado es inválido")
                return

    def alter_people(self, table, rut):
        cargo = ''
        if table == "usuarios":
            while cargo != '1' and cargo != '2' and cargo != '3':
                nuevo_valor = input('Ingrese el nuevo cargo: 1 Administración | 2 Recepción | 3 Técnico')
            if nuevo_valor == '1':
                cargo = 'Administración'
            elif nuevo_valor == '2':
                cargo = 'Recepción'
            else:
                cargo = 'Técnico'

            try:
                query = f"UPDATE {table} SET Cargo = %s WHERE rut = %s"
                self.cursor.execute(query, (cargo, rut))
                query2 = f"UPDAtE {table} SET Nivel = %s WHERE rut = %s"
                self.cursor.execute(query2, (nuevo_valor, rut))
                self.connection.commit()
                print(f"Usuario {rut} modificado correctamente.")
            except pymysql.MySQLError as err:
                print(f"Error al modificar usuario: {err}")

        elif table == "clientes":
            while campo != '1' and campo != '2': 
                campo = input("Ingrese el campo a modificar (1 = Contacto, 2 = Correo): ")
            if campo == '1':
                campo = 'contacto'
            elif campo == '2':
                campo = 'mail'
            nuevo_valor = input(f"Ingrese el nuevo {campo} asociado al cliente: ")

        try:
            query = f"UPDATE {table} SET {campo} = %s WHERE rut = %s"
            self.cursor.execute(query, (nuevo_valor, rut))
            self.connection.commit()
            print(f"Usuario {rut} modificado correctamente.")
        except pymysql.MySQLError as err:
            print(f"Error al modificar usuario: {err}")

    def check_rut_on_table(self, rut):
        query = "SELECT * FROM usuarios WHERE rut = %s"
        self.cursor.execute(query, (rut,))
        registro = self.cursor.fetchone()
        return registro


class User(People):
    def __init__(self, conexion, rut='1', nombre='', ap_paterno='',
                 ap_materno='', cargo='', nivel=0, clave='123'):
        super().__init__(conexion, rut, nombre, ap_paterno, ap_materno)
        self.cargo = cargo
        self.nivel = nivel
        self.clave = clave
        self.id = None
        self.connection = conexion.connection
        self.cursor = conexion.cursor    

    def get_user(self, rut, conexion):
    
        sql_sentence = """
            SELECT rut, id, nombre, ap_paterno, ap_materno, cargo, nivel, clave 
            FROM usuarios 
            WHERE rut = %s
        """
        self.cursor.execute(sql_sentence, (rut,))
        user_info = self.cursor.fetchall()
        nombre = user_info[0][2]
        ap_paterno = user_info[0][3]
        ap_materno = user_info[0][4]
        cargo = user_info[0][5]
        nivel = user_info[0][6]
        clave = user_info[0][7]
        current_user = User(conexion, rut, nombre, ap_paterno, ap_materno, cargo, nivel, clave)
        current_user.id = user_info[0][1]
        return current_user
     
    def validate_password(self, rut, contrasena, aux):
        query = "SELECT clave FROM usuarios WHERE rut = %s"
        self.cursor.execute(query, (rut,))
        result = self.cursor.fetchone()         
        if result:
            clave_almacenada = result[0] 
            if aux.encrypt_password(contrasena) == clave_almacenada: 
                return True
            else:
                return False
        else:
            return False

    def add_user(self, aux):
        try:
            sentencia_sql = (
                'INSERT INTO usuarios (rut, nombre, ap_paterno, ap_materno, cargo, nivel, clave)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s)'
                )
            self.clave = aux.encrypt_password(self.clave)
            self.cursor.execute(sentencia_sql, (self.rut, self.nombre, self.ap_paterno, self.ap_materno,
                                                self.cargo, self.nivel, self.clave))
            self.connection.commit()
            self.id = self.cursor.lastrowid
            print(self.id)
            print(f"Usuario {self.nombre} agregado correctamente.")
        except pymysql.MySQLError as err:
            print(f"Error al agregar usuario: {err}")

    def view_users(self, tecnicos=None):
        if tecnicos is None:
            self.cursor.execute("SELECT * FROM usuarios")
            registros = self.cursor.fetchall()
            print(tabulate(registros, headers=["Rut", "Id", "Nombre", "Ap. Paterno", "Ap. Materno",
                                               "Cargo", "Nivel", "Clave"], tablefmt="fancy_grid"))
        else:
            self.cursor.execute("SELECT id, nombre, ap_paterno, ap_materno, cargo from usuarios where nivel = 3")
            registros = self.cursor.fetchall()
            print(tabulate(registros, headers=["Id", "Nombre", "Ap. Paterno", "Ap. Materno"], tablefmt="fancy_grid"))

    def delete_user(self, rut):
        try:
            query = "DELETE FROM usuarios WHERE rut = %s"
            self.cursor.execute(query, (rut,))
            self.connection.commit()
            print(f"Usuario {rut} eliminado correctamente.")
        except pymysql.MySQLError as err:
            print(f"Error al eliminar usuario: {err}")

    def update_access(self, nuevo_nivel):
        while nuevo_nivel != "1" and nuevo_nivel != "2" and nuevo_nivel != "3":
            nuevo_nivel = input("Por favor elija un valor entre 1, 2 y 3")
        return nuevo_nivel


class Client(People):
    def __init__(self, conexion, aux = None, rut = "", nombre = "", ap_paterno = "", ap_materno = "", direccion = "", contacto = "", mail = ""):
        super().__init__(conexion, rut, nombre, ap_paterno, ap_materno)
        self.direccion = direccion
        self.contacto = contacto
        self.mail = mail
        self.connection = conexion.connection
        self.cursor = conexion.cursor
        self.aux = aux

    def new_client(self, rut=""):
        if rut == "":
            rut = input("Ingrese el RUT del cliente")
            rut = rut.replace('.', '')
        while len(rut) < 10:
            rut = input("RUT inválido. Por favor ingrésalo nuevamente")
            rut = rut.replace('.', '')
        if not self.aux.find_rut_in_table('clientes', rut):
            self.rut = rut
        else:
            print("RUT de cliente ya se encuentra en uso")
            return

        while True:
            self.nombre = input("Ingrese el nombre: ")
            if self.nombre and len(self.nombre) <= 30:
                break
            print("Nombre inválido.")

        while True:
            self.ap_paterno = input("Ingrese el apellido paterno: ")
            if self.ap_paterno and len(self.ap_paterno) <= 30:
                break
            print("Apellido inválido.")

        while True:
            self.ap_materno = input("Ingrese el apellido materno: ")
            if self.ap_materno and len(self.ap_materno) <= 30:
                break
            print("Apellido inválido.")

        while True:
            self.direccion = input("Ingrese la dirección: ")
            if len(self.direccion) <= 100:
                break
            print("Dirección demasiado larga.")

        while True:
            self.contacto = input("Ingrese el teléfono de contacto: ")
            if len(self.contacto) <= 15:
                break
            print("Número inválido.")

        while True:
            self.mail = input("Ingrese el correo de contacto: ")
            if len(self.mail) <= 50:
                break
            print("Correo inválido.")

        query = """
            INSERT INTO clientes (rut, nombre, ap_paterno, ap_materno, direccion, contacto, mail)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (self.rut, self.nombre, self.ap_paterno, self.ap_materno, self.direccion, self.contacto, self.mail)
        self.cursor.execute(query, values)
        self.connection.commit()
        self.connection.commit()
        print("")
        print(f"\nCliente {self.nombre} agregado correctamente.")

    def update_client(self, campo, nuevo_valor):
        try:
            query = f"UPDATE clientes SET {campo} = %s WHERE rut = %s"
            self.cursor.execute(query, (nuevo_valor, self.rut))
            self.connection.commit()
            print(f"Cliente {self.rut} modificado correctamente.")
        except pymysql.MySQLError as err:
            print(f"Error al modificar cliente: {err}")

    def delete_client(self, rut):
        try:
            query = "DELETE FROM clientes WHERE rut = %s"
            self.cursor.execute(query, (rut,))
            self.connection.commit()
            print(f"Cliente {rut} eliminado correctamente.")
        except pymysql.MySQLError as err:
            print(f"Error al eliminar cliente: {err}")

    def show_clients(self):
        self.cursor.execute("SELECT * FROM clientes")
        registros = self.cursor.fetchall()
        print(tabulate(registros, headers=["RUT", "Nombre", "Ap. Paterno", "Ap. Materno", "Dirección", "Contacto", "Correo"], tablefmt="fancy_grid"))


class WorkOrder:
    def __init__(self, conexion):
        self.connection = conexion.connection
        self.cursor = conexion.cursor
        self.rut_cliente = ""
        self.fecha_ingreso = ""
        self.problema_reportado = ""
        self.fecha_estimada_reparacion = ""
        self.id_tecnico = ""
        self.comentarios = ""

    def load_info(self, rut_cliente):
        self.rut_cliente = rut_cliente
        while True:
            self.fecha_ingreso = input("Ingrese la fecha en que se inicia la orden de trabajo (YYYY-MM-DD): ")
            try:
                # Test para ver si los datos coinciden con el formato DATE
                self.cursor.execute("SELECT DATE(%s)", (self.fecha_ingreso,))
                break
            except:
                print("Formato de fecha incorrecto. Intente nuevamente. Ej: 2024-12-27")

        while True:
            self.problema_reportado = input("Describa los problemas reportados por el cliente "
                                       "(máx. 1000 caracteres): ")
            if len(self.problema_reportado) <= 1000:
                break
            print("La descripción es demasiado larga. Intente resumirla.")

        while True:
            self.fecha_estimada_reparacion = input("Ingrese la fecha estimada de reparación (YYYY-MM-DD): ")
            try:
                self.cursor.execute("SELECT DATE(%s)", (self.fecha_estimada_reparacion,))
                break
            except:
                print("Formato de fecha incorrecto. Intente nuevamente. Ej: 2024-12-27")

        user = User(self)
        print("Estos son los técnicos disponibles:")
        user.view_users("tecnico")
        self.id_tecnico = input("ID del técnico asignado: ")

        while True:
            self.comentarios = input("Comentarios adicionales (opcional): ")
            if len(self.comentarios) < 1000:
                break
            print("El comentario es demasiado largo. Intente resumir.")

    def create(self):
        try:
            sql = """
                INSERT INTO ordenes_trabajo (rut_cliente, fecha_ingreso, problema_reportado, fecha_estimada_reparacion, 
                comentarios, id_tecnico) VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (self.rut_cliente, self.fecha_ingreso, self.problema_reportado,
                      self.fecha_estimada_reparacion, self.comentarios, self.id_tecnico)
            self.cursor.execute(sql, values)
            self.connection.commit()
            print("Orden de trabajo creada correctamente")
        except pymysql.MySQLError as err:
            print(f"Error creando la orden de trabajo: {err}")

    def view_all_orders(self, current_user=None, return_data=False):
        if current_user.nivel == 3:
            sql = """
                SELECT 
                  ot.id,
                  CONCAT(c.nombre, ' ', c.ap_paterno) AS cliente,
                  ot.fecha_ingreso,
                  ot.fecha_estimada_reparacion,
                  ot.problema_reportado,
                  ot.comentarios,
                  CONCAT(u.nombre, ' ', u.ap_paterno) AS tecnico,
                  estado
                FROM ordenes_trabajo ot
                JOIN usuarios u ON ot.id_tecnico = u.id
                JOIN clientes c ON c.rut = ot.rut_cliente
                WHERE u.id = %s;
            """
            self.cursor.execute(sql, (current_user.id,))

        else:
            sql = """
                SELECT 
                  ot.id,
                  CONCAT(c.nombre, ' ', c.ap_paterno) AS cliente,
                  ot.fecha_ingreso,
                  ot.fecha_estimada_reparacion,
                  ot.problema_reportado,
                  ot.comentarios,
                  CONCAT(u.nombre, ' ', u.ap_paterno) AS tecnico,
                  estado
                FROM ordenes_trabajo ot
                JOIN usuarios u ON ot.id_tecnico = u.id
                JOIN clientes c ON c.rut = ot.rut_cliente;
            """
            self.cursor.execute(sql)
        info = self.cursor.fetchall()
        if not info and current_user.nivel == 3:
            print("\n⚠Actualmente no tienes órdenes de trabajo asignadas.")
            return [] if return_data else None

        print(tabulate(info,
                       headers=["Id de trabajo", "Cliente", "Fecha de ingreso", "Fecha de término",
                                "Problema reportado", "Comentarios", "Técnico responsable", "Estado"],
                       tablefmt="fancy_grid"))
        if return_data:
            valid_ids = [row[0] for row in info]
            return valid_ids

    def change_order_state(self, current_user):
        valid_ids = self.view_all_orders(current_user, return_data=True)

        if valid_ids:
            while True:
                selected_id = input("Ingresa el ID de la orden de trabajo que quieres marcar como 'Completada': ")
                if not selected_id.isdigit():
                    print("Por favor ingresa solo números.")
                    continue
                selected_id = int(selected_id)
                if selected_id in valid_ids:
                    sql = """
                        UPDATE ordenes_trabajo
                        SET estado = 'Completada'
                        WHERE id = %s;
                    """
                    self.cursor.execute(sql, (selected_id,))
                    self.connection.commit()
                    print("Orden de trabajo actualizada")
                    break
                else:
                    print("El ID ingresado no está dentro de tus órdenes asignadas.")


class Aux:

    schema = ("""
          
 .----------------.  .----------------.  .----------------.  .-----------------. .----------------.  .----------------.  .----------------.   
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |  
| |     _____    | || | _____  _____ | || |      __      | || | ____  _____  | || |     _____    | || |  _________   | || |     ____     | |  
| |    |_   _|   | || ||_   _||_   _|| || |     /  \     | || ||_   \|_   _| | || |    |_   _|   | || | |  _   _  |  | || |   .'    `.   | |  
| |      | |     | || |  | |    | |  | || |    / /\ \    | || |  |   \ | |   | || |      | |     | || | |_/ | | \_|  | || |  /  .--.  \  | |  
| |   _  | |     | || |  | '    ' |  | || |   / ____ \   | || |  | |\ \| |   | || |      | |     | || |     | |      | || |  | |    | |  | |  
| |  | |_' |     | || |   \ `--' /   | || | _/ /    \ \_ | || | _| |_\   |_  | || |     _| |_    | || |    _| |_     | || |  \  `--'  /  | |  
| |  `.___.'     | || |    `.__.'    | || ||____|  |____|| || ||_____|\____| | || |    |_____|   | || |   |_____|    | || |   `.____.'   | |  
| |              | || |              | || |              | || |              | || |              | || |              | || |              | |  
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |  
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'   
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.                                           
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |                                          
| |   ______     | || |     _____    | || |  ___  ____   | || |  _________   | || |    _______   | |                                          
| |  |_   _ \    | || |    |_   _|   | || | |_  ||_  _|  | || | |_   ___  |  | || |   /  ___  |  | |                                          
| |    | |_) |   | || |      | |     | || |   | |_/ /    | || |   | |_  \_|  | || |  |  (__ \_|  | |                                          
| |    |  __'.   | || |      | |     | || |   |  __'.    | || |   |  _|  _   | || |   '.___`-.   | |                                          
| |   _| |__) |  | || |     _| |_    | || |  _| |  \ \_  | || |  _| |___/ |  | || |  |`\____) |  | |                                          
| |  |_______/   | || |    |_____|   | || | |____||____| | || | |_________|  | || |  |_______.'  | |                                          
| |              | || |              | || |              | || |              | || |              | |                                          
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |                                          
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'                                           
""")
    
    def __init__(self, conexion):
        self.connection = conexion
    
    def encrypt_password(self, contrasena):
        return hashlib.sha256(contrasena.encode()).hexdigest()
    
    def root_user(self):
        try:
            sql_sentence = (
                'INSERT IGNORE INTO usuarios (rut, nombre, ap_paterno, ap_materno, cargo, nivel, clave)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s)'
                )
            clave = self.encrypt_password('123')
            self.connection.cursor.execute(sql_sentence, ('11111111-1', 'Root', '', '', 'Administrador', 1, clave))
            self.connection.connection.commit()
        except pymysql.MySQLError as err:
            print(f"Error al agregar usuario: {err}")
    
    def dummy_users(self):

        dummys = [('22222222-2', 'Juan', 'Rodríguez', 'Silva', 'Técnico', 3, '123'),
        ('33333333-3', 'Daniela', 'Jiménez', 'Contreras', 'Técnico', 3, '123'),
        ('44444444-4', 'Miguel', 'Hito', 'Abarca', 'Recepcionista', 2, '123')]

        for usuario in dummys:
            rut = usuario[0]
            nombre = usuario[1]
            ap_paterno = usuario[2]
            ap_materno = usuario[3]
            cargo = usuario[4]
            nivel = usuario[5]
            clave = usuario[6]
       
            try:
                sentencia_sql = (
                    'INSERT IGNORE INTO usuarios (rut, nombre, ap_paterno, ap_materno, cargo, nivel, clave)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)'
                    )
                clave = self.encrypt_password(clave)
                self.connection.cursor.execute(sentencia_sql, (rut, nombre, ap_paterno, ap_materno, cargo, nivel, clave))
                self.connection.connection.commit()
            except pymysql.MySQLError as err:
                print(f"Error al agregar usuario: {err}")
    
    def find_rut_in_table(self, tabla, rut, id = None):
            if id is None:
                sql_sentence = f'select * from {tabla} where rut = %s'
                self.connection.cursor.execute(sql_sentence, (rut,))
                self.connection.connection.commit()
            else:
                sql_sentence = f'select * from {tabla} where id = %s'
                self.connection.cursor.execute(sql_sentence, (id,))
            table_content = self.connection.cursor.fetchall()
            if table_content:
                return True
            else:
                return False
            #return len(table_content) > 0
