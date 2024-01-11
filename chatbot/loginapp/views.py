# Create your views here.

#Imports do Chatbot
import os
import threading
import time
from datetime import datetime

import pytz
import requests
from django.contrib import auth, messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from .forms import LoginForms
from .models import Chatbot, ChatbotFinalizado


def login(request):
    form = LoginForms()

    if request.method == 'POST':
        form = LoginForms(request.POST)

        if form.is_valid():
            username = form['nome_login'].value()
            password = form['senha'].value()

        usuario = auth.authenticate(
            request,
            username=username,
            password=password
        )
        if usuario is not None:
            auth.login(request, usuario)
            messages.success(request, f" Usuário {username} logado com sucesso!")   # noqa: E501
            return redirect('loginapp:chamado')
        else:
            messages.error(request, "Erro ao efetuar login")
            return redirect('loginapp:login')

    return render(request, "login.html", {"form": form})


def logout(request):
    auth.logout(request)
    messages.success(request, "Usúario deslogado")
    return redirect('loginapp:login')



def chamado(request):
    if not request.user.is_authenticated:
        return redirect('loginapp:login')
    chamado = Chatbot.objects.filter(status = 6).order_by('id')
    chamado_fechado = Chatbot.objects.filter().order_by('-id')[:51]
    tem_chamado = Chatbot.objects.filter(status = 6, encerrado = 'False')

    return render(request, 'chamado.html', context={
                'chamado': chamado,
                'chamado_fechado': chamado_fechado,
                'tem_chamado': tem_chamado,
        })


def alterar_status(request, pk):
    chamado = Chatbot.objects.get(pk=pk)
    chamado.encerrado = True
    chamado.save()
    #chamado_encerrado = ChatbotFinalizado.objects.create(telefone=chamado.telefone , mensagem=chamado.mensagem, status = chamado.status)
    #chamado_encerrado.save()
    #chamado.delete()
    #chamado_encerrado.save()
    return redirect('loginapp:chamado')


