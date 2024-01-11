from django.contrib import admin
from django.db import models


class Cadastro(models.Model):
    nome_cadastro = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    senha1 = models.CharField(max_length=70)
    senha_2 = models.CharField(max_length=70)

class Chatbot(models.Model):
    id = models.BigAutoField(primary_key=True)
    telefone = models.CharField(max_length=255)
    mensagem = models.CharField(max_length=500)
    status = models.IntegerField(default=1)
    encerrado = models.BooleanField(default=False)

    class Meta:
        db_table = 'Chatbot'

    def __str__(self):
        return f"Telefone: {self.telefone}, Status: {self.status}, Msg: {self.mensagem}"
    
class ChatbotAdmin(admin.ModelAdmin):
    list_display = ('id', 'telefone', 'mensagem', 'status', 'encerrado')
    
class ChatbotFinalizado(models.Model):
    id = models.BigAutoField(primary_key=True)
    telefone = models.CharField(max_length=255)
    mensagem = models.CharField(max_length=500)
    status = models.IntegerField(default=1)
    encerrado = models.BooleanField(default=True)

    def __str__(self):
        return f"Telefone: {self.telefone}, Status: {self.status}, Msg: {self.mensagem}"
    
class ChatbotFinalizadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'telefone', 'mensagem', 'status', 'encerrado')


