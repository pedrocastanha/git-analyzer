from src.core.state import GraphState


def route_after_diff(state: GraphState):
    current_action = state.get("current_action")
    diff = state.get("diff")

    if not diff:
        return "end"

    if current_action == "analyze":
        return "analyze_code"
    elif current_action == "deep_analyze":
        return "deep_analyze_critic"
    elif current_action == "commit":
        return "generate_commit"
    else:
        return "end"

def route_deep_analysis(state: GraphState):
    if state.get('error'):
        print(f"❌ Erro detectado: {state['error']}")
        print("Abortando discussão...\n")
        return "deep_generate_improvements"

    conversation_history = state.get("conversation_history", [])

    if len(conversation_history) >= 8:
        print("⏱️  Limite de 8 mensagens atingido. Finalizando discussão...")
        return "deep_generate_improvements"

    if len(conversation_history) >= 2:
        critic_messages = [msg for msg in conversation_history
                          if hasattr(msg, 'name') and msg.name == "Crítico de Segurança e Padrões"]
        constructive_messages = [msg for msg in conversation_history
                                if hasattr(msg, 'name') and msg.name == "Construtivo de Lógica e Desempenho"]

        if critic_messages and constructive_messages:
            last_critic = critic_messages[-1]
            last_constructive = constructive_messages[-1]

            critic_agreed = "AGREEMENT" in str(last_critic.content).upper()
            constructive_agreed = "AGREEMENT" in str(last_constructive.content).upper()

            if critic_agreed and constructive_agreed:
                print("🤝 ACORDO MÚTUO detectado!")
                print("   🔴 Crítico concordou ✓")
                print("   🟢 Construtivo concordou ✓")
                print("   Finalizando discussão...\n")
                return "deep_generate_improvements"

    last_message = conversation_history[-1] if conversation_history else None

    if last_message and hasattr(last_message, 'name'):
        agent_name = last_message.name
        print(f"🔄 Último agente: {agent_name}")

        if agent_name == "Crítico de Segurança e Padrões":
            print("➡️  Próximo: Agente Construtivo\n")
            return "deep_analyze_constructive"
        else:
            print("➡️  Próximo: Agente Crítico\n")
            return "deep_analyze_critic"
    else:
        print("🔴 Iniciando com Agente Crítico\n")
        return "deep_analyze_critic"
