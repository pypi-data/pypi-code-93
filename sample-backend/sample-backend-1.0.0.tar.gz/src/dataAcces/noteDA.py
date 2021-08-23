import datetime
from dataAcces.context import Context
from entites.note import Note

class NoteDA:

    def Insert(self, note):
        #MYSQL
        # sql = "INSERT INTO notas (id, titulo, descripcion, usuarioId, fecha) VALUES(NULL, %s, %s, %s, %s);"

        #SQLITE
        sql = "INSERT INTO notas (id, titulo, descripcion, usuarioId, fecha) VALUES(NULL, ?, ?, ?, ?);"

        try:
            fecha = datetime.date.today().strftime("%d/%m/%y")
            params = (note.Title, note.Description, note.UserId, fecha)
        
            context = Context()

            context.Cursor.execute(sql, params)
            context.db.commit()

            result = context.Cursor.rowcount
        except Exception as ex:
            result = 0
        return result
    
    def Update(self, note):
        #MYSQL
        # sql = "UPDATE notas SET titulo = %s, descripcion = %s, fecha = %s WHERE id = %s;"

        #SQLITE
        sql = "UPDATE notas SET titulo = ?, descripcion = ?, fecha = ? WHERE id = ?;"

        try:
            fecha = datetime.date.today().strftime("%d/%m/%y")
            params = (note.Title, note.Description, fecha, note.Id)
        
            context = Context()

            context.Cursor.execute(sql, params)
            context.db.commit()

            result = context.Cursor.rowcount
        except Exception as ex:
            result = 0
        return result
    
    def Delete(self, note):
        #MYSQL
        # sql = "DELETE FROM notas WHERE id = %s;"

        #SQLITE
        sql = "DELETE FROM notas WHERE id = ?;"

        try:
            params = (note.Id,)
        
            context = Context()

            context.Cursor.execute(sql, params)
            context.db.commit()

            result = context.Cursor.rowcount
        except Exception as ex:
            result = 0
        return result
    
    def GetById(self, id):
        #MYSQL
        # sql = "SELECT n.Id, n.titulo, n.descripcion, n.usuarioId FROM notas n WHERE n.id = %s;"

        #SQLITE
        sql = "SELECT n.Id, n.titulo, n.descripcion, n.usuarioId FROM notas n WHERE n.id = ?;"
        
        params = (id,)
    
        context = Context()

        context.Cursor.execute(sql, params)
           
        resultDb = context.Cursor.fetchone()

        return resultDb

    def GetByUser(self, userId):
        #MYSQL
        # sql = "SELECT n.Id, n.titulo, n.descripcion, n.usuarioId FROM notas n WHERE n.usuarioId = %s;"

        #SQLITE
        sql = "SELECT n.Id, n.titulo, n.descripcion, n.usuarioId FROM notas n WHERE n.usuarioId = ?;"
        
        params = (userId,)
    
        context = Context()

        context.Cursor.execute(sql, params)
           
        resultDb = context.Cursor.fetchall()

        return resultDb
