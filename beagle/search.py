#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os

from cliff import lister

from beagle import hound


class Search(lister.Lister):
    """Search for a pattern and show the results.

    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--ignore-comments',
            default=False,
            action='store_true',
            help='ignore comment lines',
        )
        parser.add_argument(
            '--comment-marker',
            default='#',
            help='start of a comment line',
        )
        parser.add_argument(
            'query',
            help='the text pattern',
        )
        return parser

    def _flatten_results(self, results, parsed_args):
        for repo, repo_matches in sorted(results.items()):
            for repo_match in repo_matches['Matches']:
                for file_match in repo_match['Matches']:
                    if (parsed_args.ignore_comments and
                        file_match['Line'].lstrip().startswith(
                            parsed_args.comment_marker)):
                        continue
                    yield (repo,
                           repo_match['Filename'],
                           file_match['LineNumber'],
                           file_match['Line'].strip(),
                           file_match['Before'],
                           file_match['After'],
                           )

    def take_action(self, parsed_args):
        results = hound.query(
            self.app.options.server_url,
            parsed_args.query,
        )
        return (
            ('Repository', 'Filename', 'Line Number', 'Line', 'Before', 'After'),
            self._flatten_results(results, parsed_args),
        )