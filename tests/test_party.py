import pytest

from pelita.loader import load_data
from pelita.party import Hero, stats_at_level, xp_for_next, xp_to_reach


@pytest.fixture(scope="module")
def data():
    return load_data()


def test_kurva_xp():
    assert xp_to_reach(1) == 0
    assert xp_to_reach(2) == 80
    assert xp_for_next(1) == 80
    assert xp_for_next(9) == 2000          # 20·10²


def test_pertumbuhan_deterministik(data):
    rimba = data.character("rimba")
    lv1 = stats_at_level(rimba, 1)
    assert (lv1.hp, lv1.atk) == (45, 8)
    lv2 = stats_at_level(rimba, 2)
    assert lv2.hp == 52 and lv2.atk == 9    # 8 + 1.6 → 9
    assert stats_at_level(rimba, 6).atk == 16  # 8 + 1.6·5 = 16.0


def test_skill_terbuka_sesuai_level(data):
    h = Hero.create(data, "rimba", 5)
    assert [s.id for s in h.skills()] == ["sulut", "sinar_lentera"]
    h = Hero.create(data, "rimba", 6)
    assert "kobar" in [s.id for s in h.skills()]


def test_naik_level_memulihkan(data):
    h = Hero.create(data, "sela", 1)
    h.hp = 10
    gained = h.gain_xp(xp_to_reach(3))
    assert gained == [2, 3]
    assert h.level == 3
    assert h.hp > 10
    assert h.hp <= h.max_hp
