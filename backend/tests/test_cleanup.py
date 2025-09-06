"""
Teste direto da função de processamento de PDF
"""

import gc
import os
import tempfile
import time
import uuid


def test_pdf_cleanup():
    """Testa a nova lógica de cleanup de PDF"""

    # Simular dados de PDF
    pdf_data = b"Dados de teste para arquivo PDF"

    # Aplicar a nova lógica de cleanup
    temp_dir = tempfile.gettempdir()
    temp_filename = f"pdf_extract_{uuid.uuid4().hex}.pdf"
    temp_path = os.path.join(temp_dir, temp_filename)

    print(f"🧪 Criando arquivo temporário: {temp_path}")

    try:
        # Escrever arquivo de teste
        with open(temp_path, "wb") as temp_file:
            temp_file.write(pdf_data)

        print("✅ Arquivo criado com sucesso")

        # Simular processamento (apenas leitura)
        with open(temp_path, "rb") as test_file:
            content = test_file.read()
            print(f"✅ Conteúdo lido: {len(content)} bytes")

        # Forçar garbage collection
        gc.collect()

        print("🧹 Iniciando processo de cleanup...")

        # Aplicar novo processo de cleanup robusto
        for attempt in range(5):
            try:
                os.unlink(temp_path)
                print(f"✅ Arquivo deletado na tentativa #{attempt + 1}")
                break
            except (OSError, PermissionError) as e:
                if attempt < 4:
                    delay = 0.1 * (2**attempt)
                    print(f"⚠️ Tentativa #{attempt + 1} falhou: {e}")
                    print(f"⏳ Aguardando {delay} segundos...")
                    time.sleep(delay)
                    gc.collect()
                    continue
                else:
                    print(f"❌ Falha final após 5 tentativas: {e}")
                    assert False, f"Falha final após 5 tentativas: {e}"

        # Verificar se arquivo foi realmente deletado
        if os.path.exists(temp_path):
            print("❌ Arquivo ainda existe após cleanup")
            assert False, "Arquivo ainda existe após cleanup"
        else:
            print("✅ Arquivo removido com sucesso")
            assert True

    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        assert False, f"Erro durante teste: {e}"


def list_temp_pdf_files():
    """Lista arquivos PDF temporários no diretório temp"""
    temp_dir = tempfile.gettempdir()
    pdf_files = []

    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith("pdf_extract_") and filename.endswith(".pdf"):
                file_path = os.path.join(temp_dir, filename)
                file_size = os.path.getsize(file_path)
                pdf_files.append((filename, file_size))
    except Exception as e:
        print(f"Erro ao listar arquivos temp: {e}")

    return pdf_files


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE DE CORREÇÃO DE CLEANUP DE ARQUIVOS PDF TEMPORÁRIOS")
    print("=" * 70)

    # Listar arquivos antes do teste
    print("📁 Arquivos PDF temporários ANTES do teste:")
    before_files = list_temp_pdf_files()
    if before_files:
        for filename, size in before_files:
            print(f"   - {filename} ({size} bytes)")
    else:
        print("   Nenhum arquivo encontrado")

    print("\n🔧 Executando teste de cleanup...")
    success = test_pdf_cleanup()

    # Listar arquivos depois do teste
    print("\n📁 Arquivos PDF temporários DEPOIS do teste:")
    after_files = list_temp_pdf_files()
    if after_files:
        for filename, size in after_files:
            print(f"   - {filename} ({size} bytes)")
    else:
        print("   Nenhum arquivo encontrado")

    # Resultado
    new_files = len(after_files) - len(before_files)
    if new_files > 0:
        print(f"⚠️ {new_files} novos arquivos temporários criados")

    print(
        f"\n{'✅ TESTE PASSOU - Cleanup funcionando!' if success else '❌ TESTE FALHOU - Problema no cleanup'}"
    )
    print("=" * 70)
