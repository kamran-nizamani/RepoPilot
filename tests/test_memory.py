from repopilot.memory import ProjectMemory

def test_memory_roundtrip(tmp_path):
    path = tmp_path / ".repopilot-memory.json"
    memory = ProjectMemory()
    memory.remember("language", "python")
    memory.save(path)
    assert ProjectMemory.load(path).facts["language"] == "python"
