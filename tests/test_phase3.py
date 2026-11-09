"""Reglas de seguridad y contrato del generador sin red ni almacenamiento."""
import unittest
from types import SimpleNamespace
from backend.generator import generate, parse_ports


def case(**changes):
    data = dict(model="Catalyst 2960", version="15.0(2)SE", groups=[
        SimpleNamespace(name="Administración", vlan="10", ports="Fa0/1, Fa0/2"),
        SimpleNamespace(name="Laboratorio", vlan="20", ports="Gi0/1")])
    data.update(changes)
    return SimpleNamespace(**data)


class GeneratorTests(unittest.TestCase):
    def test_reference_commands_and_limits(self):
        result = generate(case())
        self.assertEqual(result["status"], "proposed")
        self.assertFalse(result["lab_verified"])
        self.assertIn("interface FastEthernet0/1\nswitchport mode access\nswitchport access vlan 10", result["commands"])
        self.assertIn("interface GigabitEthernet0/1\nswitchport mode access\nswitchport access vlan 20", result["commands"])
        self.assertTrue(result["commands"].endswith("end"))
        self.assertNotIn("startup-config", result["commands"])
        self.assertEqual(len(result["checks"]), 5)

    def test_missing_data_blocks_commands(self):
        result = generate(case(model=" "))
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(result["missing"])
        self.assertEqual(result["commands"], "")

    def test_ios_version_is_not_required(self):
        result = generate(case(version=""))
        self.assertEqual(result["status"], "proposed")
        self.assertTrue(result["commands"])
        legacy = case()
        del legacy.version
        self.assertEqual(generate(legacy)["status"], "proposed")

    def test_vlan_bounds_and_conflicts(self):
        for vlan in ["1", "1002", "4094", "-1", "1e1", "10\nexit"]:
            c = case(); c.groups[0].vlan = vlan
            self.assertEqual(generate(c)["status"], "invalid")
        c = case(); c.groups[1].vlan = "0010"
        self.assertEqual(generate(c)["status"], "invalid")

    def test_aliases_cannot_hide_port_conflicts(self):
        c = case(); c.groups[1].ports = "fastethernet0/1"
        self.assertEqual(generate(c)["status"], "invalid")
        with self.assertRaises(ValueError):
            parse_ports("Fa0/1, FastEthernet0/1")

    def test_malformed_ports_and_command_injection(self):
        for ports in ["Fa0/1-4", "Fa0/1\nshutdown", "Fa0/0", "Fa00/1", "Fa0/1,", "Gi0/1;reload"]:
            with self.subTest(ports=ports), self.assertRaises(ValueError):
                parse_ports(ports)

    def test_group_labels_do_not_enter_cli(self):
        c = case(); c.groups[0].name = "X\nreload"
        self.assertNotIn("reload", generate(c)["commands"])
