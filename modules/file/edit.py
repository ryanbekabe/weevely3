from core.vectors import PhpCmd, ShellCmd, ModuleCmd, Os
from core.module import Module
from core.loggers import log
from core import modules
from core import messages
import tempfile
import subprocess
import hashlib
import base64
import re

class Edit(Module):

    """Edit remote file."""

    def init(self):

        self.register_info(
            {
                'author': [
                    'Emilio Pinna'
                ],
                'license': 'GPLv3'
            }
        )

        self.register_arguments([
          { 'name' : 'rpath', 'help' : 'Remote file path' },
          { 'name' : '-vector', 'choices' : modules.loaded['file_download'].vectors.get_names() },
          { 'name' : '-keep-ts', 'action' : 'store_true', 'default' : False },
          { 'name' : '-editor', 'help' : 'Choose editor', 'default' : 'vim' }
        ])

    def run(self, args):

        # Get a temporary file name
        suffix = re.sub('[\W]+', '_', args['rpath'])
        temp_file = tempfile.NamedTemporaryFile(suffix = suffix)
        lpath = temp_file.name

        # If remote file already exists and readable
        if ModuleCmd(
                    'file_check',
                    [ args.get('rpath'), 'readable' ]
                ).run():

            # Download file
            result_download = ModuleCmd(
                        'file_download',
                        [ args.get('rpath'), lpath ]
                    ).run()

            # Exit with no result
            # The error should already been printed by file_download exec
            if result_download == None: return

            # Store original md5
            md5_orig = hashlib.md5(open(lpath, 'rb').read()).hexdigest()

            # Run editor
            subprocess.check_call( [ args['editor'], lpath ])

            # With no changes, just return
            if md5_orig == hashlib.md5(open(lpath, 'rb').read()).hexdigest():
                log.debug(messages.module_file_edit.unmodified_file)
                temp_file.close()
                return

        else:
            subprocess.check_call( [ args['editor'], lpath ])

        # Upload file
        result_upload = ModuleCmd(
                    'file_upload',
                    [ '-force', lpath, args.get('rpath') ]
                ).run()

        # Delete temp file
        temp_file.close()

        return result_upload