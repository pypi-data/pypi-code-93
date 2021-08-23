from dataAcces.noteDA import NoteDA
from entites.note import Note


class NoteManager:
    
    
    def Create(self, note):
        da = NoteDA()
        
        return da.Insert(note)
    
    def Update(self, note):
        da = NoteDA()
        
        return da.Update(note)
    
    def Delete(self, note):
        da = NoteDA()
        
        return da.Delete(note)
    
    def GetById(self, id):
        da = NoteDA()
        record = da.GetById(id)

        if(record != None):
            nota = Note(record[0],record[1],record[2],record[3])

        return nota

    def GetByUser(self, userId):
        da = NoteDA()
        resultDb = da.GetByUser(userId)

        notas = []
        if(resultDb != None):
            for record in resultDb:
                nota = Note(record[0],record[1],record[2],record[3])
                notas.append(nota)

        return notas
