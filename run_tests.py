#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run tests for the ActiveTableXBlock.

This script is required to run the Selenium tests inside the xblock-sdk workbench
because the workbench SDK's settings file is not inside any python module.
"""

from __future__ import absolute_import

import os
import logging
import sys

from django.conf import settings
from django.core.management import execute_from_command_line
import six

logging_level_overrides = {
    'workbench.views': logging.ERROR,
    'django.request': logging.ERROR,
    'workbench.runtime': logging.ERROR,
}

if __name__ == '__main__':
    # Use the workbench settings file:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workbench.settings')
    # Configure a range of ports in case the default port of 8081 is in use
    os.environ.setdefault('DJANGO_LIVE_TEST_SERVER_ADDRESS', 'localhost:8081-8099')

    try:
        os.mkdir('var')
    except OSError:
        # May already exist.
        pass

    settings.INSTALLED_APPS += ('activetable', )

    for noisy_logger, log_level in six.iteritems(logging_level_overrides):
        logging.getLogger(noisy_logger).setLevel(log_level)

    args_iter = iter(sys.argv[1:])
    options = []
    paths = []
    for arg in args_iter:
        if arg == '--':
            break
        if arg.startswith('-'):
            options.append(arg)
        else:
            paths.append(arg)
    paths.extend(args_iter)
    if not paths:
        paths = ['tests/']
    execute_from_command_line([sys.argv[0], 'test'] + options + ['--'] + paths)
