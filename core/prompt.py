def get_system_prompt() -> str:
    with open("prompts/system_hardware_expert.txt", "r", encoding="utf-8") as f:
        return f.read().strip()