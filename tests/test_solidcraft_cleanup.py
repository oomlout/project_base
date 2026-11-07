"""Exercise cleanup only inside disposable copies, never against project parts."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == 'nt', 'Windows batch cleanup')
class SolidCraftCleanupTests(unittest.TestCase):
    def fixture(self, root):
        shutil.copyfile(PROJECT / 'action_delete_solidcraft_files.bat', root / 'action_delete_solidcraft_files.bat')
        helper = root / 'components/solidcraft_cleanup'
        helper.mkdir(parents=True)
        shutil.copyfile(PROJECT / 'components/solidcraft_cleanup/working.ps1', helper / 'working.ps1')
        part = root / 'parts/part [one]'
        part.mkdir(parents=True)
        generated = []
        for mode in ('true', '3dpr'):
            for suffix in ('.solidcraft', '.step', '_solidcraft.stl', '_solidcraft.png', '_solidcraft_manifest.json', '_solidcraft_exports_manifest.json'):
                target = part / (mode + suffix)
                target.write_bytes(b'generated fixture')
                generated.append(target)
        preserved = [part / 'working.yaml', part / 'true.scad', part / 'true.stl', part / 'custom.solidcraft',
                     part / 'manual/true.solidcraft', root / 'parts/sealed/SEALED.json',
                     root / 'parts/sealed/true.solidcraft', root / 'build/solidcraft/runs/attempts/old/generated.solidcraft']
        for target in preserved:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'preserved fixture')
        return generated, preserved

    def run_batch(self, root, *options):
        return subprocess.run([os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/c',
                               str(root / 'action_delete_solidcraft_files.bat'), *options],
                              cwd=root.parent, capture_output=True, text=True, timeout=30)

    def test_batch_preview_and_cleanup_preserve_unrelated_files(self):
        with tempfile.TemporaryDirectory(prefix='solidcraft cleanup ') as temporary:
            root = Path(temporary)
            generated, preserved = self.fixture(root)
            preview = self.run_batch(root, '-DryRun')
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertIn('Nothing deleted', preview.stdout)
            self.assertTrue(all(p.exists() for p in generated + preserved))
            cleaned = self.run_batch(root)
            self.assertEqual(cleaned.returncode, 0, cleaned.stdout + cleaned.stderr)
            self.assertTrue(all(not p.exists() for p in generated))
            self.assertTrue(all(p.read_bytes() == b'preserved fixture' for p in preserved))
            again = self.run_batch(root)
            self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
            self.assertIn('Deleted 0 generated', again.stdout)

    def test_active_build_lock_prevents_all_deletion(self):
        import msvcrt
        with tempfile.TemporaryDirectory(prefix='solidcraft cleanup ') as temporary:
            root = Path(temporary)
            generated, preserved = self.fixture(root)
            guard = root / 'build/solidcraft/.writer.guard'
            with guard.open('w+b') as stream:
                stream.write(b'0')
                stream.flush()
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                try:
                    result = self.run_batch(root)
                finally:
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('currently building', result.stderr)
            self.assertTrue(all(p.exists() for p in generated + preserved))
