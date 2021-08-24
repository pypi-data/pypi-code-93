# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from collections import OrderedDict

from contrast.agent.protect.rule.cmdi_rule import CmdInjection
from contrast.agent.protect.rule.deserialization_rule import Deserialization
from contrast.agent.protect.rule.http_method_tampering import MethodTampering
from contrast.agent.protect.rule.malformed_header import MalformedHeader
from contrast.agent.protect.rule.nosqli_rule import NoSqlInjection
from contrast.agent.protect.rule.path_traversal_rule import PathTraversal
from contrast.agent.protect.rule.sqli_rule import SqlInjection
from contrast.agent.protect.rule.ssrf_rule import Ssrf
from contrast.agent.protect.rule.unsafe_file_upload_rule import UnsafeFileUpload
from contrast.agent.protect.rule.xss_rule import Xss
from contrast.agent.protect.rule.xxe_rule import Xxe


class RulesBuilder(object):
    """
    Combines all rules
    """

    @staticmethod
    def build_protect_rules(settings):
        """
        Build a dict with rules with prefilter rules first.
        We want prefilter rules first so they get evaluated / trigger first.
        :param settings:
        :return: an ordered dict of protect rules
        """
        rules = OrderedDict(
            {
                UnsafeFileUpload.NAME: UnsafeFileUpload(settings),
                CmdInjection.NAME: CmdInjection(settings),
                Deserialization.NAME: Deserialization(settings),
                # Turned off until TS can handle rule information
                MalformedHeader.NAME: MalformedHeader(settings),
                MethodTampering.NAME: MethodTampering(settings),
                NoSqlInjection.NAME: NoSqlInjection(settings),
                # Padding Oracle rule is currently disabled - CONTRAST-35352
                # PaddingOracle.NAME: PaddingOracle(settings),
                PathTraversal.NAME: PathTraversal(settings),
                SqlInjection.NAME: SqlInjection(settings),
                Ssrf.NAME: Ssrf(settings),
                Xss.NAME: Xss(settings),
                Xxe.NAME: Xxe(settings),
            }
        )

        return rules
