# Register your models here.
from django.contrib import admin

from .models import (Chatbot, ChatbotAdmin, ChatbotFinalizado,
                     ChatbotFinalizadoAdmin)

# Register your models here.

#admin.site.register(ChamadosCriados)
admin.site.register(Chatbot, ChatbotAdmin)
admin.site.register(ChatbotFinalizado, ChatbotFinalizadoAdmin)
