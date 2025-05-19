from Clases_jb import Connection, Tables, People, User, Client, Aux, WorkOrder
conexion = Connection()
tables = Tables(conexion)
tables.create_tables()
people = People(conexion, '11111111-1', 'Dummy_user', '', '')
user = User(conexion)
aux = Aux(conexion)
client = Client(conexion)
aux.root_user()
aux.dummy_users()
active_program = True


def menu_perfiles():
    estado_perfiles = True
    while estado_perfiles:
        print("\n1. Crear Usuario")
        print("2. Ver Usuarios")
        print("3. Modificar Usuario")
        print("4. Eliminar Usuario")
        print("5. Volver al menú principal")
        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            rut = input("Ingrese el RUT: ")
            nombre = input("Ingrese el nombre: ")
            ap_paterno = input("Ingrese el apellido paterno: ")
            ap_materno = input("Ingrese el apellido materno: ")
            cargo = input("Ingrese el cargo: ")
            nivel = input("Ingrese el nivel de acceso (1 = Admin, 2 = Recepción, 3 = Técnico): ")
            while nivel != "1" and nivel != "2" and nivel != "3":
                nivel = input("Por favor elija un valor entre 1, 2 y 3")
            clave = input("Ingrese la clave: ")
            nuevo_usuario = User(conexion, rut, nombre, ap_paterno, ap_materno, cargo, nivel, clave)
            nuevo_usuario.add_user(aux)
                
        elif opcion == '2':
            user.view_users()
        
        elif opcion == '3':
            user.view_users()
            rut = input("Ingrese el RUT del usuario a modificar: ")
            if aux.find_rut_in_table('usuarios', rut):
                user.alter_people('usuarios', rut)
            else:
                print("El rut seleccionado no existe en los registros")
            
        elif opcion == '4':
            user.view_users()
            rut = input("Ingrese el RUT del usuario a eliminar: ")
            if aux.find_rut_in_table('usuarios', rut):
                user.delete_user(rut)
            else:
                print("El rut seleccionado no existe en los registros")
            
        elif opcion == '5':
            estado_perfiles = False
        else:
            print("Opción inválida.")


def menu_recepcion(active_program, current_user):
    estado_recepcion = True
    client = Client(conexion, aux)
    new_work_order = WorkOrder(conexion)
    while estado_recepcion:
        print("")
        print("1. Crear Cliente")
        print("2. Modificar Cliente")
        print("3. Eliminar Cliente")
        print("4. Ver listado de clientes")
        print("5. Ingresar Orden de Trabajo")
        print("6. Ver Órdenes de Trabajo")
        print("7. Salir del programa")
        
        if current_user.nivel == 1:
            print("\n0. Volver al menú de Administración")
        opcion = input("\nSeleccione una opción: ")
        
        if current_user.nivel == 1 and opcion == '0':
            estado_recepcion = False

        elif opcion == '1':
            client.new_client()
        elif opcion == '2':
            rut = input("Ingrese el RUT del cliente a modificar: ")
            if aux.find_rut_in_table('clientes', rut):
                people.alter_people('clientes', rut)
            else:
                print("El rut seleccionado no existe en los registros")
        
        elif opcion == '3':
            client.show_clients()
            rut = input("Ingrese el RUT del cliente a eliminar: ")
            client.delete_client(rut)

        elif opcion == '4':
            client.show_clients()

        elif opcion == '5':
            temp = client.rut_validation_soft()
            if temp is not None:
                rut_cliente = temp
            if aux.find_rut_in_table('clientes', rut_cliente):
                new_work_order.load_info(rut_cliente)
                new_work_order.create()
            else:
                to_create = input("El cliente no existe en el sistema. ¿Desea crearlo?").lower()
                if to_create == "sí" or to_create == "s" or to_create == "si":
                    client.new_client(rut_cliente)
                    if aux.find_rut_in_table('clientes', rut_cliente):
                        new_work_order.load_info(rut_cliente)
                        new_work_order.create()
                else:
                    continue

        elif opcion == '6':
            new_work_order.view_all_orders()

        elif opcion == '7':
            active_program = False
            estado_recepcion = False

        else:
            print("Opción inválida.")
    return active_program


def menu_tecnico(active_program, current_user):
    new_work_order = WorkOrder(conexion)
    estado_tecnico = True
    while estado_tecnico:
        print("1. Ver Órdenes de Trabajo Asignadas")
        print("2. Modificar Estado de Orden de Trabajo")
        print("3. Salir")
        if current_user.nivel == 1:
            print("\n0. Volver al menú de Administración")
        opcion = input("\nSeleccione una opción: ")

        if current_user.nivel == 1 and opcion == '0':
            estado_tecnico = False

        if opcion == '1':
            new_work_order.view_all_orders(current_user)

        elif opcion == '2':
            new_work_order.change_order_state(current_user)

        elif opcion == '3':
            estado_tecnico = False
            active_program = False

        else:
            print("Opción inválida.")
    return active_program


def menu_administrador(active_program, current_user):
    while active_program:
        print("\n1. Administrar Perfiles")
        print("2. Recepción")
        print("3. Técnicos")
        print("4. Salir")
        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            menu_perfiles()
        elif opcion == '2':
            active_program = menu_recepcion(active_program, current_user)
        elif opcion == '3':
            active_program = menu_tecnico(active_program, current_user)
        elif opcion == '4':
            active_program = False
        else:
            print("Opción inválida.")
    return active_program


def login():
    login_attempt_count = 0
    while login_attempt_count <= 3:
        login_attempt_count = login_attempt_count + 1
        user_login = people.rut_validation()
        user_pass = input("Ingrese contraseña de usuario: ") 
        if people.check_rut_on_table(user_login) and user.validate_password(user_login, user_pass, aux):
            print("Inicio de sesión exitoso.")
            return user_login             
        elif login_attempt_count == 3:
            print("Demasiados intentos fallidos")
        else:
            print("RUT o contraseña incorrectos. Intente nuevamente")      
                

print(aux.schema)
print("Por favor inicie sesión")

while active_program:
    user_login = login()
    if user_login:
        current_user = user.get_user(user_login, conexion)
        if current_user.nivel == 1:  # Administrador
            active_program = menu_administrador(active_program, current_user)
        elif current_user.nivel == 2:  # Recepción
            active_program = menu_recepcion(active_program, current_user)
        elif current_user.nivel == 3:  # Técnico
            active_program = menu_tecnico(active_program, current_user)
    else:
        active_program = False


print("Saliendo del sistema.")
conexion.close()