def chatbot(request):
    agent = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}  # noqa: E501


    api = requests.get(
        "https://editacodigo.com.br/index/api-whatsapp/xgLNUFtZsAbhZZaxkRh5ofM6Z0YIXwwv", headers=agent)  # noqa: E501
    time.sleep(1)
    api = api.text
    api = api.split(".n.")
    bolinha_notificacao = api[3].strip()
    contato_cliente = api[4].strip()
    caixa_msg = api[5].strip()
    msg_cliente = api[6].strip()

    #Site do selenium
    """    options = webdriver.ChromeOptions()
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)"""

    #SUAP
    """    dir_path = os.getcwd()
    chrome_driver_path = f'/usr/local/bin/chromedriver_linux64'
    chrome_options2 = Options()
    chrome_options2.add_argument(r"user-data-dir=" + dir_path + "/pasta/sessao")
    chrome_options2.add_argument("--start-maximized")
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options = chrome_options2, service=Service(ChromeDriverManager().install()))"""

    dir_path = os.getcwd()
    #chrome_driver_path = f'/Users/aeve/Downloads/chrome-win64/chromedriver'
    chrome_options2 = Options()
    #chrome_options2.add_argument(r"user-data-dir=" + dir_path + "/pasta/sessao")
    if os.path.exists(f"{dir_path}/pasta"):
        chrome_options2.add_argument("--headless=new")
        chrome_options2.add_argument(f"user-data-dir={dir_path}/pasta/sessao")
    else:
        chrome_options2.add_argument("--start-maximized")
        chrome_options2.add_argument(f"user-data-dir={dir_path}/pasta/sessao")
    driver = webdriver.Chrome(options = chrome_options2, service=Service(ChromeDriverManager().install()))
    driver.get('https://web.whatsapp.com/')

    time.sleep(10)

    def bot():

        try:

            # PEGA A BOLINHA VERDE

            bolinha = driver.find_element(By.CLASS_NAME, bolinha_notificacao)
            bolinha = driver.find_elements(By.CLASS_NAME, bolinha_notificacao)
            clica_bolinha = bolinha[-1]
            acao_bolinha = webdriver.common.action_chains.ActionChains(driver)
            acao_bolinha.move_to_element_with_offset(clica_bolinha, 0, -20)
            acao_bolinha.click()
            acao_bolinha.perform()
            acao_bolinha.click()
            acao_bolinha.perform()

            # PEGA O TELEFONE DO CLIENTE

            telefone_cliente = driver.find_element(By.XPATH, contato_cliente)
            telefone_final = telefone_cliente.text
            print(telefone_final)

            # PEGA A MENSAGEM DO CLIENTE

            todas_as_msg = driver.find_elements(By.CLASS_NAME, msg_cliente)
            todas_as_msg_texto = [e.text for e in todas_as_msg]
            msg = todas_as_msg_texto[-1]
            print(msg)

            campo_de_texto = driver.find_element(By.XPATH, caixa_msg)
            campo_de_texto.click()

            chamado = Chatbot.objects.all()
            abrir_chamado = Chatbot.objects.filter(telefone = telefone_final, encerrado = 'False')
            if abrir_chamado.exists():
                for chamado in abrir_chamado:
                    if chamado.status > 0 and chamado.status < 6:
                        chamado.status += 1
                        chamado.mensagem = msg
                        chamado.save()
                        resposta = responder(msg, telefone_final, chamado.status)
                        if chamado.status == 2 and chamado.mensagem == '5':
                            resposta = responder(msg, telefone_final, chamado.status)
                            chamado.status = 5
                            chamado.save()
                        elif chamado.status == 3 and chamado.mensagem == '1':
                            chamado.status = 1
                            chamado.save()
                        elif chamado.status == 3 and chamado.mensagem == '2':
                            chamado_finalizado = ChatbotFinalizado.objects.create(telefone=telefone_final, mensagem=msg, status = chamado.status)
                            chamado_finalizado.save()
                            chamado.delete()
                        elif resposta == 'Digite o número da opção que deseja acessar:\n1 - Contracheque\n2 - Ficha Financeira\n3 - Ficha Funcional\n4 - Declaração de Rendimentos\n5 - Outros' or resposta == 'Opção Inválida! Digite uma opção válida.\nDigite o número da opção que deseja acessar:\n1 - Contracheque\n2 - Ficha Financeira\n3 - Ficha Funcional\n4 - Declaração de Rendimentos\n5 - Outros' or resposta == 'Opção Inválida! Digite uma opção válida.\n1 - Para tirar uma nóva dúvida\n2 - Encerrar o chamado':
                            resposta = responder(msg, telefone_final, chamado.status)
                            chamado.status -= 1
                            chamado.save()
                        elif chamado.encerrado == 'True':
                            chamado_finalizado = ChatbotFinalizado.objects.create(telefone=telefone_final, mensagem=msg, status = chamado.status)
                            chamado_finalizado.save()
                            chamado.delete()
                    else:
                        resposta = responder(msg, telefone_final, chamado.status)
                    
            else:
                chamado = Chatbot.objects.create(telefone=telefone_final, mensagem=msg, status = 1)
                resposta = responder(msg, telefone_final, chamado.status)

            print(resposta)

            bot_resposta = resposta
            campo_de_texto.send_keys(bot_resposta, Keys.ENTER)

            # FECHA O CONTATO
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        except:  # noqa: E722
            print('Buscando novas mensagens')
            time.sleep(3)

    while True:
        bot()
    

