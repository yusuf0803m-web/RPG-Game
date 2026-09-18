import json

import pytest

from pelita.loader import DataError, load_data
from pelita.models import Affinity, CostType, Element


def test_data_bawaan_valid():
    d = load_data()
    assert "rimba" in d.characters
    assert d.enemy("serigala_kabut").affinity(Element.API) == Affinity.LEMAH
    assert d.enemy("serigala_kabut").affinity(Element.PETIR) == Affinity.NORMAL
    assert d.skill("nyala_pulih").cost_type == CostType.BARA


def test_rujukan_skill_rusak_terdeteksi(tmp_path):
    src = load_data.__globals__["DATA_DIR"]
    for f in ("skills.json", "characters.json", "enemies.json", "items.json"):
        (tmp_path / f).write_text((src / f).read_text(encoding="utf-8"), encoding="utf-8")
    chars = json.loads((tmp_path / "characters.json").read_text())
    chars["rimba"]["skills"].append("skill_tidak_ada")
    (tmp_path / "characters.json").write_text(json.dumps(chars))
    with pytest.raises(DataError):
        load_data(tmp_path, use_cache=False)
