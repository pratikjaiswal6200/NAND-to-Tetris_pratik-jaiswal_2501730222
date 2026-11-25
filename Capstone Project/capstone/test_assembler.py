import unittest

from assembler import assemble


class AssembleRomCapacityTests(unittest.TestCase):
    def test_accepts_full_rom(self):
        source = "\n".join("@0" for _ in range(1 << 15))

        self.assertEqual(len(assemble(source)), 1 << 15)

    def test_rejects_instruction_past_rom_capacity(self):
        source = "\n".join("@0" for _ in range((1 << 15) + 1))

        with self.assertRaisesRegex(ValueError, "ROM address space exhausted"):
            assemble(source)

    def test_rejects_label_at_unrepresentable_rom_address(self):
        source = "\n".join(["@0"] * (1 << 15) + ["(END)"])

        with self.assertRaisesRegex(ValueError, "label address exceeds ROM capacity"):
            assemble(source)