def responder(msg, telefone, status):
    menuInicial = 'Olá, Bem vindo a central de dúvidas da SEAD, COPAG e Central de Atendimento.\nDigite o número da opção que deseja acessar:\n1 - Contracheque\n2 - Ficha Financeira\n3 - Ficha Funcional\n4 - Declaração de Rendimentos\n5 - Outros'

    menuContraCheque = 'Para acessar o seu ContraCheque:\na) Acesse o site: www.sead.rn.gov.br\nb) No menu selecione a opção "Serviços"\nc) Clique na opção CONSULTA DE CONTRACHEQUE\nd) Clique na sua categoria em "Acesse o seu Contracheque"\ne) Preencha os campos que estão dentro da opção "1. Contracheque"\nf) Clique em "Exibir comprovante".\nHá algo mais que eu possa fazer por você?\n1 - Sim\n2 - Não'

    menuFichaFinanceira = 'Para acessar a sua Ficha Financeira:\na) Acesse o site: www.sead.rn.gov.br\nb) No menu selecione a opção "Serviços"\nc) Clique na opção CONSULTA DE CONTRACHEQUE\nd) Clique na sua categoria em "Acesse o seu Contracheque"\ne) Preencha os campos que estão dentro da opção "2. Fecha Financeira"\nf) Clique em "Exibir Ficha Financeira".\nHá algo mais que eu possa fazer por você?\n1 - Sim\n2 - Não'

    menuFichaFuncional = 'Para acessar a sua Ficha Funcional:\na) Acesse o site suap.rn.gov.br\nb) Clique em Gestão de Pessoas\nc) Clique em Servidores\nd) No campo Texto, digite o nome completo ou a matrícula e clique em Filtrar\ne) Clique na lupa que aparece ao lado do campo "Foto"\nf) Clique na aba "Histórico Funcional".\nHá algo mais que eu possa fazer por você?\n1 - Sim\n2 - Não'

    menuDeclaracaoRendimentos = 'Para acessar a sua Declaração de Rendimentos:\na) Acesse o site: www.sead.rn.gov.br\nb) No menu selecione a opção "Serviços"\nc) Clique em "DIRPF - (Ano Vigente)"\nd) Clique na sua categoria\ne) Preencha os dados\nf) Clique em "Consultar".\nHá algo mais que eu possa fazer por você?\n1 - Sim\n2 - Não'

    menuOutros = 'Me informa por gentileza:\nQual a sua categoria (Servidor Ativo/Inativo, Pensionista, Outros):\nMatrícula:\nCPF:\nE-mail:\nDigite sua dúvida que encaminharei para um de nossos atendentes e em breve você terá um retorno:'

    menuOutrosForaDoHorario = 'Nosso horário de atendimento é de Segunda a Sexta, das 7h às 14h, mas me informa os dados abaixo que assim que possível terá um retorno de um dos nossos atendentes.\nMe informa por gentileza:\nQual a sua categoria (Servidor Ativo/Inativo, Pensionista, Outros):\nMatrícula:\nCPF:\nE-mail:\nDúvida/Problema:'

    menuNao = 'Foi um prazer ajudá-lo. Caso tenha alguma outra dúvida, estarei aqui pra te ajudar!'

    menuSim = 'Digite o número da opção que deseja acessar:\n1 - Contracheque\n2 - Ficha Financeira\n3 - Ficha Funcional\n4 - Declaração de Rendimentos\n5 - Outros'

    menuOpcaoInvalida = 'Opção Inválida! Digite uma opção válida.\nDigite o número da opção que deseja acessar:\n1 - Contracheque\n2 - Ficha Financeira\n3 - Ficha Funcional\n4 - Declaração de Rendimentos\n5 - Outros'

    menuOpcaoInvalidaSimOuNao = 'Opção Inválida! Digite uma opção válida.\n1 - Para tirar uma nóva dúvida\n2 - Encerrar o chamado'

    menuAgradecimento = 'Obrigado, aguarde que um de nossos atendentes entrará em contato com você!'

    menuDepoisDeSalvarChamado = 'Seu chamado já foi encaminhado pra um de nossos atendentes, assim que possível entraremos em contato com você! Obrigado.'
        
    if status == 1:
        msg = menuInicial    
        return msg    
    elif status == 2:
        if msg == '1':
            msg = menuContraCheque
            return msg
        elif msg == '2':
            msg = menuFichaFinanceira
            return msg
        elif msg == '3':
            msg = menuFichaFuncional
            return msg
        elif msg == '4':
            msg = menuDeclaracaoRendimentos
            return msg
        elif msg == '5':
            msg = menuOutros
            return msg
        else:
            msg = menuOpcaoInvalida
            return msg
    elif status == 3:
        if msg == '1':
            msg = menuSim
            status = 1
            return msg
        elif msg == '2':
            msg = menuNao
            return msg
        else:
            msg = menuOpcaoInvalidaSimOuNao
            return msg
    elif status == 5:
        today = datetime.now()
        day_today = today.strftime("%w")
        hour_today = today.strftime("%H")
        if 0 < day_today < 6:
            if 6 < hour_today < 15:
                msg = menuOutros
                return msg
            else:
                msg = menuOutrosForaDoHorario
                return msg
        else:
            msg = menuOutrosForaDoHorario
            return msg 
    elif status == 6:
        msg = menuAgradecimento
        return msg
    elif status > 6:
        msg = menuDepoisDeSalvarChamado
        return msg
    else:
        return print('erro')


def incrementar_status(request, pk):
    chamado = Chatbot.objects.get(pk=pk)
    chamado.status += 1
    chamado.save()
    return redirect('loginapp:chamado')

def decrementar_status(request, pk):
    chamado = Chatbot.objects.get(pk=pk)
    chamado.status -= 1
    chamado.save()
    return chamado.status



