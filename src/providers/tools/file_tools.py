import os
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool


_current_repo_path: str = "."


def set_repo_path(repo_path: str):
    global _current_repo_path
    _current_repo_path = repo_path


def get_full_path(relative_path: str) -> Path:
    return Path(_current_repo_path) / relative_path


@tool
def read_file(file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Lê o conteúdo de um arquivo do repositório.

    Retorna o conteúdo com números de linha formatados.
    Pode ler o arquivo inteiro ou apenas um intervalo de linhas.

    Args:
        file_path: Caminho do arquivo relativo ao repositório
        start_line: Linha inicial para leitura (opcional, 1-indexed)
        end_line: Linha final para leitura (opcional, 1-indexed)

    Returns:
        Conteúdo do arquivo formatado com números de linha
    """
    full_path = get_full_path(file_path)

    if not full_path.exists():
        return f"❌ Arquivo não encontrado: {file_path}"

    if not full_path.is_file():
        return f"❌ Não é um arquivo: {file_path}"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if start_line is not None or end_line is not None:
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else len(lines)
            lines = lines[start_idx:end_idx]
            line_offset = start_idx
        else:
            line_offset = 0

        formatted_lines = []
        for i, line in enumerate(lines, start=line_offset + 1):
            formatted_lines.append(f"{i:4d} | {line.rstrip()}")

        return "\n".join(formatted_lines)

    except Exception as e:
        return f"❌ Erro ao ler arquivo: {e}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Escreve conteúdo em um arquivo (substitui todo o conteúdo).

    IMPORTANTE: Esta operação substitui TODO o conteúdo do arquivo.
    Use edit_file para modificações parciais.

    Args:
        file_path: Caminho do arquivo relativo ao repositório
        content: Novo conteúdo completo do arquivo

    Returns:
        Mensagem de sucesso ou erro
    """
    full_path = get_full_path(file_path)

    full_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        backup_content = None
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        lines_count = len(content.split('\n'))
        return f"✅ Arquivo escrito com sucesso: {file_path} ({lines_count} linhas)"

    except Exception as e:
        return f"❌ Erro ao escrever arquivo: {e}"


@tool
def edit_file(file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    """
    Edita um arquivo substituindo texto específico.

    Esta é a forma RECOMENDADA de fazer edições:
    - Encontra 'old_string' no arquivo
    - Substitui por 'new_string'
    - Preserva o resto do arquivo

    Args:
        file_path: Caminho do arquivo relativo ao repositório
        old_string: Texto exato a ser substituído
        new_string: Novo texto que substituirá o antigo
        replace_all: Se True, substitui TODAS as ocorrências

    Returns:
        Mensagem de sucesso com detalhes da edição
    """
    full_path = get_full_path(file_path)

    if not full_path.exists():
        return f"❌ Arquivo não encontrado: {file_path}"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        occurrences = content.count(old_string)

        if occurrences == 0:
            return f"❌ Texto não encontrado no arquivo: '{old_string[:50]}...'"

        if occurrences > 1 and not replace_all:
            return f"⚠️ Múltiplas ocorrências ({occurrences}) encontradas. Use replace_all=True para substituir todas, ou forneça mais contexto."

        if replace_all:
            new_content = content.replace(old_string, new_string)
            replaced_count = occurrences
        else:
            new_content = content.replace(old_string, new_string, 1)
            replaced_count = 1

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"✅ Editado {file_path}: {replaced_count} substituição(ões) feita(s)"

    except Exception as e:
        return f"❌ Erro ao editar arquivo: {e}"


@tool
def list_files(directory: str = ".", pattern: str = "*") -> str:
    """
    Lista arquivos em um diretório.

    Args:
        directory: Diretório relativo ao repositório (padrão: raiz)
        pattern: Padrão glob para filtrar (ex: "*.py", "**/*.js")

    Returns:
        Lista de arquivos encontrados
    """
    full_path = get_full_path(directory)

    if not full_path.exists():
        return f"❌ Diretório não encontrado: {directory}"

    try:
        if "**" in pattern:
            files = list(full_path.glob(pattern))
        else:
            files = list(full_path.glob(pattern))

        files = [f for f in files if f.is_file()]

        files = [f for f in files if ".git" not in str(f)]

        if len(files) > 100:
            files = files[:100]
            truncated = True
        else:
            truncated = False

        result = []
        for f in sorted(files):
            rel_path = f.relative_to(get_full_path("."))
            size = f.stat().st_size
            result.append(f"  {rel_path} ({size} bytes)")

        output = f"📁 {len(files)} arquivo(s) encontrado(s):\n" + "\n".join(result)

        if truncated:
            output += "\n\n⚠️ Resultados truncados (máx 100)"

        return output

    except Exception as e:
        return f"❌ Erro ao listar arquivos: {e}"


@tool
def search_in_files(pattern: str, file_pattern: str = "*.py", directory: str = ".") -> str:
    """
    Busca um padrão de texto em arquivos.

    Args:
        pattern: Texto ou regex para buscar
        file_pattern: Padrão glob para filtrar arquivos (ex: "*.py")
        directory: Diretório para buscar

    Returns:
        Lista de ocorrências com arquivo:linha:conteúdo
    """
    import re

    full_path = get_full_path(directory)

    if not full_path.exists():
        return f"❌ Diretório não encontrado: {directory}"

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        regex = re.compile(re.escape(pattern), re.IGNORECASE)

    results = []
    files_searched = 0

    try:
        for file_path in full_path.glob(f"**/{file_pattern}"):
            if not file_path.is_file() or ".git" in str(file_path):
                continue

            files_searched += 1

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            rel_path = file_path.relative_to(get_full_path("."))
                            results.append(f"{rel_path}:{line_num}: {line.strip()[:80]}")

                            if len(results) >= 50:
                                break

            except Exception:
                continue

            if len(results) >= 50:
                break

        if not results:
            return f"🔍 Nenhuma ocorrência de '{pattern}' encontrada em {files_searched} arquivo(s)"

        output = f"🔍 {len(results)} ocorrência(s) de '{pattern}':\n\n"
        output += "\n".join(results)

        if len(results) >= 50:
            output += "\n\n⚠️ Resultados truncados (máx 50)"

        return output

    except Exception as e:
        return f"❌ Erro na busca: {e}"


@tool
def create_file(file_path: str, content: str = "") -> str:
    """
    Cria um novo arquivo.

    Args:
        file_path: Caminho do arquivo relativo ao repositório
        content: Conteúdo inicial (opcional)

    Returns:
        Mensagem de sucesso ou erro
    """
    full_path = get_full_path(file_path)

    if full_path.exists():
        return f"⚠️ Arquivo já existe: {file_path}. Use write_file para sobrescrever."

    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"✅ Arquivo criado: {file_path}"

    except Exception as e:
        return f"❌ Erro ao criar arquivo: {e}"


@tool
def delete_lines(file_path: str, start_line: int, end_line: int) -> str:
    """
    Remove linhas específicas de um arquivo.

    Args:
        file_path: Caminho do arquivo relativo ao repositório
        start_line: Primeira linha a remover (1-indexed)
        end_line: Última linha a remover (1-indexed, inclusivo)

    Returns:
        Mensagem de sucesso com detalhes
    """
    full_path = get_full_path(file_path)

    if not full_path.exists():
        return f"❌ Arquivo não encontrado: {file_path}"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)

        if start_line < 1 or end_line > total_lines or start_line > end_line:
            return f"❌ Intervalo inválido. Arquivo tem {total_lines} linhas."

        deleted_lines = lines[start_line - 1:end_line]
        new_lines = lines[:start_line - 1] + lines[end_line:]

        with open(full_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        deleted_count = end_line - start_line + 1
        return f"✅ Removidas {deleted_count} linha(s) de {file_path} (linhas {start_line}-{end_line})"

    except Exception as e:
        return f"❌ Erro ao remover linhas: {e}"


@tool
def insert_lines(file_path: str, after_line: int, content: str) -> str:
    """
    Insere novas linhas após uma linha específica.

    Args:
        file_path: Caminho do arquivo relativo ao repositório
        after_line: Número da linha após a qual inserir (0 = início do arquivo)
        content: Conteúdo a inserir (pode ter múltiplas linhas)

    Returns:
        Mensagem de sucesso com detalhes
    """
    full_path = get_full_path(file_path)

    if not full_path.exists():
        return f"❌ Arquivo não encontrado: {file_path}"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)

        if after_line < 0 or after_line > total_lines:
            return f"❌ Linha inválida. Arquivo tem {total_lines} linhas (use 0 para inserir no início)."

        if content and not content.endswith('\n'):
            content += '\n'

        new_content_lines = content.splitlines(keepends=True)
        new_lines = lines[:after_line] + new_content_lines + lines[after_line:]

        with open(full_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        inserted_count = len(new_content_lines)
        return f"✅ Inseridas {inserted_count} linha(s) em {file_path} após linha {after_line}"

    except Exception as e:
        return f"❌ Erro ao inserir linhas: {e}"


file_tools = [
    read_file,
    write_file,
    edit_file,
    list_files,
    search_in_files,
    create_file,
    delete_lines,
    insert_lines,
]
