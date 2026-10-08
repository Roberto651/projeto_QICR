import logging
from src.core.kg import KnowledgeGraph
from src.core.engine import QICREngine
from src.scheduler.calendar import CalendarModule
from src.repository.memory import InMemoryIntentRepository
from src.domain.parser import NileParser

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

def get_massive_kg():
    """
    Constrói um Knowledge Graph hierárquico.
    - 1 Raiz (Matriz_Global)
    - 5 Setores (Setor_1 a Setor_5)
    - 25 IPs (5 IPs por setor, ex: IP_1_1 a IP_5_5)
    
    Também cria um 'Datacenter_Global' como alvo genérico.
    """
    kg = KnowledgeGraph()
    
    setores = [f"Setor_{i}" for i in range(1, 6)]
    kg.add_inclusion("Matriz_Global", setores)
    
    for i in range(1, 6):
        ips = [f"IP_{i}_{j}" for j in range(1, 6)]
        kg.add_inclusion(f"Setor_{i}", ips)
            
    # Destinos Estratégicos
    kg.add_inclusion("Datacenter_Global", ["Web_Server", "DB_Server", "App_Server"])
    
    return kg

def print_repo_status(repo):
    total = len(repo.get_all())
    print(f"\n>>> STATUS DO REPOSITÓRIO: {total} Intenções Ativas na Rede <<<")
    intents = repo.get_all()
    for intent in intents:
        print(intent)
        print("-" * 40)
    print("=" * 80 + "\n")

