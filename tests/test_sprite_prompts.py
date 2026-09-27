"""Setiap musuh punya prompt sprite (tools/sprite_prompts.json), dan sprite yang ada bernama id musuh."""
import json
from pathlib import Path

from pelita.loader import load_data

AKAR = Path(__file__).resolve().parents[1]


def test_setiap_musuh_punya_prompt_sprite():
    data = load_data()
    prompt = json.loads((AKAR / "tools" / "sprite_prompts.json").read_text(encoding="utf-8"))
    assert set(data.enemies) - set(prompt) == set()
    assert set(prompt) - set(data.enemies) == set()


def test_berkas_sprite_bernama_id_musuh():
    data = load_data()
    aset = AKAR / "pelita" / "web" / "static" / "assets" / "enemies"
    for f in aset.glob("*.webp"):
        assert f.stem in data.enemies, f"{f.name} tidak cocok dengan id musuh mana pun"


def test_url_sprite_hanya_untuk_berkas_yang_ada():
    from pelita.web.session import url_sprite
    assert url_sprite("kunang_kelam") == "/static/assets/enemies/kunang_kelam.webp"
    assert url_sprite("musuh_yang_tidak_ada") == ""
    assert url_sprite("../../app") == ""
