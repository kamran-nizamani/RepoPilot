from repopilot.generator import parse_generated_patches

def test_parse_generated_patch():
    text = "FILE: app.py\n```python\nx = 2\n```"
    patches = parse_generated_patches(text)
    assert patches[0].path == "app.py"
    assert patches[0].content == "x = 2\n"
