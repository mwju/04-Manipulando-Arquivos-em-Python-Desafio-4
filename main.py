import datetime
import os
import functools

# Constantes
AGENCIA = "0001"
LIMITE_SAQUES = 3
LIMITE_TRANSACOES_DIARIAS = 10
clientes = []


# Decorador para imprimir mensagens antes e depois de chamar uma função
def imprimir_mensagem(func):
    def wrapper(*args, **kwargs):
        print(f"Chamando {func.__name__}")
        resultado = func(*args, **kwargs)
        print(f"Concluído {func.__name__}")
        return resultado
    return wrapper


# Função para converter os argumentos em uma string formatada
def formatar_argumentos(args, kwargs):
    argumentos = [repr(arg) for arg in args] + [f"{key}={value!r}" for key, value in kwargs.items()]
    return ", ".join(argumentos)

# Decorador para registrar informações de execução de função em um arquivo de log
def registrar_execucao(func):
    @functools.wraps(func)  # Preserva os metadados da função original
    def wrapper(*args, **kwargs):
        # Registrar data e hora atuais
        horario_atual = datetime.datetime.now()
        # Registrar nome da função
        nome_funcao = func.__name__
        # Registrar argumentos da função
        argumentos_str = formatar_argumentos(args, kwargs)
        # Chamar função e registrar valor retornado
        resultado = func(*args, **kwargs)
        
        # Criar ou abrir arquivo de log em modo de adição
        with open("log.txt", "a") as arquivo_log:
            # Escrever informações no arquivo
            arquivo_log.write(f"Função: {nome_funcao}, Argumentos: {argumentos_str}, Valor Retornado: {resultado}, Horário: {horario_atual}\n")

        return resultado
    return wrapper

class Endereco:
    def __init__(self, rua, numero, complemento, bairro, cidade, uf):
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf

class Cliente:
    def __init__(self, cpf, nome, data_nascimento, endereco, qtd_saques=0):
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.endereco = endereco
        self.contas = []
        self.qtd_saques = qtd_saques

    def adicionar_conta(self, conta):
        self.contas.append(conta)

    # Implementação do iterador de classe
    def __iter__(self):
        return iter(self.contas)

class Transacao:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
        self.horario = datetime.datetime.now()

    def registrar(self, conta):
        conta.extrato.append((self.horario, self.valor))

class Conta:
    _numero_conta = 0  # Atributo de classe para controlar o número da próxima conta

    def __init__(self, cliente, agencia, extrato=None):
        self.cliente = cliente
        self.numero_conta = self.gerar_numero_conta()  # Usando o gerador de número de conta
        self.agencia = agencia
        if extrato is None:
            self.extrato = []
        else:
            self.extrato = extrato
        self.historico = Historico()  # Cria uma instância de Historico para a conta

    @classmethod
    def gerar_numero_conta(cls):
        cls._numero_conta += 1
        return cls._numero_conta

    def realizar_transacao(self, transacao):
        transacao.registrar(self)

    @property
    def saldo(self):
        total = 0
        for horario, valor in self.extrato:
            total += valor
        return total

    def efetiva_deposito(self, valor):
        if valor > 0:
            now = datetime.datetime.now()
            self.extrato.append((now, valor))  # Adiciona uma tupla (horário, valor) ao extrato
            self.historico.registrar_transacao("Depósito", valor, now)
            return True
        else:
            print('Valor não pode ser negativo')
            return False

    def efetiva_retirada(self, valor):
        if self.cliente.qtd_saques > LIMITE_SAQUES:
            print(f'Valor excede limite de saque. Limite: R$ {self.cliente.qtd_saques}')
            return False
        elif valor > self.saldo:
            print('Saldo insuficiente para saque.')
            return False
        else:
            now = datetime.datetime.now()
            self.extrato.append((now, -valor))  # Adiciona uma tupla (horário, valor) ao extrato
            self.historico.registrar_transacao("Saque", valor, now)
            return True

    def listar_extrato(self):
        if not self.extrato:
            print('Não foram realizadas movimentações!')
        else:
            print("==========================================")
            print(f"CPF: {self.cliente.cpf}")
            print(f"Agência: {self.agencia}")
            print(f"C/C: {self.numero_conta}")
            print(f"Titular: {self.cliente.nome}")
            print("==========================================")
            print("Início Extrato")
            for horario, valor in self.extrato:
                
                if valor >= 0:
                    print(f"Depósito: {valor}, Horário: {horario.strftime('%d/%m/%Y, %H:%M')}")
                else:
                    print(f"Saque: {-valor}, Horário: {horario.strftime('%d/%m/%Y, %H:%M')}")
            print(f"\nSaldo: R$ {self.saldo}")
            print("Fim Extrato")
            print("==========================================")