if __name__ == "__main__":
    setup_logger()
    
    print("\n" + "#"*80)
    print("INICIANDO SIMULAÇÃO CONTÍNUA DO MOTOR QICR (main3.py)")
    print("Topologia: 1 Raiz -> 5 Setores -> 25 IPs")
    print("#"*80 + "\n")

    kg = get_massive_kg()
    engine = QICREngine(kg)
    repo = InMemoryIntentRepository()
    calendar = CalendarModule(engine, repo)
    
    # ---------------------------------------------------------
    # JANELA 1: Intenções Independentes
    # ---------------------------------------------------------
    print("\n--- JANELA 1: Intenções Independentes (Exemplo 1) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W1_Setor1_Web:
      from endpoint('IP_1_1')
      to endpoint('Web_Server')
      allow traffic('80')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W1_Setor2_DB:
      from endpoint('IP_2_1')
      to endpoint('DB_Server')
      allow traffic('3306')
    """))
    calendar.close_time_window()
    print_repo_status(repo)
    
    # ---------------------------------------------------------
    # JANELA 2: Conflito Atômico nos Filters
    # ---------------------------------------------------------
    print("\n--- JANELA 2: Conflito Atômico nos Filters (Exemplo 2) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W2_Setor1_Web_HTTPS:
      from endpoint('IP_1_1')
      to endpoint('Web_Server')
      allow traffic('443')
    """))
    calendar.close_time_window()
    print_repo_status(repo)
    
    # ---------------------------------------------------------
    # JANELA 3: Conflito Atômico Constraints vs Filters
    # ---------------------------------------------------------
    print("\n--- JANELA 3: Conflito Atômico Constraints vs Filters (Exemplo 3) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W3_Sec_Bloqueia_80:
      from endpoint('IP_1_1')
      to endpoint('Web_Server')
      block traffic('80')
    """))
    calendar.close_time_window()
    print_repo_status(repo)
    
    # ---------------------------------------------------------
    # JANELA 4: Conflito Atômico em SFC
    # ---------------------------------------------------------
    print("\n--- JANELA 4: Conflito Atômico em SFC (Exemplo 4) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W4_Setor2_DB_FW_LB:
      from endpoint('IP_2_1')
      to endpoint('DB_Server')
      add middlebox('FW'), middlebox('LB')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W4_Setor2_DB_IDS_FW:
      from endpoint('IP_2_1')
      to endpoint('DB_Server')
      add middlebox('IDS'), middlebox('FW')
    """))
    calendar.close_time_window()
    print_repo_status(repo)

    # ---------------------------------------------------------
    # JANELA 5: Conflito Atômico Total (Filters, Constraints, SFC)
    # ---------------------------------------------------------
    print("\n--- JANELA 5: Conflito Atômico Total (Exemplo 5) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W5_Dev_Total:
      from endpoint('IP_3_1')
      to endpoint('App_Server')
      add middlebox('FW')
      allow traffic('80'), traffic('443')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W5_Sec_Total:
      from endpoint('IP_3_1')
      to endpoint('App_Server')
      add middlebox('VPN'), middlebox('IDS')
      block traffic('80')
    """))
    calendar.close_time_window()
    print_repo_status(repo)

    # ---------------------------------------------------------
    # JANELA 6: Conflito Não-Atômico em Filters
    # ---------------------------------------------------------
    print("\n--- JANELA 6: Conflito Não-Atômico em Filters (Exemplo 6) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W6_Setor4_Libera:
      from group('Setor_4')
      to endpoint('Web_Server')
      allow traffic('80')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W6_IP_Especifico_Libera:
      from endpoint('IP_4_1')
      to endpoint('Web_Server')
      allow traffic('3306')
    """))
    calendar.close_time_window()
    print_repo_status(repo)

    # ---------------------------------------------------------
    # JANELA 7: Conflito Não-Atômico Constraints vs Filters
    # ---------------------------------------------------------
    print("\n--- JANELA 7: Conflito Não-Atômico Constraints vs Filters (Exemplo 7) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W7_Setor5_Libera_App:
      from group('Setor_5')
      to endpoint('App_Server')
      allow traffic('8080')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W7_IP5_Bloqueia_App:
      from endpoint('IP_5_1')
      to endpoint('App_Server')
      block traffic('8080')
    """))
    calendar.close_time_window()
    print_repo_status(repo)

    # ---------------------------------------------------------
    # JANELA 8: Conflito Não-Atômico em SFC
    # ---------------------------------------------------------
    print("\n--- JANELA 8: Conflito Não-Atômico em SFC (Exemplo 8) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W8_Matriz_SFC_Basica:
      from group('Matriz_Global')
      to endpoint('DB_Server')
      add middlebox('FW')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W8_Setor1_SFC_Segura:
      from group('Setor_1')
      to endpoint('DB_Server')
      add middlebox('IDS')
    """))
    calendar.close_time_window()
    print_repo_status(repo)

    # ---------------------------------------------------------
    # JANELA 9: Conflito Não-Atômico Total (A Grande Decomposição)
    # ---------------------------------------------------------
    print("\n--- JANELA 9: Conflito Não-Atômico Total (Exemplo 9) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W9_Regra_Matriz_Global:
      from group('Matriz_Global')
      to endpoint('Web_Server')
      add middlebox('FW')
      allow traffic('80')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W9_Regra_Setor2_Bloqueio:
      from group('Setor_2')
      to endpoint('Web_Server')
      add middlebox('VPN')
      block traffic('80')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W9_Excecao_IP_2_2:
      from endpoint('IP_2_2')
      to endpoint('Web_Server')
      add middlebox('WAF')
      allow traffic('443')
    """))
    calendar.close_time_window()
    print_repo_status(repo)

    # ---------------------------------------------------------
    # JANELA 10: Ordem de Pesos Iguais (IDS vs IPS)
    # ---------------------------------------------------------
    print("\n--- JANELA 10: Ordem de Pesos Iguais (Exemplo 10) ---")
    calendar.declare_intent(NileParser.parse("""
    define intent W10_Admin_A:
      from endpoint('IP_5_5')
      to endpoint('DB_Server')
      add middlebox('FW'), middlebox('IDS')
    """))
    calendar.declare_intent(NileParser.parse("""
    define intent W10_Admin_B:
      from endpoint('IP_5_5')
      to endpoint('DB_Server')
      add middlebox('FW'), middlebox('IPS'), middlebox('IDS')
    """))
    calendar.close_time_window()
    print_repo_status(repo)
    
    print("\n[SIMULAÇÃO CONCLUÍDA COM SUCESSO]")
