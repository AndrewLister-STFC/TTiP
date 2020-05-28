.. _conf_parsing:

Config Parsing
==============

Parsing the config file is done using a set of parsers, one for each config
section in the ``parsers`` directory. These are called from 
``core/read_config.py``.

To extend the config options to add more options to a config section, add the
parsing to ``parse`` function in the associated parser, and fetch it in the
``read_config.py`` section.

To add a new section, an additional parser should be created.
