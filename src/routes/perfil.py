from extension.extesion import *

perfil_bp = Blueprint('perfil', __name__)


# Funcion para editar el perfil y verlo
@perfil_bp.route('/perfil/editar', methods=['GET', 'POST'])
def perfil():
    
    form=perfilform(obj=current_user)
    
    if request.method == 'POST':

        if form.validate_on_submit():
            nombre = form.nombre.data
            correo = form.correo.data
            fecha_nacimiento = form.fecha_nacimiento.data
        
            if ModelUser.update_user(db, current_user.id, nombre, correo,fecha_nacimiento):
                flash("Perfil actualizado correctamente.","success")
                return redirect(url_for('perfil.perfil'))
            
            else:
                flash("Error al actualizar el perfil.","error")
                return redirect(url_for("perfil.perfil"))
        else:
            flash("Corrige los errores del formulario", "error")
            return render_template('perfil.html', form=form, user=current_user)

    if request.method == "GET":
        if current_user.is_authenticated:
            return render_template('perfil.html', form=form, user=current_user)
        
        else:
            return redirect(url_for('iniciar_sesion'))

# Funcion para eliminar la cuenta del usuario(usuario)
@perfil_bp.route('/eliminar', methods=['POST'])
def eliminar_cuenta():
    
    user = ModelUser.get_by_id(db, current_user.id)

    if request.method == 'POST':
        if current_user.is_authenticated:
            ModelUser.delete_user(db, user.id)
            logout_user()
            flash("Perfil eliminado correctamente.","info")
            return redirect(url_for('inicio.html'))
        
@perfil_bp.route('/historial', methods=['GET'])
def historial_compras():
    
    if current_user.is_authenticated:
        compra = ModelUser.historial_compras(db, current_user.id)
        return render_template('historial_compras.html', compra=compra)
    else:
        return redirect(url_for('auth.iniciar_sesion'))
    
@perfil_bp.route('/historial')
def tu_ruta_historial():

    cur = db.connection.cursor()
    
    evento = request.args.get('evento', '').strip()
    fecha = request.args.get('fecha', '').strip()
    lugar = request.args.get('lugar', '').strip()

    # Construye la consulta según filtros (ajusta según tu acceso a BD)
    query = "SELECT * FROM entradas WHERE usuario_id = %s"
    params = [current_user.id]

    if evento:
        query += " AND nombre_evento LIKE %s"
        params.append(f"%{evento}%")
    if fecha:
        query += " AND fecha_evento = %s"
        params.append(fecha)
    if lugar:
        query += " AND lugar_evento LIKE %s"
        params.append(f"%{lugar}%")

    # Ejecutar consulta con params y devolver resultados
    compra = cur.excute(query, params)
    db.connection.commit()
    cur.close()
    return render_template('historial.html', compra=compra)

@perfil_bp.route('/eliminar_entrada/<int:entrada_id>', methods=['POST'])
def eliminar_entrada(entrada_id):
    
    if current_user.is_authenticated and request.method == "POST":
        cur = db.connection.cursor()
        cur.execute("DELETE FROM entradas WHERE id = %s AND usuario_id = %s", (entrada_id, current_user.id))
        db.connection.commit()
        cur.close()
        flash('Entrada eliminada correctamente', 'success')

        return redirect(url_for('perfil.tu_ruta_historial'))
    else:
        return redirect(url_for('auth.iniciar_sesion'))
    
@perfil_bp.route('/devolver_entrada/<int:entrada_id>', methods=['POST'])
def devolver_entrada(entrada_id):

    if request.method == "POST" and current_user.is_authenticated:

        entrada_id = request.form.get('entrada_id')

        if not entrada_id:
            flash("Entrada no válida", "error")
            return redirect(url_for('perfil.historial_compras'))

        success = ModelUser.procesar_devolucion(db, entrada_id, current_user.id)

        if success:
            flash("Entrada devuelta con éxito", "success")
        else:
            flash("No se pudo procesar la devolución. Asegúrate de que cumpla las condiciones.", "error")

        return redirect(url_for('perfil.historial_compras'))
    else:
        return redirect(url_for('auth.iniciar_sesion'))


