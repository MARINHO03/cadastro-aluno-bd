import psycopg2

# ====== CONFIGURE AQUI ======
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_SENHA = "SUA_SENHA_AQUI"
DB_NOME = "cadastro_alunos"
# ============================


def conectar(banco=DB_NOME):
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_SENHA, dbname=banco
    )


def criar_banco_e_tabela():
    # cria o banco automaticamente, se ainda não existir
    conn = conectar("postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NOME,))
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {DB_NOME}")
    cur.close()
    conn.close()

    # cria a tabela, se ainda não existir
    conn = conectar()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS alunos (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    idade INTEGER NOT NULL,
                    nota REAL NOT NULL
                )
                """
            )
    conn.close()


def executar(sql, params=(), buscar=None):
    """Executa um comando SQL parametrizado.
    buscar: None (sem retorno), 'um', 'todos' ou 'linhas' (rowcount)."""
    conn = conectar()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if buscar == "um":
                    return cur.fetchone()
                if buscar == "todos":
                    return cur.fetchall()
                if buscar == "linhas":
                    return cur.rowcount
    finally:
        conn.close()


# ---------- validações ----------
def ler_nome(msg="Nome: "):
    while True:
        nome = input(msg).strip()
        if nome:
            return nome
        print("Nome não pode ser vazio.")


def ler_idade(msg="Idade: "):
    while True:
        try:
            idade = int(input(msg))
            if 0 < idade < 120:
                return idade
            print("Idade inválida.")
        except ValueError:
            print("Digite um número inteiro.")


def ler_nota(msg="Nota (0 a 10): "):
    while True:
        try:
            nota = float(input(msg).replace(",", "."))
            if 0 <= nota <= 10:
                return nota
            print("A nota deve estar entre 0 e 10.")
        except ValueError:
            print("Digite um número válido.")


def ler_id(msg="ID do aluno: "):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Digite um número inteiro.")


# ---------- operações ----------
def cadastrar_aluno():
    nome = ler_nome()
    idade = ler_idade()
    nota = ler_nota()
    executar(
        "INSERT INTO alunos (nome, idade, nota) VALUES (%s, %s, %s)",
        (nome, idade, nota),
    )
    print("Aluno cadastrado com sucesso!")


def mostrar(alunos):
    for id_, nome, idade, nota in alunos:
        print(f"ID: {id_} | Nome: {nome} | Idade: {idade} | Nota: {nota:.1f}")


def listar_alunos():
    alunos = executar(
        "SELECT id, nome, idade, nota FROM alunos ORDER BY id", buscar="todos"
    )
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    mostrar(alunos)


def buscar_aluno():
    nome = ler_nome("Nome para buscar: ")
    alunos = executar(
        "SELECT id, nome, idade, nota FROM alunos WHERE nome ILIKE %s",
        (f"%{nome}%",),
        buscar="todos",
    )
    if not alunos:
        print("Nenhum aluno encontrado com esse nome.")
        return
    mostrar(alunos)


def atualizar_aluno():
    id_ = ler_id()
    aluno = executar("SELECT id FROM alunos WHERE id = %s", (id_,), buscar="um")
    if not aluno:
        print("Aluno não encontrado.")
        return
    nome = ler_nome("Novo nome: ")
    idade = ler_idade("Nova idade: ")
    nota = ler_nota("Nova nota (0 a 10): ")
    executar(
        "UPDATE alunos SET nome = %s, idade = %s, nota = %s WHERE id = %s",
        (nome, idade, nota, id_),
    )
    print("Aluno atualizado com sucesso!")


def remover_aluno():
    id_ = ler_id()
    linhas = executar("DELETE FROM alunos WHERE id = %s", (id_,), buscar="linhas")
    if linhas:
        print("Aluno removido com sucesso!")
    else:
        print("Aluno não encontrado.")


def media_geral():
    media = executar("SELECT AVG(nota) FROM alunos", buscar="um")[0]
    if media is None:
        print("Nenhum aluno cadastrado.")
    else:
        print(f"Média geral das notas: {media:.2f}")


# ---------- menu ----------
def menu():
    print("\n=== Sistema de Cadastro de Alunos ===")
    print("1. Cadastrar aluno")
    print("2. Listar todos os alunos")
    print("3. Buscar aluno pelo nome")
    print("4. Atualizar dados de um aluno")
    print("5. Remover aluno")
    print("6. Mostrar média geral das notas")
    print("7. Sair")


def main():
    try:
        criar_banco_e_tabela()
    except psycopg2.Error as e:
        print("Erro ao conectar no PostgreSQL. Confira usuário, senha e se o servidor está ligado.")
        print(e)
        return

    acoes = {
        "1": cadastrar_aluno,
        "2": listar_alunos,
        "3": buscar_aluno,
        "4": atualizar_aluno,
        "5": remover_aluno,
        "6": media_geral,
    }
    while True:
        menu()
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "7":
            print("Saindo...")
            break
        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()