class Historico:
    def __init__(self):
        self.transacoes = []

    def registrar_transacao(self, tipo, valor, horario):    
        if len(self.transacoes) >= LIMITE_TRANSACOES_DIARIAS:
            print(f'Número máximo de transações atingido (Máximo {LIMITE_TRANSACOES_DIARIAS})')
        else:
            self.transacoes.append((tipo, valor, horario))

    def mostrar_transacoes(self):
        print("Histórico de Transações:")
        for tipo, valor, horario in self.transacoes:
            print(f"Tipo: {tipo}, Valor: {valor}, Horário: {horario.strftime('%d/%m/%Y, %H:%M')}")

def retira_sinais(texto):
    resultado = ''
    for caractere in texto:
        if caractere.isdigit():
            resultado += caractere
    return resultado

def menu_conta():
    tela = """
            Movimentação de Conta Corrente

                Selecione uma opção:
                [C]adastrar Cliente
                [I]ncluir Conta
                [P]osicionar Cliente/Conta
                [L]istar Contas

                [S]air
        => """
    return input(tela)

def menu_opcoes():
    tela = """
            Movimentação de Conta Corrente

                Selecione uma opção:
                [D]epositar
                [R]etirar
                [E]xtrato
                [T]ransações

                [V]oltar
        => """
    return input(tela)

def saldo_conta(conta):
    return sum(valor for _, valor in conta.extrato)

@imprimir_mensagem  # Aplicando o decorador
@registrar_execucao  # Aplicando o decorador
def selecionar_cliente(cpf):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

@imprimir_mensagem  # Aplicando o decorador
@registrar_execucao  # Aplicando o decorador
def selecionar_conta(cpf, numero_conta):
    cliente = selecionar_cliente(cpf)
    if cliente:
        for conta in cliente.contas:
            if conta.numero_conta == numero_conta:
                return conta
    return None

@imprimir_mensagem  # Aplicando o decorador
@registrar_execucao  # Aplicando o decorador
def listar_contas():
    print("==========================================")
    print("Início da Listagem")
    for cliente in clientes:
        for conta in cliente.contas:
            saldo = conta.saldo
            print(f"""
                Agência: {conta.agencia}
                C/C: {conta.numero_conta}
                Titular: {cliente.nome}
                Saldo: {saldo}
            """)
    print("Fim da Listagem")
    print("==========================================")

@imprimir_mensagem  # Aplicando o decorador
@registrar_execucao  # Aplicando o decorador
def criar_conta(cliente):
    if cliente:
        conta = Conta(cliente, AGENCIA)
        cliente.adicionar_conta(conta)
        return conta
    else:
        print("Cliente não cadastrado!")
    

def solicitar_numero_conta():
    while True:
        numero_conta = input("Número da conta: ")
        if numero_conta.isdigit():
            return int(numero_conta)
        else:
            print("Por favor, insira apenas números inteiros para o número da conta.")

@imprimir_mensagem  # Aplicando o decorador
@registrar_execucao  # Aplicando o decorador
def depositar(conta):
    valor = float(input("Entre com o valor do depósito: "))
    if valor > 0:
        conta.efetiva_deposito(valor)
        return valor
    else:
        print('Valor não pode ser negativo')

@imprimir_mensagem  # Aplicando o decorador
@registrar_execucao  # Aplicando o decorador
def retirar(conta):
    valor = float(input("Entre com o valor de saque: "))
    if valor < 0:
        print('Valor não pode ser negativo')
    else:
        conta.efetiva_retirada(valor)
        return valor

def listar_transacoes(conta):
    conta.historico.mostrar_transacoes()

while True:
    opcao = menu_conta().upper()

    if opcao == 'C':
        cpf = input("CPF: ")
        nome = input("Nome: ")
        data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
        rua = input("Rua: ")
        numero = input("Número: ")
        complemento = input("Complemento: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        uf = input("UF: ")
        endereco = Endereco(rua, numero, complemento, bairro, cidade, uf)
        clientes.append(Cliente(cpf, nome, data_nascimento, endereco))
        print("Cliente cadastrado com sucesso!")

    elif opcao == 'I':
        cpf = input("CPF do cliente: ")
        cliente = selecionar_cliente(cpf)
        if cliente:
            conta = criar_conta(cliente)
            if conta:
                print("Conta cadastrada com sucesso!")

    elif opcao == 'L':
        listar_contas()

    elif opcao == 'P':
        cpf = input("CPF do cliente: ")
        numero_conta = solicitar_numero_conta()
        conta = selecionar_conta(cpf, numero_conta)
        
        opcao_conta = ''
        while opcao_conta != 'V':
            opcao_conta = menu_opcoes().upper()
            if opcao_conta == 'D':
                depositar(conta)
            elif opcao_conta == 'R':
                retirar(conta)
            elif opcao_conta == 'E':                
                conta.listar_extrato()
            elif opcao_conta == 'T':
                listar_transacoes(conta)
            elif opcao_conta == 'V':
                break
            else:
                print("Opção inválida!")

    elif opcao == 'S':
        break

    else:
        print("Opção inválida!")
